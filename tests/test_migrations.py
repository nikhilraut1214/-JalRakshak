import os
import tempfile
from contextlib import redirect_stdout
import io
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect

from backend.app.database import Base
import backend.app.models  # ensure models registered


def test_migration_upgrade_and_downgrade_clean_db():
    """Verify that alembic upgrade head runs cleanly from an empty database,

    produces the exact schema expected by Base.metadata without drift,
    and cleanly downgrades back to base.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name

    engine = None
    try:
        db_url = f"sqlite:///{temp_db_path}"
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # 1. Upgrade from empty to head
        command.upgrade(alembic_cfg, "head")

        # 2. Inspect created schema
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected_tables = {
            "alembic_version",
            "audit_events",
            "users",
            "meters",
            "alerts",
            "readings",
            "alert_evidence",
            "explanations",
        }
        assert tables == expected_tables, f"Unexpected tables: {tables ^ expected_tables}"

        # Check columns of each table
        cols_users = {c["name"] for c in inspector.get_columns("users")}
        assert {"id", "email", "role", "organization_id", "created_at"}.issubset(cols_users)

        cols_meters = {c["name"] for c in inspector.get_columns("meters")}
        assert {"id", "name", "location_label", "meter_type", "owner_id", "organization_id", "created_at"}.issubset(cols_meters)

        cols_alerts = {c["name"] for c in inspector.get_columns("alerts")}
        assert {"id", "meter_id", "status", "severity", "risk_score", "created_at", "updated_at"}.issubset(cols_alerts)

        cols_readings = {c["name"] for c in inspector.get_columns("readings")}
        assert {"id", "meter_id", "timestamp", "reading_liters", "raw_or_derived", "created_at"}.issubset(cols_readings)

        cols_evidence = {c["name"] for c in inspector.get_columns("alert_evidence")}
        assert {
            "id",
            "alert_id",
            "current_usage_liters",
            "baseline_liters",
            "deviation_pct",
            "persistence_intervals",
            "trend",
            "estimated_excess_liters",
            "risk_score",
            "severity",
            "verification_required",
            "raw_evidence_json",
            "created_at",
        }.issubset(cols_evidence)

        cols_explanations = {c["name"] for c in inspector.get_columns("explanations")}
        assert {"id", "alert_id", "language", "explanation", "source", "created_at"}.issubset(cols_explanations)

        cols_audit = {c["name"] for c in inspector.get_columns("audit_events")}
        assert {"id", "entity_type", "entity_id", "action", "from_state", "to_state", "performed_by", "note", "timestamp"}.issubset(cols_audit)

        # Check indexes
        reading_idx_names = {idx["name"] for idx in inspector.get_indexes("readings")}
        assert "idx_meter_timestamp" in reading_idx_names

        # Check foreign keys
        meters_fks = inspector.get_foreign_keys("meters")
        assert any(fk["referred_table"] == "users" for fk in meters_fks)

        alerts_fks = inspector.get_foreign_keys("alerts")
        assert any(fk["referred_table"] == "meters" for fk in alerts_fks)

        readings_fks = inspector.get_foreign_keys("readings")
        assert any(fk["referred_table"] == "meters" for fk in readings_fks)

        evidence_fks = inspector.get_foreign_keys("alert_evidence")
        assert any(fk["referred_table"] == "alerts" for fk in evidence_fks)

        explanations_fks = inspector.get_foreign_keys("explanations")
        assert any(fk["referred_table"] == "alerts" for fk in explanations_fks)

        # 3. Verify zero schema drift with alembic check
        command.check(alembic_cfg)

        # 4. Downgrade to base
        engine.dispose()
        command.downgrade(alembic_cfg, "base")

        engine = create_engine(db_url)
        tables_after_downgrade = set(inspect(engine).get_table_names())
        assert tables_after_downgrade == {"alembic_version"}, f"Tables left after downgrade: {tables_after_downgrade}"

        # 5. Re-upgrade to head
        engine.dispose()
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(db_url)
        tables_reupgraded = set(inspect(engine).get_table_names())
        assert tables_reupgraded == expected_tables

    finally:
        if engine:
            engine.dispose()
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except OSError:
                pass


def test_offline_postgresql_migration_ddl():
    """Verify that alembic upgrade head --sql compiles valid PostgreSQL DDL

    for an empty database target.
    """
    buf = io.StringIO()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/jalrakshak",
    )

    with redirect_stdout(buf):
        command.upgrade(alembic_cfg, "head", sql=True)

    sql_output = buf.getvalue()
    assert len(sql_output) > 0, "No SQL generated for PostgreSQL target"

    # Verify tables in PostgreSQL DDL
    assert "CREATE TABLE audit_events" in sql_output
    assert "CREATE TABLE users" in sql_output
    assert "CREATE TABLE meters" in sql_output
    assert "CREATE TABLE alerts" in sql_output
    assert "CREATE TABLE readings" in sql_output
    assert "CREATE TABLE alert_evidence" in sql_output
    assert "CREATE TABLE explanations" in sql_output

    # Verify indexes and constraints in PostgreSQL DDL
    assert "CREATE UNIQUE INDEX ix_users_email ON users" in sql_output
    assert "CREATE INDEX idx_meter_timestamp ON readings" in sql_output
    assert "CREATE UNIQUE INDEX ix_alert_evidence_alert_id ON alert_evidence" in sql_output
    assert "FOREIGN KEY(meter_id) REFERENCES meters (id)" in sql_output
    assert "FOREIGN KEY(alert_id) REFERENCES alerts (id)" in sql_output
    assert "INSERT INTO alembic_version" in sql_output
