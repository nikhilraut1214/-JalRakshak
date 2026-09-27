import os
import io
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
import jwt

from backend.app.main import app
from backend.app.config import settings
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
    assert result["persistence_intervals"] == 1
    assert result["estimated_excess_liters"] == 150.0  # max(250 - 100, 0) * 1
    assert result["risk_score"] > 0
    assert result["severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_analytics_estimated_excess_zero_excess():
    # Readings with observed usage equal to expected baseline: excess must be 0
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(6, 0, -1)
    ]
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["current_usage_liters"] == 100.0
    assert result["persistence_intervals"] == 0
    assert result["estimated_excess_liters"] == 0.0
    assert result["loss_score"] == 0.0

def test_analytics_estimated_excess_negative_deviation():
    # Observed usage lower than expected baseline: excess must be clamped to 0
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(6, 1, -1)
    ]
    readings.append({"timestamp": now, "reading_liters": 40.0})
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["current_usage_liters"] == 40.0
    assert result["deviation_pct"] == -60.0
    assert result["persistence_intervals"] == 0
    assert result["estimated_excess_liters"] == 0.0
    assert result["loss_score"] == 0.0

def test_analytics_estimated_excess_zero_persistence():
    # Reading slightly above baseline but below persistence threshold:
    # persistence is 0, so estimated excess must be exactly 0, NOT single_excess * 1
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=5), "reading_liters": 80.0},
        {"timestamp": now - timedelta(hours=4), "reading_liters": 90.0},
        {"timestamp": now - timedelta(hours=3), "reading_liters": 100.0},
        {"timestamp": now - timedelta(hours=2), "reading_liters": 110.0},
        {"timestamp": now - timedelta(hours=1), "reading_liters": 120.0},
        {"timestamp": now, "reading_liters": 105.0},
    ]
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["current_usage_liters"] == 105.0
    assert result["current_usage_liters"] > result["baseline_liters"]
    assert result["persistence_intervals"] == 0
    assert result["estimated_excess_liters"] == 0.0
    assert result["loss_score"] == 0.0

def test_analytics_estimated_excess_one_persistence_interval():
    # 5 baseline readings at 100 L followed by single elevated spike at 150 L:
    # persistence = 1, estimated_excess_liters = (150 - 100) * 1 = 50.0
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(6, 1, -1)
    ]
    readings.append({"timestamp": now, "reading_liters": 150.0})
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["current_usage_liters"] == 150.0
    assert result["persistence_intervals"] == 1
    assert result["estimated_excess_liters"] == 50.0

def test_analytics_estimated_excess_multiple_persistence_intervals():
    # 5 baseline readings at 100 L followed by 3 elevated readings: 140, 150, 160 L
    # persistence = 3, estimated_excess_liters = (160 - 100) * 3 = 180.0
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=i), "reading_liters": 100.0}
        for i in range(8, 3, -1)
    ]
    readings.extend([
        {"timestamp": now - timedelta(hours=2), "reading_liters": 140.0},
        {"timestamp": now - timedelta(hours=1), "reading_liters": 150.0},
        {"timestamp": now, "reading_liters": 160.0},
    ])
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 100.0
    assert result["current_usage_liters"] == 160.0
    assert result["persistence_intervals"] == 3
    assert result["estimated_excess_liters"] == 180.0

def test_analytics_estimated_excess_normal_reading_zero():
    # 8 consistent normal readings: excess must remain 0.0
    now = datetime.now(timezone.utc)
    readings = [
        {"timestamp": now - timedelta(hours=i), "reading_liters": 120.0}
        for i in range(8, 0, -1)
    ]
    result = compute_baseline_and_anomaly(readings)
    assert result["status"] == "SUCCESS"
    assert result["baseline_liters"] == 120.0
    assert result["current_usage_liters"] == 120.0
    assert result["deviation_pct"] == 0.0
    assert result["persistence_intervals"] == 0
    assert result["estimated_excess_liters"] == 0.0
    assert result["risk_score"] == 0.0

