import uuid
import io
import jwt
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import Settings, settings
from backend.app.database import Base, engine, SessionLocal
from backend.app.models import User, Meter, Reading, Alert, AlertEvidence
from backend.app.auth import create_access_token, decode_token, get_current_user
from backend.app.authorization import (
    verify_alert_access,
    verify_meter_access,
    AuthorizationError,
    get_authorized_meters_query
)
from backend.app.rate_limiter import explain_rate_limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_tables():
    Base.metadata.create_all(bind=engine)
    yield

# ==============================================================================
# SEC-01: CORS Origin Allowlist and Credential Verification
# ==============================================================================
def test_sec01_cors_allowed_and_disallowed_origins():
    # 1. Allowed localhost:3000
    res_allowed = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert res_allowed.headers.get("access-control-allow-credentials") == "true"

    # 2. Allowed 127.0.0.1:3000
    res_127 = client.get("/api/health", headers={"Origin": "http://127.0.0.1:3000"})
    assert res_127.headers.get("access-control-allow-origin") == "http://127.0.0.1:3000"

    # 3. Disallowed origin: arbitrary external domain must NOT be allowed
    res_disallowed = client.get("/api/health", headers={"Origin": "http://malicious-site.com"})
    assert res_disallowed.headers.get("access-control-allow-origin") is None

    # 4. Preflight request with allowed origin
    res_preflight = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization,Content-Type"
        }
    )
    assert res_preflight.status_code == 200
    assert res_preflight.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert res_preflight.headers.get("access-control-allow-credentials") == "true"

    # 5. Preflight request with disallowed origin
    res_preflight_bad = client.options(
        "/api/health",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert res_preflight_bad.status_code == 400

# ==============================================================================
# SEC-02: Demo Endpoint Cannot Target Existing Real Meter & Does Not Delete Readings
# ==============================================================================
def test_sec02_demo_endpoint_cannot_target_real_meter():
    db = SessionLocal()
    try:
        # Create user with unique email and real meter
        uid = str(uuid.uuid4())[:8]
        user = User(email=f"real-resident-{uid}@test.local", role="RESIDENT")
        db.add(user)
        db.commit()
        db.refresh(user)

        real_meter = Meter(name="Production Meter #101", location_label="Flat 4B", owner_id=user.id)
        db.add(real_meter)
        db.commit()
        db.refresh(real_meter)

        # Seed real historical readings
        r1 = Reading(meter_id=real_meter.id, timestamp=datetime.now(timezone.utc) - timedelta(hours=2), reading_liters=150.0)
        r2 = Reading(meter_id=real_meter.id, timestamp=datetime.now(timezone.utc) - timedelta(hours=1), reading_liters=160.0)
        db.add_all([r1, r2])
        db.commit()

        initial_readings_count = db.query(Reading).filter(Reading.meter_id == real_meter.id).count()
        assert initial_readings_count == 2

        token = create_access_token({"sub": user.id, "email": user.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # Malicious request: attempt to pass meter_id in payload
        res_malicious = client.post(
            "/api/demo/scenario",
            json={
                "scenario": "PERSISTENT_LEAK",
                "seed": 42,
                "meter_id": real_meter.id
            },
            headers=headers
        )
        # MUST BE REJECTED with 422 Unprocessable Entity
        assert res_malicious.status_code == 422
        assert "meter_id" in res_malicious.json()["error"]["message"]

        # CRITICAL VERIFICATION: Confirm real meter readings were NOT deleted
        post_attempt_count = db.query(Reading).filter(Reading.meter_id == real_meter.id).count()
        assert post_attempt_count == 2

        # Valid demo scenario run: backend generates isolated demo meter
        res_valid = client.post(
            "/api/demo/scenario",
            json={"scenario": "PERSISTENT_LEAK", "seed": 42},
            headers=headers
        )
        assert res_valid.status_code == 200
        demo_data = res_valid.json()["data"]
        demo_meter_id = demo_data["meter_id"]
        assert demo_meter_id != real_meter.id

        # Verify real meter readings still completely intact
        assert db.query(Reading).filter(Reading.meter_id == real_meter.id).count() == 2
    finally:
        db.close()

# ==============================================================================
# SEC-03: Production JWT Secret Startup Validation
# ==============================================================================
def test_sec03_production_jwt_secret_validation():
    # 1. Production + default secret -> MUST FAIL
    with pytest.raises(ValueError) as exc1:
        Settings(
            ENVIRONMENT="production",
            SUPABASE_JWT_SECRET="jalrakshak-dev-secret-key-change-in-prod-32chars"
        )
    assert "SUPABASE_JWT_SECRET must be explicitly configured" in str(exc1.value)

    # 2. Production + missing/empty secret -> MUST FAIL
    with pytest.raises(ValueError) as exc2:
        Settings(
            ENVIRONMENT="production",
            SUPABASE_JWT_SECRET=""
        )
    assert "SUPABASE_JWT_SECRET must be explicitly configured" in str(exc2.value)

    # 3. Production + valid custom high-entropy secret -> MUST SUCCEED
    prod_settings = Settings(
        ENVIRONMENT="production",
        SUPABASE_JWT_SECRET="high-entropy-secure-production-secret-999"
    )
    assert prod_settings.ENVIRONMENT == "production"
    assert prod_settings.SUPABASE_JWT_SECRET == "high-entropy-secure-production-secret-999"

    # 4. Production + wildcard origin -> MUST FAIL
    with pytest.raises(ValueError) as exc3:
        Settings(
            ENVIRONMENT="production",
            SUPABASE_JWT_SECRET="high-entropy-secure-production-secret-999",
            ALLOWED_ORIGINS="*"
        )
    assert "Wildcard '*' origin is not permitted" in str(exc3.value)

    # 5. Development + default secret -> ALLOWED
    dev_settings = Settings(
        ENVIRONMENT="development",
        SUPABASE_JWT_SECRET="jalrakshak-dev-secret-key-change-in-prod-32chars"
    )
    assert dev_settings.ENVIRONMENT == "development"

# ==============================================================================
# SEC-04: JWT Audience Verification
# ==============================================================================
def test_sec04_jwt_audience_validation():
    # 1. Valid generated token has aud="authenticated" and decodes successfully
    token_valid = create_access_token({"sub": "user-valid-123"})
    payload = decode_token(token_valid)
    assert payload["sub"] == "user-valid-123"
    assert payload["aud"] == "authenticated"

    # 2. Token with wrong audience -> MUST BE REJECTED
    token_wrong_aud = jwt.encode(
        {"sub": "user-123", "aud": "wrong-audience", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    with pytest.raises(Exception) as exc_aud:
        decode_token(token_wrong_aud)
    assert "audience" in str(exc_aud.value).lower()

    # 3. Token with missing audience -> MUST BE REJECTED
    token_missing_aud = jwt.encode(
        {"sub": "user-123", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    with pytest.raises(Exception) as exc_missing:
        decode_token(token_missing_aud)
    assert "aud" in str(exc_missing.value).lower()

    # 4. Expired token -> MUST BE REJECTED
    token_expired = jwt.encode(
        {"sub": "user-123", "aud": "authenticated", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    with pytest.raises(Exception) as exc_exp:
        decode_token(token_expired)
    assert "expired" in str(exc_exp.value).lower()

# ==============================================================================
# SEC-05: SQL-Level RBAC Filtering & Dashboard Aggregation
# ==============================================================================
def test_sec05_sql_rbac_and_dashboard_aggregation():
    db = SessionLocal()
    try:
        # Create users with unique emails
        uid = str(uuid.uuid4())[:8]
        resident_x = User(email=f"res_x_{uid}@sec05.local", role="RESIDENT", organization_id="org_alpha")
        resident_y = User(email=f"res_y_{uid}@sec05.local", role="RESIDENT", organization_id="org_beta")
        mgr_alpha = User(email=f"mgr_{uid}@sec05.local", role="SOCIETY_MANAGER", organization_id="org_alpha")
        admin = User(email=f"admin_{uid}@sec05.local", role="ADMINISTRATOR")
        db.add_all([resident_x, resident_y, mgr_alpha, admin])
        db.commit()

        # Create meters
        m_x = Meter(name="Meter X", location_label="Block X", owner_id=resident_x.id, organization_id="org_alpha")
        m_y = Meter(name="Meter Y", location_label="Block Y", owner_id=resident_y.id, organization_id="org_beta")
        db.add_all([m_x, m_y])
        db.commit()

        # Query for Resident X: only Meter X
        q_x = get_authorized_meters_query(db, resident_x).all()
        assert len(q_x) == 1
        assert q_x[0].id == m_x.id

        # Query for Manager Alpha: Meter X (same org), but not Meter Y (different org)
        q_mgr = get_authorized_meters_query(db, mgr_alpha).all()
        assert any(m.id == m_x.id for m in q_mgr)
        assert not any(m.id == m_y.id for m in q_mgr)

        # Query for Administrator: all meters
        q_admin = get_authorized_meters_query(db, admin).all()
        assert any(m.id == m_x.id for m in q_admin)
        assert any(m.id == m_y.id for m in q_admin)

        # Dashboard summary for Resident X
        token_x = create_access_token({"sub": resident_x.id, "email": resident_x.email, "user_metadata": {"role": "RESIDENT"}})
        res_dash = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token_x}"})
        assert res_dash.status_code == 200
        dash_data = res_dash.json()["data"]
        assert dash_data["total_meters"] == 1
    finally:
        db.close()

# ==============================================================================
# SEC-06: Groq Explanation Rate Limiting
# ==============================================================================
def test_sec06_groq_rate_limiting():
    db = SessionLocal()
    try:
        uid = str(uuid.uuid4())[:8]
        user = User(email=f"rate-user-{uid}@test.local", role="RESIDENT")
        db.add(user)
        db.commit()
        db.refresh(user)

        meter = Meter(name="Rate Meter", location_label="Lab", owner_id=user.id)
        db.add(meter)
        db.commit()
        db.refresh(meter)

        alert = Alert(meter_id=meter.id, status="DETECTED", severity="HIGH", risk_score=75.0)
        db.add(alert)
        db.commit()
        db.refresh(alert)

        evidence = AlertEvidence(
            alert_id=alert.id,
            current_usage_liters=150.0,
            baseline_liters=100.0,
            deviation_pct=50.0,
            persistence_intervals=2,
            trend="increasing",
            estimated_excess_liters=100.0,
            risk_score=75.0,
            severity="HIGH",
            verification_required=True
        )
        db.add(evidence)
        db.commit()

        token = create_access_token({"sub": user.id, "email": user.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # Reset rate limiter
        explain_rate_limiter.reset()

        # Send 10 rapid explanation requests (all should succeed)
        for i in range(10):
            res = client.post("/api/explain", json={"alert_id": alert.id, "language": "en-IN"}, headers=headers)
            assert res.status_code == 200, f"Request {i+1} failed with status {res.status_code}"

        # 11th request must exceed rate limit and return HTTP 429
        res_limit = client.post("/api/explain", json={"alert_id": alert.id, "language": "en-IN"}, headers=headers)
        assert res_limit.status_code == 429
        assert res_limit.json()["error"]["code"] == "HTTP_429"
        assert "Rate limit exceeded" in res_limit.json()["error"]["message"]
        assert "Retry-After" in res_limit.headers
    finally:
        explain_rate_limiter.reset()
        db.close()

# ==============================================================================
# SEC-07: Fail-Closed Orphaned Alert Authorization
# ==============================================================================
def test_sec07_orphan_alert_fail_closed():
    user = User(id="sec07-user", email="user@sec07.local", role="RESIDENT")
    # Orphaned alert: alert.meter is None
    orphan_alert = Alert(id="orphan-alert-1", meter_id="non-existent-meter", status="DETECTED", severity="HIGH", risk_score=75.0)
    orphan_alert.meter = None

    # Must raise AuthorizationError
    with pytest.raises(AuthorizationError) as exc:
        verify_alert_access(user, orphan_alert)
    assert "no associated meter" in str(exc.value.detail).lower()

# ==============================================================================
# SEC-09: Synchronous CSV Upload Execution
# ==============================================================================
def test_sec09_csv_upload_sync_threadpool():
    db = SessionLocal()
    try:
        uid = str(uuid.uuid4())[:8]
        user = User(email=f"csv-user-{uid}@test.local", role="RESIDENT")
        db.add(user)
        db.commit()
        db.refresh(user)

        meter = Meter(name="CSV Meter", location_label="Lab B", owner_id=user.id)
        db.add(meter)
        db.commit()
        db.refresh(meter)

        token = create_access_token({"sub": user.id, "email": user.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Valid CSV upload
        csv_content = f"meter_id,timestamp,reading_liters\n{meter.id},2026-09-27T10:00:00Z,210.0\n"
        res_ok = client.post(
            "/api/readings/upload",
            files={"file": ("readings.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
            headers=headers
        )
        assert res_ok.status_code == 200
        assert res_ok.json()["data"]["inserted_readings_count"] == 1

        # 2. Non-CSV file rejected
        res_txt = client.post(
            "/api/readings/upload",
            files={"file": ("readings.txt", io.BytesIO(b"data"), "text/plain")},
            headers=headers
        )
        assert res_txt.status_code == 400

        # 3. Missing columns rejected
        bad_csv = f"meter_id,timestamp\n{meter.id},2026-09-27T10:00:00Z\n"
        res_missing = client.post(
            "/api/readings/upload",
            files={"file": ("readings.csv", io.BytesIO(bad_csv.encode("utf-8")), "text/csv")},
            headers=headers
        )
        assert res_missing.status_code == 400
    finally:
        db.close()

# ==============================================================================
# SEC-10: Lightweight Security Headers and Docs Availability
# ==============================================================================
def test_sec10_security_headers_and_docs():
    res_api = client.get("/api/health")
    assert res_api.status_code == 200
    assert res_api.headers.get("x-content-type-options") == "nosniff"
    assert res_api.headers.get("x-frame-options") == "DENY"

    # OpenAPI docs must still load cleanly
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    assert res_docs.headers.get("x-content-type-options") == "nosniff"
    assert res_docs.headers.get("x-frame-options") == "DENY"
