import io
import math
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.database import SessionLocal
from backend.app.models import User, Meter, Reading
from backend.app.auth import create_access_token

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    yield
    db.close()

def test_csv_success_single_and_multiple_rows_and_meters():
    db = SessionLocal()
    u = None
    m1 = None
    m2 = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()

        m1 = Meter(name="Meter 1", location_label="Flat 1", owner_id=u.id)
        m2 = Meter(name="Meter 2", location_label="Flat 2", owner_id=u.id)
        db.add_all([m1, m2])
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Single valid row using 'reading' column
        csv1 = f"meter_id,timestamp,reading\n{m1.id},2026-09-25T10:00:00Z,42.5\n"
        res1 = client.post(
            "/api/readings/upload",
            files={"file": ("readings.csv", io.BytesIO(csv1.encode("utf-8")), "text/csv")},
            headers=headers
        )
        assert res1.status_code == 200
        assert res1.json()["data"]["inserted_readings_count"] == 1
        assert res1.json()["data"]["meters_updated"] == 1

        # 2. Multiple valid rows across multiple authorized meters using 'reading_liters'
        csv2 = (
            f"meter_id,timestamp,reading_liters\n"
            f"{m1.id},2026-09-25T11:00:00Z,45.0\n"
            f"{m2.id},2026-09-25T11:00:00Z,100.2\n"
            f"{m2.id},2026-09-25T12:00:00Z,105.8\n"
        )
        res2 = client.post(
            "/api/readings/upload",
            files={"file": ("readings.csv", io.BytesIO(csv2.encode("utf-8")), "text/csv")},
            headers=headers
        )
        assert res2.status_code == 200
        assert res2.json()["data"]["inserted_readings_count"] == 3
        assert res2.json()["data"]["meters_updated"] == 2

    finally:
        if m1 and m2:
            db.query(Reading).filter(Reading.meter_id.in_([m1.id, m2.id])).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id.in_([m1.id, m2.id])).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_schema_validation():
    db = SessionLocal()
    u = None
    m = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter Schema", location_label="Lab S", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # Non-csv extension
        res_ext = client.post("/api/readings/upload", files={"file": ("data.txt", io.BytesIO(b"data"), "text/plain")}, headers=headers)
        assert res_ext.status_code == 400
        assert "CSV file" in res_ext.json()["error"]["message"]

        # Empty file
        res_empty = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(b""), "text/csv")}, headers=headers)
        assert res_empty.status_code == 400
        assert "empty" in res_empty.json()["error"]["message"].lower()

        # Missing meter_id
        csv_no_meter = f"timestamp,reading\n2026-09-25T10:00:00Z,50.0\n"
        res_no_meter = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_no_meter.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_no_meter.status_code == 400
        assert "meter_id" in res_no_meter.json()["error"]["message"]

        # Missing timestamp
        csv_no_ts = f"meter_id,reading\n{m.id},50.0\n"
        res_no_ts = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_no_ts.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_no_ts.status_code == 400
        assert "timestamp" in res_no_ts.json()["error"]["message"]

        # Missing reading
        csv_no_val = f"meter_id,timestamp\n{m.id},2026-09-25T10:00:00Z\n"
        res_no_val = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_no_val.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_no_val.status_code == 400
        assert "reading" in res_no_val.json()["error"]["message"].lower()

        # Duplicate header columns
        csv_dup_col = f"meter_id,timestamp,reading,reading\n{m.id},2026-09-25T10:00:00Z,50.0,50.0\n"
        res_dup_col = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_dup_col.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_dup_col.status_code == 400
        assert "Duplicate column" in res_dup_col.json()["error"]["message"]

        # Unexpected column in strict schema
        csv_extra = f"meter_id,timestamp,reading,unauthorized_extra_col\n{m.id},2026-09-25T10:00:00Z,50.0,leak\n"
        res_extra = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_extra.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_extra.status_code == 400
        assert "Unexpected column" in res_extra.json()["error"]["message"]

        # Malformed structure (missing row column)
        csv_malformed = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z\n"
        res_mal = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_malformed.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_mal.status_code == 400
        assert "Malformed CSV structure" in res_mal.json()["error"]["message"]

        # Missing field values in data row
        csv_empty_field = f"meter_id,timestamp,reading\n{m.id},,50.0\n"
        res_empty_field = client.post("/api/readings/upload", files={"file": ("data.csv", io.BytesIO(csv_empty_field.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_empty_field.status_code == 400
        assert "timestamp" in res_empty_field.json()["error"]["message"]

    finally:
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_encoding_utf8_and_bom():
    db = SessionLocal()
    u = None
    m = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter BOM", location_label="Lab BOM", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Valid UTF-8 with BOM (\xef\xbb\xbf)
        bom_csv = b"\xef\xbb\xbfmeter_id,timestamp,reading\n" + f"{m.id},2026-09-25T10:00:00Z,75.0\n".encode("utf-8")
        res_bom = client.post("/api/readings/upload", files={"file": ("bom.csv", io.BytesIO(bom_csv), "text/csv")}, headers=headers)
        assert res_bom.status_code == 200
        assert res_bom.json()["data"]["inserted_readings_count"] == 1

        # 2. Invalid UTF-8 bytes
        bad_utf8 = b"\xff\xfe\x00\x00meter_id,timestamp,reading\n"
        res_bad = client.post("/api/readings/upload", files={"file": ("bad.csv", io.BytesIO(bad_utf8), "text/csv")}, headers=headers)
        assert res_bad.status_code == 400
        assert "Unable to decode CSV as UTF-8" in res_bad.json()["error"]["message"]

    finally:
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_timestamp_validation():
    db = SessionLocal()
    u = None
    m = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter TS", location_label="Lab TS", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Valid UTC and offset timestamps
        valid_ts_csv = (
            f"meter_id,timestamp,reading\n"
            f"{m.id},2026-09-25T10:00:00Z,50.0\n"
            f"{m.id},2026-09-25T16:30:00+05:30,55.0\n"
        )
        res_valid = client.post("/api/readings/upload", files={"file": ("ts.csv", io.BytesIO(valid_ts_csv.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_valid.status_code == 200
        assert res_valid.json()["data"]["inserted_readings_count"] == 2

        # 2. Malformed timestamp
        mal_ts_csv = f"meter_id,timestamp,reading\n{m.id},2026-13-45T99:99:99,60.0\n"
        res_mal = client.post("/api/readings/upload", files={"file": ("ts.csv", io.BytesIO(mal_ts_csv.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_mal.status_code == 400
        assert "Invalid timestamp format" in res_mal.json()["error"]["message"]

        # 3. Future timestamp (> 24h ahead)
        future_ts = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        future_ts_csv = f"meter_id,timestamp,reading\n{m.id},{future_ts},60.0\n"
        res_fut = client.post("/api/readings/upload", files={"file": ("ts.csv", io.BytesIO(future_ts_csv.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_fut.status_code == 400
        assert "Future timestamp" in res_fut.json()["error"]["message"]

    finally:
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_reading_numeric_validation():
    db = SessionLocal()
    u = None
    m = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter Num", location_label="Lab Num", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # Non-numeric
        csv_non_num = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z,not-a-number\n"
        res_non_num = client.post("/api/readings/upload", files={"file": ("num.csv", io.BytesIO(csv_non_num.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_non_num.status_code == 400
        assert "Non-numeric reading" in res_non_num.json()["error"]["message"]

        # Negative
        csv_neg = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z,-15.5\n"
        res_neg = client.post("/api/readings/upload", files={"file": ("num.csv", io.BytesIO(csv_neg.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_neg.status_code == 400
        assert "Negative reading" in res_neg.json()["error"]["message"]

        # NaN
        csv_nan = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z,NaN\n"
        res_nan = client.post("/api/readings/upload", files={"file": ("num.csv", io.BytesIO(csv_nan.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_nan.status_code == 400
        assert "NaN or Infinity" in res_nan.json()["error"]["message"]

        # Infinity
        csv_inf = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z,inf\n"
        res_inf = client.post("/api/readings/upload", files={"file": ("num.csv", io.BytesIO(csv_inf.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_inf.status_code == 400
        assert "NaN or Infinity" in res_inf.json()["error"]["message"]

    finally:
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_meter_authorization_and_isolation():
    db = SessionLocal()
    user_a = user_b = mgr_org1 = admin_user = None
    m_a = m_b = None
    try:
        uid = str(uuid.uuid4())[:8]
        user_a = User(email=f"a_{uid}@test.local", role="RESIDENT", organization_id="org-1")
        user_b = User(email=f"b_{uid}@test.local", role="RESIDENT", organization_id="org-2")
        mgr_org1 = User(email=f"mgr_{uid}@test.local", role="SOCIETY_MANAGER", organization_id="org-1")
        admin_user = User(email=f"admin_{uid}@test.local", role="ADMINISTRATOR")
        db.add_all([user_a, user_b, mgr_org1, admin_user])
        db.commit()

        m_a = Meter(name="Meter A", location_label="Zone 1", owner_id=user_a.id, organization_id="org-1")
        m_b = Meter(name="Meter B", location_label="Zone 2", owner_id=user_b.id, organization_id="org-2")
        db.add_all([m_a, m_b])
        db.commit()

        token_a = create_access_token({"sub": user_a.id, "email": user_a.email, "user_metadata": {"role": "RESIDENT"}})
        headers_a = {"Authorization": f"Bearer {token_a}"}

        token_mgr = create_access_token({"sub": mgr_org1.id, "email": mgr_org1.email, "user_metadata": {"role": "SOCIETY_MANAGER"}})
        headers_mgr = {"Authorization": f"Bearer {token_mgr}"}

        token_admin = create_access_token({"sub": admin_user.id, "email": admin_user.email, "user_metadata": {"role": "ADMINISTRATOR"}})
        headers_admin = {"Authorization": f"Bearer {token_admin}"}

        # 1. Unknown meter ID -> 404
        csv_unknown = f"meter_id,timestamp,reading\nnonexistent-meter-uuid,2026-09-25T10:00:00Z,50.0\n"
        res_unk = client.post("/api/readings/upload", files={"file": ("unk.csv", io.BytesIO(csv_unknown.encode("utf-8")), "text/csv")}, headers=headers_a)
        assert res_unk.status_code == 404
        assert "not found" in res_unk.json()["error"]["message"].lower()

        # 2. Resident A attempts to upload to Meter B (unauthorized / cross-tenant) -> 403
        csv_unauth = f"meter_id,timestamp,reading\n{m_b.id},2026-09-25T10:00:00Z,50.0\n"
        res_unauth = client.post("/api/readings/upload", files={"file": ("unauth.csv", io.BytesIO(csv_unauth.encode("utf-8")), "text/csv")}, headers=headers_a)
        assert res_unauth.status_code == 403

        # 3. Mixed authorized and unauthorized meters in one CSV -> 403, and NOTHING inserted for authorized meter
        csv_mixed = (
            f"meter_id,timestamp,reading\n"
            f"{m_a.id},2026-09-25T10:00:00Z,50.0\n"
            f"{m_b.id},2026-09-25T10:00:00Z,60.0\n"
        )
        res_mixed = client.post("/api/readings/upload", files={"file": ("mixed.csv", io.BytesIO(csv_mixed.encode("utf-8")), "text/csv")}, headers=headers_a)
        assert res_mixed.status_code == 403
        # Check DB to verify meter A has 0 readings
        assert db.query(Reading).filter(Reading.meter_id == m_a.id).count() == 0

        # 4. Society Manager of org-1 uploads to Meter A (same org) -> 200
        csv_mgr = f"meter_id,timestamp,reading\n{m_a.id},2026-09-25T10:00:00Z,50.0\n"
        res_mgr = client.post("/api/readings/upload", files={"file": ("mgr.csv", io.BytesIO(csv_mgr.encode("utf-8")), "text/csv")}, headers=headers_mgr)
        assert res_mgr.status_code == 200

        # 5. Society Manager of org-1 attempts upload to Meter B (org-2) -> 403
        csv_mgr_b = f"meter_id,timestamp,reading\n{m_b.id},2026-09-25T10:00:00Z,50.0\n"
        res_mgr_b = client.post("/api/readings/upload", files={"file": ("mgr_b.csv", io.BytesIO(csv_mgr_b.encode("utf-8")), "text/csv")}, headers=headers_mgr)
        assert res_mgr_b.status_code == 403

        # 6. Administrator uploads to Meter B -> 200
        csv_admin = f"meter_id,timestamp,reading\n{m_b.id},2026-09-25T10:00:00Z,50.0\n"
        res_admin = client.post("/api/readings/upload", files={"file": ("admin.csv", io.BytesIO(csv_admin.encode("utf-8")), "text/csv")}, headers=headers_admin)
        assert res_admin.status_code == 200

    finally:
        if m_a and m_b:
            db.query(Reading).filter(Reading.meter_id.in_([m_a.id, m_b.id])).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id.in_([m_a.id, m_b.id])).delete(synchronize_session=False)
        u_ids = [u.id for u in [user_a, user_b, mgr_org1, admin_user] if u is not None]
        if u_ids:
            db.query(User).filter(User.id.in_(u_ids)).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_duplicate_detection_and_atomicity():
    db = SessionLocal()
    u = None
    m = None
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter Dup", location_label="Lab Dup", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Duplicate within the same CSV -> 400
        csv_intra_dup = (
            f"meter_id,timestamp,reading\n"
            f"{m.id},2026-09-25T10:00:00Z,50.0\n"
            f"{m.id},2026-09-25T10:00:00Z,55.0\n"
        )
        res_intra = client.post("/api/readings/upload", files={"file": ("dup.csv", io.BytesIO(csv_intra_dup.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_intra.status_code == 400
        assert "Duplicate reading" in res_intra.json()["error"]["message"]
        # Verify 0 readings committed
        assert db.query(Reading).filter(Reading.meter_id == m.id).count() == 0

        # 2. Commit 1 valid reading
        csv_single = f"meter_id,timestamp,reading\n{m.id},2026-09-25T10:00:00Z,50.0\n"
        res_single = client.post("/api/readings/upload", files={"file": ("single.csv", io.BytesIO(csv_single.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_single.status_code == 200
        assert db.query(Reading).filter(Reading.meter_id == m.id).count() == 1

        # 3. Duplicate against existing database reading (repeated upload) -> 400
        res_rep = client.post("/api/readings/upload", files={"file": ("single.csv", io.BytesIO(csv_single.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_rep.status_code == 400
        assert "already exists in the database" in res_rep.json()["error"]["message"]
        # Count remains 1
        assert db.query(Reading).filter(Reading.meter_id == m.id).count() == 1

        # 4. Mixed valid and invalid rows -> 0 of the new valid rows inserted
        csv_mixed = (
            f"meter_id,timestamp,reading\n"
            f"{m.id},2026-09-25T11:00:00Z,60.0\n"
            f"{m.id},2026-09-25T12:00:00Z,-99.0\n"  # Invalid negative reading
            f"{m.id},2026-09-25T13:00:00Z,70.0\n"
        )
        res_mixed = client.post("/api/readings/upload", files={"file": ("mixed.csv", io.BytesIO(csv_mixed.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_mixed.status_code == 400
        assert "Row 3: Negative reading" in res_mixed.json()["error"]["message"]

        # Neither 11:00 nor 13:00 was inserted! Count remains 1
        assert db.query(Reading).filter(Reading.meter_id == m.id).count() == 1

    finally:
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_csv_limits_and_security():
    db = SessionLocal()
    u = None
    m = None
    orig_max_rows = settings.CSV_MAX_ROWS
    try:
        uid = str(uuid.uuid4())[:8]
        u = User(email=f"user_{uid}@test.local", role="RESIDENT")
        db.add(u)
        db.commit()
        m = Meter(name="Meter Lim", location_label="Lab Lim", owner_id=u.id)
        db.add(m)
        db.commit()

        token = create_access_token({"sub": u.id, "email": u.email, "user_metadata": {"role": "RESIDENT"}})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Unauthenticated request -> 401
        res_unauth = client.post("/api/readings/upload", files={"file": ("lim.csv", io.BytesIO(b"data"), "text/csv")})
        assert res_unauth.status_code == 401

        # 2. Oversized file (> 10MB)
        # Create small header then pad
        large_bytes = b"meter_id,timestamp,reading\n" + b"x" * (10 * 1024 * 1024 + 10)
        res_large = client.post("/api/readings/upload", files={"file": ("large.csv", io.BytesIO(large_bytes), "text/csv")}, headers=headers)
        assert res_large.status_code == 400
        assert "maximum permitted limit" in res_large.json()["error"]["message"]

        # 3. Row count exceeds bounded limit
        settings.CSV_MAX_ROWS = 3
        csv_too_many = (
            f"meter_id,timestamp,reading\n"
            f"{m.id},2026-09-25T10:00:00Z,10.0\n"
            f"{m.id},2026-09-25T11:00:00Z,20.0\n"
            f"{m.id},2026-09-25T12:00:00Z,30.0\n"
            f"{m.id},2026-09-25T13:00:00Z,40.0\n"
        )
        res_rows = client.post("/api/readings/upload", files={"file": ("rows.csv", io.BytesIO(csv_too_many.encode("utf-8")), "text/csv")}, headers=headers)
        assert res_rows.status_code == 400
        assert "Row count (4) exceeds maximum permitted limit (3 rows)" in res_rows.json()["error"]["message"]

        # 4. Error response security: No SQL or stack traces leaked
        err_data = res_rows.json()
        assert "error" in err_data
        assert "message" in err_data["error"]
        msg = err_data["error"]["message"]
        assert "Traceback" not in msg
        assert "SELECT" not in msg
        assert "INSERT" not in msg

    finally:
        settings.CSV_MAX_ROWS = orig_max_rows
        if m:
            db.query(Reading).filter(Reading.meter_id == m.id).delete(synchronize_session=False)
            db.query(Meter).filter(Meter.id == m.id).delete(synchronize_session=False)
        if u:
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
        db.commit()
        db.close()