def test_analytics_estimated_excess_api_propagation():
    # Verify end-to-end API response propagates estimated_excess_liters correctly
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "excess-test@test.local").first()
        if not user:
            user = User(email="excess-test@test.local", role="ADMINISTRATOR")
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        headers = {"Authorization": f"Bearer {token}"}

        meter = Meter(name="Excess Test Meter", location_label="Test Wing", owner_id=user.id)
        db.add(meter)
        db.commit()
        db.refresh(meter)

        # 5 normal readings + 2 elevated readings
        now = datetime.now(timezone.utc)
        for i in range(7, 2, -1):
            db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=i), reading_liters=100.0))
        db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=2), reading_liters=150.0))
        db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=1), reading_liters=160.0))
        db.commit()

        res = client.post(f"/api/analyze/{meter.id}", headers=headers)
        assert res.status_code == 200
        data = res.json()["data"]
        evidence = data["evidence"]
        assert evidence["persistence_intervals"] == 2
        # (160 - 100) * 2 = 120.0
        assert evidence["estimated_excess_liters"] == 120.0
    finally:
        db.close()

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
    token = create_access_token({"sub": "demo-tester-user", "email": "demo-tester@test.local", "user_metadata": {"role": "ADMINISTRATOR"}})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/demo/scenario", json={"scenario": "PERSISTENT_LEAK", "seed": 42}, headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]
    meter_id = data["meter_id"]
    assert data["ground_truth"] == "SUSPECTED_PERSISTENT_LEAK"

    # Analyze the seeded meter
    res_ana = client.post(f"/api/analyze/{meter_id}", headers=headers)
    assert res_ana.status_code == 200
    ana_data = res_ana.json()["data"]
    assert ana_data["status"] == "SUCCESS"
    assert ana_data["evidence"]["risk_score"] > 50

    # Check alert was created and list alerts
    res_alerts = client.get(f"/api/alerts?meter_id={meter_id}", headers=headers)
    assert res_alerts.status_code == 200
    alerts_list = res_alerts.json()["data"]
    assert len(alerts_list) >= 1
    alert_id = alerts_list[0]["id"]
    assert alerts_list[0]["status"] == "DETECTED"

    # Acknowledge alert
    res_ack = client.post(f"/api/alerts/{alert_id}/acknowledge", headers=headers)
    assert res_ack.status_code == 200
    assert res_ack.json()["data"]["status"] == "ACKNOWLEDGED"

    # Request explanation
    res_exp = client.post("/api/explain", json={"alert_id": alert_id, "language": "en-IN"}, headers=headers)
    assert res_exp.status_code == 200
    assert res_exp.json()["data"]["source"] in ["groq", "deterministic"]

    # Dashboard summary
    res_dash = client.get("/api/dashboard/summary", headers=headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()["data"]
    assert dash_data["total_meters"] >= 1
    assert dash_data["active_alerts_count"] >= 1

def test_csv_upload():
    token = create_access_token({"sub": "csv-tester-user", "email": "csv-tester@test.local", "user_metadata": {"role": "RESIDENT"}})
    headers = {"Authorization": f"Bearer {token}"}

    # Create meter
    res_m = client.post("/api/meters", json={"name": "CSV Test Meter", "location_label": "Block C"}, headers=headers)
    assert res_m.status_code == 201
    m_id = res_m.json()["data"]["id"]

    csv_data = f"meter_id,timestamp,reading_liters\n{m_id},2026-09-26T10:00:00Z,120.5\n{m_id},2026-09-26T11:00:00Z,130.0\n"
    res_up = client.post(
        "/api/readings/upload",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")},
        headers=headers
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

def test_canonical_evidence_breakdown_and_api_serialization():
    # End-to-end verification of deterministic evidence breakdown across analyze, alerts, and dashboard APIs
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "canon-tester@test.local").first()
        if not user:
            user = User(email="canon-tester@test.local", role="ADMINISTRATOR")
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        headers = {"Authorization": f"Bearer {token}"}

        meter = Meter(name="Canonical Evidence Meter", location_label="East Sector", owner_id=user.id)
        db.add(meter)
        db.commit()
        db.refresh(meter)

        now = datetime.now(timezone.utc)
        # 5 normal baseline readings at 100 L
        for i in range(7, 2, -1):
            db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=i), reading_liters=100.0))
        # 2 elevated persistence readings
        db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=2), reading_liters=140.0))
        db.add(Reading(meter_id=meter.id, timestamp=now - timedelta(hours=1), reading_liters=150.0))
        db.commit()

        # 1. Trigger Analysis
        res_analyze = client.post(f"/api/analyze/{meter.id}", headers=headers)
        assert res_analyze.status_code == 200
        an_evidence = res_analyze.json()["data"]["evidence"]

        # Verify all 9 canonical items
        assert an_evidence["current_usage_liters"] == 150.0
        assert an_evidence["baseline_liters"] == 100.0
        assert an_evidence["deviation_pct"] == 50.0
        assert an_evidence["persistence_intervals"] == 2
        assert an_evidence["trend"] == "increasing"
        assert an_evidence["estimated_excess_liters"] == 100.0  # (150 - 100) * 2
        assert an_evidence["severity"] == "MEDIUM"
        assert an_evidence["risk_score"] > 0
        assert an_evidence["verification_required"] is True

        # Verify all 4 deterministic risk component breakdown scores
        assert an_evidence["deviation_score"] == 50.0
        assert an_evidence["persistence_score"] == 50.0
        assert an_evidence["loss_score"] == 10.0
        assert an_evidence["trend_score"] is not None
        assert an_evidence["robust_z"] is not None
        assert an_evidence["mad"] is not None

        # 2. Query Alerts API
        res_alerts = client.get(f"/api/alerts?meter_id={meter.id}", headers=headers)
        assert res_alerts.status_code == 200
        alerts_list = res_alerts.json()["data"]
        assert len(alerts_list) >= 1
        alert_ev = alerts_list[0]["evidence"]

        assert alert_ev["current_usage_liters"] == 150.0
        assert alert_ev["baseline_liters"] == 100.0
        assert alert_ev["deviation_pct"] == 50.0
        assert alert_ev["persistence_intervals"] == 2
        assert alert_ev["trend"] == "increasing"
        assert alert_ev["estimated_excess_liters"] == 100.0
        assert alert_ev["severity"] == "MEDIUM"
        assert alert_ev["verification_required"] is True
        assert alert_ev["deviation_score"] == 50.0
        assert alert_ev["persistence_score"] == 50.0
        assert alert_ev["loss_score"] == 10.0
        assert alert_ev["trend_score"] is not None

        # 3. Query Dashboard Summary API
        res_dash = client.get("/api/dashboard/summary", headers=headers)
        assert res_dash.status_code == 200
        highlights = res_dash.json()["data"]["evidence_highlights"]
        assert len(highlights) > 0
        for h in highlights:
            assert h["deviation_score"] is not None
            assert h["persistence_score"] is not None
            assert h["loss_score"] is not None
            assert h["trend_score"] is not None
    finally:
        db.close()

