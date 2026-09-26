import os
import io
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models import User, Meter, Reading, Alert, AlertEvidence
from backend.app.auth import create_access_token
from backend.app.analytics import (
    compute_baseline_and_anomaly,
    compute_forecast_and_savings,
    clamp
)
from backend.app.alerts import transition_alert_state, ALLOWED_TRANSITIONS
from backend.app.explanations import generate_deterministic_fallback, generate_explanation
from backend.app.schemas import EvidenceDetail
from backend.app.scenarios import generate_scenario_readings

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup test DB tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up test records if needed

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["error"] is None
    assert json_data["data"]["status"] == "healthy"

def test_analytics_insufficient_history():
    # Under 5 readings should trigger INSUFFICIENT_HISTORY
    short_readings = [
        {"timestamp": datetime.now(timezone.utc) - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(3)
    ]
    result = compute_baseline_and_anomaly(short_readings)
    assert result["status"] == "INSUFFICIENT_HISTORY"
    assert "Not enough historical readings" in result["message"]
    assert result["readings_count"] == 3
    assert result["required_count"] == 5

def test_analytics_normal_and_spike():
    # 10 readings at 100 L followed by 250 L spike
    readings = [
        {"timestamp": datetime.now(timezone.utc) - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(10, 0, -1)
    ]
    readings.append({"timestamp": datetime.now(timezone.utc), "reading_liters": 250.0})
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["deviation_pct"] == 150.0  # (250-100)/100 * 100
    assert result["deviation_score"] == 100.0  # clamped to 100
    assert result["persistence_intervals"] >= 1
    assert result["risk_score"] > 0
    assert result["severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_forecasting_and_savings():
    readings = [
        {"timestamp": datetime.now(timezone.utc) - timedelta(hours=i), "reading_liters": 100.0 + i * 5}
        for i in range(10)
    ]
    res = compute_forecast_and_savings(readings)
    assert res["status"] == "SUCCESS"
    assert "forecast_next_liters" in res
    assert "historical_mae" in res

def test_alert_lifecycle_valid_and_invalid_transitions():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test-admin@test.local").first()
        if not user:
            user = User(email="test-admin@test.local", role="ADMINISTRATOR")
            db.add(user)
            db.commit()
            db.refresh(user)

        meter = Meter(name="Test Meter", location_label="Test Loc", owner_id=user.id)
        db.add(meter)
        db.commit()

        alert = Alert(meter_id=meter.id, status="DETECTED", severity="HIGH", risk_score=75.0)
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # 1. Valid: DETECTED -> ACKNOWLEDGED
        alert = transition_alert_state(db, alert, "ACKNOWLEDGED", user)
        assert alert.status == "ACKNOWLEDGED"

        # 2. Valid: ACKNOWLEDGED -> VERIFYING
        alert = transition_alert_state(db, alert, "VERIFYING", user)
        assert alert.status == "VERIFYING"

        # 3. Invalid: VERIFYING -> RESOLVED (must go through CONFIRMED, FALSE_ALARM, or INVESTIGATING first)
        with pytest.raises(Exception):
            transition_alert_state(db, alert, "RESOLVED", user)

        # 4. Valid: VERIFYING -> CONFIRMED
        alert = transition_alert_state(db, alert, "CONFIRMED", user)
        assert alert.status == "CONFIRMED"

        # 5. Valid: CONFIRMED -> RESOLVED
        alert = transition_alert_state(db, alert, "RESOLVED", user)
        assert alert.status == "RESOLVED"
    finally:
        db.close()

def test_groq_fallback_multilingual():
    ev = EvidenceDetail(
        current_usage_liters=1860.0,
        baseline_liters=1040.0,
        deviation_pct=78.3,
        persistence_intervals=4,
        trend="increasing",
        estimated_excess_liters=820.0,
        risk_score=91.0,
        severity="CRITICAL",
        verification_required=True
    )
    # English fallback
    text_en, src_en = generate_explanation(ev, language="en-IN")
    assert src_en in ["groq", "deterministic"]
    assert "1860" in text_en
    assert "CRITICAL" in text_en

    # Marathi fallback
    text_mr = generate_deterministic_fallback(ev, language="mr-IN")
    assert "1860" in text_mr
    assert "CRITICAL" in text_mr
    assert "पाणी वापर" in text_mr

    # Hindi fallback
    text_hi = generate_deterministic_fallback(ev, language="hi-IN")
    assert "1860" in text_hi
    assert "CRITICAL" in text_hi
    assert "जल खपत" in text_hi

def test_demo_scenarios_and_api_integration():
    # Test Demo Scenario Generation
    for scen in ["NORMAL_HOME", "SINGLE_SPIKE", "PERSISTENT_LEAK", "BURST_USE", "FARM_IRRIGATION", "DATA_QUALITY"]:
        readings, gt, desc = generate_scenario_readings(scen, seed=123)
        assert len(readings) > 0
        assert gt is not None

    # Call API to seed PERSISTENT_LEAK
    res = client.post("/api/demo/scenario", json={"scenario": "PERSISTENT_LEAK", "seed": 42})
    assert res.status_code == 200
    data = res.json()["data"]
    meter_id = data["meter_id"]
    assert data["ground_truth"] == "SUSPECTED_PERSISTENT_LEAK"

    # Analyze the seeded meter
    res_ana = client.post(f"/api/analyze/{meter_id}")
    assert res_ana.status_code == 200
    ana_data = res_ana.json()["data"]
    assert ana_data["status"] == "SUCCESS"
    assert ana_data["evidence"]["risk_score"] > 50

    # Check alert was created and list alerts
    res_alerts = client.get(f"/api/alerts?meter_id={meter_id}")
    assert res_alerts.status_code == 200
    alerts_list = res_alerts.json()["data"]
    assert len(alerts_list) >= 1
    alert_id = alerts_list[0]["id"]
    assert alerts_list[0]["status"] == "DETECTED"

    # Acknowledge alert
    res_ack = client.post(f"/api/alerts/{alert_id}/acknowledge")
    assert res_ack.status_code == 200
    assert res_ack.json()["data"]["status"] == "ACKNOWLEDGED"

    # Request explanation
    res_exp = client.post("/api/explain", json={"alert_id": alert_id, "language": "en-IN"})
    assert res_exp.status_code == 200
    assert res_exp.json()["data"]["source"] in ["groq", "deterministic"]

    # Dashboard summary
    res_dash = client.get("/api/dashboard/summary")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()["data"]
    assert dash_data["total_meters"] >= 1
    assert dash_data["active_alerts_count"] >= 1

def test_csv_upload():
    # Create meter
    res_m = client.post("/api/meters", json={"name": "CSV Test Meter", "location_label": "Block C"})
    m_id = res_m.json()["data"]["id"]

    csv_data = f"meter_id,timestamp,reading_liters\n{m_id},2026-09-26T10:00:00Z,120.5\n{m_id},2026-09-26T11:00:00Z,130.0\n"
    res_up = client.post(
        "/api/readings/upload",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    )
    assert res_up.status_code == 200
    assert res_up.json()["data"]["inserted_readings_count"] == 2

def test_rbac_and_ownership():
    # Test Resident A cannot access Resident B meter
    token_a = create_access_token({"sub": "user-a", "email": "a@res.local", "user_metadata": {"role": "RESIDENT", "organization_id": "org-1"}})
    token_b = create_access_token({"sub": "user-b", "email": "b@res.local", "user_metadata": {"role": "RESIDENT", "organization_id": "org-2"}})
    token_mgr_org1 = create_access_token({"sub": "mgr-1", "email": "mgr1@soc.local", "user_metadata": {"role": "SOCIETY_MANAGER", "organization_id": "org-1"}})
    token_admin = create_access_token({"sub": "admin-1", "email": "admin@jal.local", "user_metadata": {"role": "ADMINISTRATOR"}})

    # User A creates Meter
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res = client.post("/api/meters", json={"name": "Meter A", "location_label": "Apt 101"}, headers=headers_a)
    assert res.status_code == 201
    meter_a_id = res.json()["data"]["id"]

    # User B (different user, different org) tries to access Meter A readings -> MUST FAIL with 403
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_b = client.get(f"/api/meters/{meter_a_id}/readings", headers=headers_b)
    assert res_b.status_code == 403
    assert "permission" in res_b.json()["error"]["message"].lower()

    # Society Manager of org-1 tries to access Meter A readings -> MUST SUCCEED
    headers_mgr = {"Authorization": f"Bearer {token_mgr_org1}"}
    res_mgr = client.get(f"/api/meters/{meter_a_id}/readings", headers=headers_mgr)
    assert res_mgr.status_code == 200

    # Administrator tries to access Meter A readings -> MUST SUCCEED
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    res_admin = client.get(f"/api/meters/{meter_a_id}/readings", headers=headers_admin)
    assert res_admin.status_code == 200