def test_evaluation_benchmark_endpoints():
    token = create_access_token({"sub": "eval-tester", "email": "eval@jalrakshak.local", "user_metadata": {"role": "ADMINISTRATOR"}})
    headers = {"Authorization": f"Bearer {token}"}

    # Test POST /api/evaluation/run
    res_run = client.post("/api/evaluation/run", json={"seed": 42}, headers=headers)
    assert res_run.status_code == 200
    data = res_run.json()["data"]

    assert data["scenarios_tested"] == 6

    # Classification Metrics (Binary Anomaly Detection suite: NORMAL_HOME, SINGLE_SPIKE, PERSISTENT_LEAK, BURST_USE)
    clf = data["classification"]
    cm = clf["confusion_matrix"]
    assert cm["true_positives"] == 3
    assert cm["true_negatives"] == 1
    assert cm["false_positives"] == 0
    assert cm["false_negatives"] == 0
    assert clf["precision"] == 1.0
    assert clf["recall"] == 1.0
    assert clf["f1"] == 1.0
    assert clf["false_alert_rate"] == 0.0

    # Numerical Accuracy (MAE)
    num = data["numerical_accuracy"]
    assert num["benchmark_mae"] is not None
    assert num["benchmark_mae"] > 0
    assert num["field_telemetry_mae_status"] == "Not yet measured"

    # Latency Metrics
    lat = data["latency"]
    assert lat["avg_processing_latency_ms"] > 0
    assert lat["min_processing_latency_ms"] > 0
    assert lat["max_processing_latency_ms"] >= lat["min_processing_latency_ms"]
    assert "In-process analytics computation" in lat["measurement_scope"]

    # AI Metrics
    ai = data["ai_metrics"]
    assert ai["fallback_coverage_rate"] == 100.0
    assert ai["fallback_supported_languages"] == ["en-IN", "mr-IN", "hi-IN"]
    assert ai["numerical_authority_preserved"] is True
    assert ai["structured_output_status"] is not None

    # Alert Lifecycle Workflow Metrics
    wf = data["workflow"]
    assert wf["workflow_tested"] is True
    assert wf["completion_rate"] == 100.0
    assert wf["steps_completed"] == 4
    assert wf["steps_total"] == 4
    assert wf["lifecycle_states_exercised"] == [
        "DETECTED", "ACKNOWLEDGED", "VERIFYING", "CONFIRMED", "RESOLVED"
    ]

    # Scenario Items (Differentiated Binary vs Guardrail vs Contextual)
    items = data["items"]
    assert len(items) == 6
    item_map = {it["scenario"]: it for it in items}

    # Verify binary scenarios
    assert item_map["NORMAL_HOME"]["classification"] == "TN"
    assert item_map["SINGLE_SPIKE"]["classification"] == "TP"
    assert item_map["PERSISTENT_LEAK"]["classification"] == "TP"
    assert item_map["BURST_USE"]["classification"] == "TP"

    # Verify explicitly audited non-binary scenarios
    assert item_map["DATA_QUALITY"]["classification"] == "GUARDRAIL_PASS"
    assert item_map["DATA_QUALITY"]["scenario_category"] == "DATA_QUALITY_GUARD"
    assert item_map["FARM_IRRIGATION"]["classification"] == "CONTEXTUAL_PASS"
    assert item_map["FARM_IRRIGATION"]["scenario_category"] == "CONTEXTUAL_DOMAIN"

    for item in items:
        assert item["processing_latency_ms"] >= 0
        assert item["passed"] is True

    # Test GET /api/evaluation/benchmark
    res_get = client.get("/api/evaluation/benchmark?seed=42", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["data"]["scenarios_tested"] == 6

def test_synthetic_scenario_calibration_and_context():
    from backend.app.scenarios import CANONICAL_SCENARIO_SPECS

    # 1. SINGLE_SPIKE Calibration
    r_spike, gt_spike, _ = generate_scenario_readings("SINGLE_SPIKE", seed=42)
    res_spike = compute_baseline_and_anomaly(r_spike)
    assert res_spike["status"] == "SUCCESS"
    assert res_spike["persistence_intervals"] == 1
    assert 40.0 <= res_spike["risk_score"] <= 69.0
    assert res_spike["severity"] == "MEDIUM"
    assert res_spike["estimated_excess_liters"] > 0
    assert res_spike["verification_required"] is True

    # 2. PERSISTENT_LEAK Behavior
    r_leak, gt_leak, _ = generate_scenario_readings("PERSISTENT_LEAK", seed=42)
    res_leak = compute_baseline_and_anomaly(r_leak)
    assert res_leak["status"] == "SUCCESS"
    assert res_leak["persistence_intervals"] > 1
    assert res_leak["severity"] in ["HIGH", "CRITICAL"]
    assert res_leak["estimated_excess_liters"] > 0

    # 3. BURST_USE Calibration (baseline -> burst -> recovery)
    r_burst, gt_burst, _ = generate_scenario_readings("BURST_USE", seed=42)
    assert len(r_burst) == 24
    # Baseline phase (0..17)
    for r in r_burst[:18]:
        assert 70.0 <= r["reading_liters"] <= 130.0
    # Burst phase (18..20): 3 intervals of extreme draw
    burst_slice = r_burst[18:21]
    assert len(burst_slice) == 3
    for r in burst_slice:
        assert r["reading_liters"] >= 800.0
    # Anomaly/alert generated during the burst peak
    res_burst = compute_baseline_and_anomaly(r_burst[:21])
    assert res_burst["status"] == "SUCCESS"
    assert res_burst["risk_score"] >= 85.0
    assert res_burst["severity"] == "CRITICAL"
    assert res_burst["persistence_intervals"] == 3
    # Post-burst recovery phase (21..23)
    recovery_slice = r_burst[21:]
    assert len(recovery_slice) == 3
    for r in recovery_slice:
        assert r["reading_liters"] <= 150.0
    # Ensure scenario does not remain continuously elevated like persistent leak
    assert not all(r["reading_liters"] > 500.0 for r in r_burst[18:])

    # 4. NORMAL_HOME Behavior
    r_norm, gt_norm, _ = generate_scenario_readings("NORMAL_HOME", seed=42)
    res_norm = compute_baseline_and_anomaly(r_norm)
    assert res_norm["status"] == "SUCCESS"
    assert res_norm["severity"] == "LOW"
    assert res_norm["risk_score"] < 40.0
    assert res_norm["persistence_intervals"] == 0
    assert res_norm["estimated_excess_liters"] == 0.0
    assert CANONICAL_SCENARIO_SPECS["NORMAL_HOME"]["participates_in_binary_evaluation"] is True
    assert CANONICAL_SCENARIO_SPECS["NORMAL_HOME"]["expected_alert"] is False

    # 5. FARM_IRRIGATION Context Handling
    spec_farm = CANONICAL_SCENARIO_SPECS["FARM_IRRIGATION"]
    assert spec_farm["semantic_category"] == "CONTEXTUAL_DOMAIN"
    assert spec_farm["participates_in_binary_evaluation"] is False
    context = spec_farm["contextual_requirements"]
    assert context["meter_type"] == "agricultural"
    assert context["operational_schedule"] == "04:00-08:00"

    r_farm, _, _ = generate_scenario_readings("FARM_IRRIGATION", seed=42)
    # Pumping window readings (04:00-08:00)
    pumping = [r for r in r_farm if 4 <= r["timestamp"].hour <= 8]
    assert len(pumping) == 5
    assert all(r["reading_liters"] >= 1500.0 for r in pumping)
    # Standby readings outside pumping window
    standby = [r for r in r_farm if not (4 <= r["timestamp"].hour <= 8)]
    assert all(r["reading_liters"] <= 50.0 for r in standby)

    # During pumping, numerical engine authoritatively calculates high draw
    res_pump = compute_baseline_and_anomaly(r_farm[:7])
    assert res_pump["risk_score"] >= 85.0
    assert res_pump["severity"] == "CRITICAL"

    # Test API creates agricultural meter with contextual metadata
    token_farm = create_access_token({"sub": "farm-tester", "email": "farmer@jalrakshak.local", "user_metadata": {"role": "FARM_OPERATOR"}})
    headers_farm = {"Authorization": f"Bearer {token_farm}"}
    res_demo = client.post("/api/demo/scenario", json={"scenario": "FARM_IRRIGATION", "seed": 42}, headers=headers_farm)
    assert res_demo.status_code == 200
    data_demo = res_demo.json()["data"]
    assert data_demo["meter_type"] == "agricultural"
    assert data_demo["operational_schedule"] == "04:00-08:00"
    assert data_demo["scenario_category"] == "CONTEXTUAL_DOMAIN"

    # 6. DATA_QUALITY Safe-Failure Guardrail
    spec_dq = CANONICAL_SCENARIO_SPECS["DATA_QUALITY"]
    assert spec_dq["semantic_category"] == "DATA_QUALITY_GUARD"
    assert spec_dq["participates_in_binary_evaluation"] is False
    r_dq, _, _ = generate_scenario_readings("DATA_QUALITY", seed=42)
    assert len(r_dq) == 3
    res_dq = compute_baseline_and_anomaly(r_dq)
    assert res_dq["status"] == "INSUFFICIENT_HISTORY"

def test_water_impact_calculations_and_api():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "resident-impact@test.local").first()
        if not user:
            user = User(email="resident-impact@test.local", role="RESIDENT")
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test Empty State
        res_empty = client.get("/api/dashboard/water-impact", headers=headers)
        assert res_empty.status_code == 200
        data_empty = res_empty.json()["data"]
        assert "total_estimated_excess_liters" in data_empty
        assert "potential_savings_liters" in data_empty
        assert "avoided_fraction_assumed" in data_empty
        assert "assumption_note" in data_empty
        assert isinstance(data_empty["items"], list)

        # 2. Test Invalid Avoided Fraction Query Param (<0 or >1)
        res_invalid_high = client.get("/api/dashboard/water-impact?avoided_fraction=1.5", headers=headers)
        assert res_invalid_high.status_code == 422
        res_invalid_low = client.get("/api/dashboard/water-impact?avoided_fraction=-0.1", headers=headers)
        assert res_invalid_low.status_code == 422

        # 3. Create Domestic Meter with Active Alert and Positive Excess
        m_dom = Meter(
            name="MTR-IMP-DOM-01",
            location_label="Domestic Zone A",
            meter_type="domestic",
            owner_id=user.id
        )
        db.add(m_dom)
        db.flush()

        alert_dom = Alert(
            meter_id=m_dom.id,
            severity="HIGH",
            risk_score=75.0,
            status="OPEN"
        )
        db.add(alert_dom)
        db.flush()

        ev_dom = AlertEvidence(
            alert_id=alert_dom.id,
            current_usage_liters=500.0,
            baseline_liters=200.0,
            deviation_pct=150.0,
            persistence_intervals=2,
            trend="increasing",
            estimated_excess_liters=600.0,  # (500 - 200) * 2 = 600
            risk_score=75.0,
            severity="HIGH",
            verification_required=True,
            raw_evidence_json={
                "deviation_score": 100.0,
                "persistence_score": 50.0,
                "loss_score": 60.0,
                "trend_score": 50.0,
            }
        )
        db.add(ev_dom)

        # 4. Create Agricultural Meter with Active Alert (Contextual Domain Exemption)
        m_agri = Meter(
            name="MTR-IMP-AGRI-01",
            location_label="Farm Sector 4",
            meter_type="agricultural",
            owner_id=user.id
        )
        db.add(m_agri)
        db.flush()

        alert_agri = Alert(
            meter_id=m_agri.id,
            severity="CRITICAL",
            risk_score=90.0,
            status="OPEN"
        )
        db.add(alert_agri)
        db.flush()

        ev_agri = AlertEvidence(
            alert_id=alert_agri.id,
            current_usage_liters=2500.0,
            baseline_liters=100.0,
            deviation_pct=2400.0,
            persistence_intervals=4,
            trend="stable",
            estimated_excess_liters=9600.0,  # Scheduled irrigation pump draw
            risk_score=90.0,
            severity="CRITICAL",
            verification_required=False,
            raw_evidence_json={"note": "Scheduled irrigation window"}
        )
        db.add(ev_agri)

        # 5. Create Meter with Zero Excess
        m_zero = Meter(
            name="MTR-IMP-ZERO-01",
            location_label="Domestic Zone B",
            meter_type="domestic",
            owner_id=user.id
        )
        db.add(m_zero)
        db.flush()

        alert_zero = Alert(
            meter_id=m_zero.id,
            severity="LOW",
            risk_score=20.0,
            status="OPEN"
        )
        db.add(alert_zero)
        db.flush()

        ev_zero = AlertEvidence(
            alert_id=alert_zero.id,
            current_usage_liters=100.0,
            baseline_liters=100.0,
            deviation_pct=0.0,
            persistence_intervals=0,
            trend="stable",
            estimated_excess_liters=0.0,
            risk_score=20.0,
            severity="LOW",
            verification_required=False
        )
        db.add(ev_zero)

        # 6. Duplicate alert on Domestic Meter (should be deduplicated to latest)
        alert_dom_old = Alert(
            meter_id=m_dom.id,
            severity="MEDIUM",
            risk_score=50.0,
            status="INVESTIGATING",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        db.add(alert_dom_old)
        db.flush()

        ev_dom_old = AlertEvidence(
            alert_id=alert_dom_old.id,
            current_usage_liters=300.0,
            baseline_liters=200.0,
            deviation_pct=50.0,
            persistence_intervals=1,
            trend="increasing",
            estimated_excess_liters=100.0,
            risk_score=50.0,
            severity="MEDIUM",
            verification_required=True
        )
        db.add(ev_dom_old)
        db.commit()

        # 7. Test Default Water Impact (avoided_fraction = 0.70)
        res_default = client.get("/api/dashboard/water-impact", headers=headers)
        assert res_default.status_code == 200
        data_def = res_default.json()["data"]

        # Domestic excess = 600.0 (from m_dom latest alert) + 0.0 (from m_zero) = 600.0
        # Deduplication verified: m_dom old alert (100.0) is not double-counted!
        assert data_def["total_estimated_excess_liters"] == 600.0
        assert data_def["avoided_fraction_assumed"] == 0.70
        # Potential savings = 600.0 * 0.70 = 420.0
        assert data_def["potential_savings_liters"] == 420.0
        # Potential savings <= total excess holds
        assert data_def["potential_savings_liters"] <= data_def["total_estimated_excess_liters"]

        # Agricultural meter must be tracked separately as contextual operational
        assert data_def["contextual_agricultural_meters_count"] == 1
        assert data_def["contextual_agricultural_excess_liters"] == 9600.0

        # Items verification
        items = data_def["items"]
        dom_item = next(i for i in items if i["meter_code"] == "MTR-IMP-DOM-01")
        assert dom_item["estimated_excess_liters"] == 600.0
        assert dom_item["potential_savings_liters"] == 420.0
        assert dom_item["is_contextual_agricultural"] is False

        agri_item = next(i for i in items if i["meter_code"] == "MTR-IMP-AGRI-01")
        assert agri_item["estimated_excess_liters"] == 9600.0
        assert agri_item["potential_savings_liters"] == 0.0  # Exempt from domestic savings
        assert agri_item["is_contextual_agricultural"] is True

        zero_item = next(i for i in items if i["meter_code"] == "MTR-IMP-ZERO-01")
        assert zero_item["estimated_excess_liters"] == 0.0
        assert zero_item["potential_savings_liters"] == 0.0

        # 8. Test Custom Avoided Fraction (avoided_fraction = 0.50)
        res_custom = client.get("/api/dashboard/water-impact?avoided_fraction=0.50", headers=headers)
        assert res_custom.status_code == 200
        data_custom = res_custom.json()["data"]
        assert data_custom["avoided_fraction_assumed"] == 0.50
        # 600.0 * 0.50 = 300.0
        assert data_custom["potential_savings_liters"] == 300.0

        # 9. Test Single Meter Filter
        res_filter = client.get(f"/api/dashboard/water-impact?meter_id={m_dom.id}", headers=headers)
        assert res_filter.status_code == 200
        data_filter = res_filter.json()["data"]
        assert data_filter["total_estimated_excess_liters"] == 600.0
        assert len(data_filter["items"]) == 1
        assert data_filter["items"][0]["meter_code"] == "MTR-IMP-DOM-01"

    finally:
        # Cleanup
        db.query(AlertEvidence).filter(AlertEvidence.alert_id.in_([alert_dom.id, alert_agri.id, alert_zero.id, alert_dom_old.id])).delete(synchronize_session=False)
        db.query(Alert).filter(Alert.id.in_([alert_dom.id, alert_agri.id, alert_zero.id, alert_dom_old.id])).delete(synchronize_session=False)
        db.query(Meter).filter(Meter.id.in_([m_dom.id, m_agri.id, m_zero.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_task07_authentication_rbac_and_session_integration():
    db = SessionLocal()
    user_alpha = user_beta = mgr_alpha = admin_user = None
    meter_alpha = meter_beta = None
    try:
        # 1. Missing token -> 401
        res_missing = client.get("/api/dashboard/summary")
        assert res_missing.status_code == 401
        assert "Authentication required" in res_missing.json()["error"]["message"]

        res_meters_missing = client.get("/api/meters")
        assert res_meters_missing.status_code == 401

        # 2. Invalid token -> 401
        res_invalid = client.get("/api/dashboard/summary", headers={"Authorization": "Bearer invalid.fake.token"})
        assert res_invalid.status_code == 401

        # 3. Expired token -> 401
        token_expired = jwt.encode(
            {"sub": "expired-user", "aud": settings.SUPABASE_JWT_AUDIENCE, "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256"
        )
        res_expired = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token_expired}"})
        assert res_expired.status_code == 401
        assert "expired" in res_expired.json()["error"]["message"].lower()

        # 4. Auth Login Endpoints
        # 4a. Unknown user login -> 401
        res_bad_user = client.post("/api/auth/login", json={"email": "nonexistent@jalrakshak.local", "password": "any"})
        assert res_bad_user.status_code == 401

        # 4b. Bad password -> 401
        res_bad_pass = client.post("/api/auth/login", json={"email": "resident@jalrakshak.local", "password": "wrongpassword999"})
        assert res_bad_pass.status_code == 401

        # 4c. Successful canonical demo login
        res_login = client.post("/api/auth/login", json={"email": "resident@jalrakshak.local", "password": "JalRakshak@2026"})
        assert res_login.status_code == 200
        login_data = res_login.json()["data"]
        assert "access_token" in login_data
        assert login_data["user"]["role"] == "RESIDENT"
        assert login_data["user"]["email"] == "resident@jalrakshak.local"

        token_res = login_data["access_token"]
        headers_res = {"Authorization": f"Bearer {token_res}"}

        # 4d. GET /api/auth/me
        res_me = client.get("/api/auth/me", headers=headers_res)
        assert res_me.status_code == 200
        assert res_me.json()["data"]["email"] == "resident@jalrakshak.local"

        # 4e. POST /api/auth/logout
        res_logout = client.post("/api/auth/logout", headers=headers_res)
        assert res_logout.status_code == 200

        # 4f. GET /api/auth/demo-accounts
        res_demo_accs = client.get("/api/auth/demo-accounts")
        assert res_demo_accs.status_code == 200
        assert len(res_demo_accs.json()["data"]) >= 5

        # 5. Role & Meter Ownership Enforcement
        uid = str(uuid.uuid4())[:8]
        user_alpha = User(email=f"alpha_{uid}@test.local", role="RESIDENT", organization_id="org_alpha")
        user_beta = User(email=f"beta_{uid}@test.local", role="RESIDENT", organization_id="org_beta")
        mgr_alpha = User(email=f"mgr_{uid}@test.local", role="SOCIETY_MANAGER", organization_id="org_alpha")
        admin_user = User(email=f"admin_{uid}@test.local", role="ADMINISTRATOR")
        db.add_all([user_alpha, user_beta, mgr_alpha, admin_user])
        db.commit()

        token_alpha = create_access_token({"sub": user_alpha.id, "email": user_alpha.email, "user_metadata": {"role": "RESIDENT"}})
        headers_alpha = {"Authorization": f"Bearer {token_alpha}"}

        token_beta = create_access_token({"sub": user_beta.id, "email": user_beta.email, "user_metadata": {"role": "RESIDENT"}})
        headers_beta = {"Authorization": f"Bearer {token_beta}"}

        token_mgr = create_access_token({"sub": mgr_alpha.id, "email": mgr_alpha.email, "user_metadata": {"role": "SOCIETY_MANAGER"}})
        headers_mgr = {"Authorization": f"Bearer {token_mgr}"}

        token_admin = create_access_token({"sub": admin_user.id, "email": admin_user.email, "user_metadata": {"role": "ADMINISTRATOR"}})
        headers_admin = {"Authorization": f"Bearer {token_admin}"}

        # Create meters
        meter_alpha = Meter(name="Meter Alpha", location_label="Zone Alpha", owner_id=user_alpha.id, organization_id="org_alpha")
        meter_beta = Meter(name="Meter Beta", location_label="Zone Beta", owner_id=user_beta.id, organization_id="org_beta")
        db.add_all([meter_alpha, meter_beta])
        db.commit()

        # Seed readings for meter_alpha
        r_alpha = Reading(meter_id=meter_alpha.id, timestamp=datetime.now(timezone.utc), reading_liters=100.0)
        db.add(r_alpha)
        db.commit()

        # 6. User cannot access another user's meter
        # User Alpha tries to read Meter Beta -> MUST BE 403 FORBIDDEN
        res_cross = client.get(f"/api/meters/{meter_beta.id}/readings", headers=headers_alpha)
        assert res_cross.status_code == 403

        # 7. User cannot read another organization's meter
        # Manager Alpha (org_alpha) tries to read Meter Beta (org_beta) -> MUST BE 403 FORBIDDEN
        res_mgr_cross = client.get(f"/api/meters/{meter_beta.id}/readings", headers=headers_mgr)
        assert res_mgr_cross.status_code == 403

        # Manager Alpha CAN read Meter Alpha (same org_alpha) -> MUST BE 200
        res_mgr_own = client.get(f"/api/meters/{meter_alpha.id}/readings", headers=headers_mgr)
        assert res_mgr_own.status_code == 200

        # Administrator CAN read any meter -> MUST BE 200
        res_admin_alpha = client.get(f"/api/meters/{meter_alpha.id}/readings", headers=headers_admin)
        assert res_admin_alpha.status_code == 200
        res_admin_beta = client.get(f"/api/meters/{meter_beta.id}/readings", headers=headers_admin)
        assert res_admin_beta.status_code == 200

        # 8. User cannot mutate another user's meter
        # User Alpha tries to submit reading to Meter Beta -> MUST BE 403 FORBIDDEN
        res_mut = client.post(
            "/api/readings",
            json={
                "meter_id": meter_beta.id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reading_liters": 150.0
            },
            headers=headers_alpha
        )
        assert res_mut.status_code == 403

        # 9. Water Impact respects meter authorization
        # User Alpha requests Water Impact for unauthorized Meter Beta -> MUST BE 403 FORBIDDEN
        res_impact_unauth = client.get(f"/api/dashboard/water-impact?meter_id={meter_beta.id}", headers=headers_alpha)
        assert res_impact_unauth.status_code == 403

        # User Alpha requests Water Impact for nonexistent meter -> MUST BE 404
        res_impact_404 = client.get("/api/dashboard/water-impact?meter_id=nonexistent-meter-id", headers=headers_alpha)
        assert res_impact_404.status_code == 404

        # User Alpha requests Water Impact for authorized Meter Alpha -> MUST BE 200
        res_impact_auth = client.get(f"/api/dashboard/water-impact?meter_id={meter_alpha.id}", headers=headers_alpha)
        assert res_impact_auth.status_code == 200

        # 10. Frontend-supplied role cannot elevate privileges
        # User Alpha token claims to be RESIDENT. If client changes UI role, backend strictly validates Bearer token and rejects unauthorized access
        res_spoof = client.get(f"/api/meters/{meter_beta.id}/readings", headers=headers_alpha)
        assert res_spoof.status_code == 403
    finally:
        if meter_alpha and meter_beta:
            db.query(Reading).filter(Reading.meter_id.in_([meter_alpha.id, meter_beta.id])).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id.in_([meter_alpha.id, meter_beta.id])).delete(synchronize_session=False)
        u_ids = [u.id for u in [user_alpha, user_beta, mgr_alpha, admin_user] if u is not None]
        if u_ids:
            db.query(User).filter(User.id.in_(u_ids)).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_task07a_authentication_security_boundary():
    orig_env = settings.ENVIRONMENT
    orig_url = settings.SUPABASE_URL
    orig_anon = settings.SUPABASE_ANON_KEY
    db = SessionLocal()
    test_meter = None
    test_user = None
    try:
        # A. Production + missing external auth configuration -> fails closed with HTTP 503
        settings.ENVIRONMENT = "production"
        settings.SUPABASE_URL = ""
        settings.SUPABASE_ANON_KEY = ""

        res_missing_cfg = client.post("/api/auth/login", json={"email": "resident@jalrakshak.local", "password": "JalRakshak@2026"})
        assert res_missing_cfg.status_code == 503
        assert "External authentication service (Supabase) is not configured" in res_missing_cfg.json()["error"]["message"]

        # B. Production + demo-accounts endpoint -> HTTP 403 Forbidden (disabled in production)
        res_demo_prod = client.get("/api/auth/demo-accounts")
        assert res_demo_prod.status_code == 403
        assert "disabled in production" in res_demo_prod.json()["error"]["message"]

        # C. Production + invalid external auth configuration -> must fail closed / not fall back to local demo
        settings.SUPABASE_URL = "https://invalid-nonexistent-project.supabase.co"
        settings.SUPABASE_ANON_KEY = "dummy-anon-key"
        res_ext_fail = client.post("/api/auth/login", json={"email": "resident@jalrakshak.local", "password": "JalRakshak@2026"})
        # Must be 503 (network/host error) or 401 (if provider rejects), and MUST NOT be 200 (no demo fallback)
        assert res_ext_fail.status_code in [401, 503]
        assert res_ext_fail.status_code != 200

        # D. Development/test + local mode -> may use documented local authentication mechanism
        settings.ENVIRONMENT = "development"
        settings.SUPABASE_URL = ""
        settings.SUPABASE_ANON_KEY = ""
        res_dev_login = client.post("/api/auth/login", json={"email": "resident@jalrakshak.local", "password": "JalRakshak@2026"})
        assert res_dev_login.status_code == 200
        token_dev = res_dev_login.json()["data"]["access_token"]

        # E. Logout behavior matches actual token/session semantics
        res_logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token_dev}"})
        assert res_logout.status_code == 200
        assert "stateless jwt tokens remain cryptographically valid until expiration" in res_logout.json()["data"]["message"].lower()

        # F. Forged role claims cannot elevate privileges
        # 1) Forged token with invalid signature
        forged_admin_token = jwt.encode(
            {"sub": "forged-admin", "aud": settings.SUPABASE_JWT_AUDIENCE, "role": "ADMINISTRATOR", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret-key-attacker-at-least-32-chars-long",
            algorithm="HS256"
        )
        res_forged_sig = client.get("/api/meters", headers={"Authorization": f"Bearer {forged_admin_token}"})
        assert res_forged_sig.status_code == 401

        # 2) Forged token with algorithm 'none'
        forged_none_token = jwt.encode(
            {"sub": "forged-admin", "aud": settings.SUPABASE_JWT_AUDIENCE, "role": "ADMINISTRATOR"},
            "",
            algorithm="none"
        )
        res_forged_none = client.get("/api/meters", headers={"Authorization": f"Bearer {forged_none_token}"})
        assert res_forged_none.status_code == 401

        # 3) Valid resident token attempting cross-tenant access to unowned meter
        uid = str(uuid.uuid4())[:8]
        test_user = User(email=f"foreign_{uid}@test.local", role="RESIDENT", organization_id="other_org")
        db.add(test_user)
        db.commit()
        test_meter = Meter(name="Foreign Meter", location_label="Secret Zone", owner_id=test_user.id, organization_id="other_org")
        db.add(test_meter)
        db.commit()

        # Resident tries to read foreign meter
        res_forbidden = client.get(f"/api/meters/{test_meter.id}/readings", headers={"Authorization": f"Bearer {token_dev}"})
        assert res_forbidden.status_code == 403

    finally:
        settings.ENVIRONMENT = orig_env
        settings.SUPABASE_URL = orig_url
        settings.SUPABASE_ANON_KEY = orig_anon
        if test_meter:
            db.query(Meter).filter(Meter.id == test_meter.id).delete(synchronize_session=False)
        if test_user:
            db.query(User).filter(User.id == test_user.id).delete(synchronize_session=False)
        db.commit()
        db.close()
