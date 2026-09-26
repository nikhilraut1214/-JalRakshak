import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Text, JSON, Integer, Boolean, Index
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, default="RESIDENT")  # RESIDENT, SOCIETY_MANAGER, FARM_OPERATOR, INSTITUTION_ADMIN, ADMINISTRATOR
    organization_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    meters = relationship("Meter", back_populates="owner")

class Meter(Base):
    __tablename__ = "meters"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    location_label = Column(String, nullable=False)
    meter_type = Column(String, nullable=False, default="water")
    owner_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    owner = relationship("User", back_populates="meters")
    readings = relationship("Reading", back_populates="meter", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="meter", cascade="all, delete-orphan")

class Reading(Base):
    __tablename__ = "readings"

    id = Column(String, primary_key=True, default=generate_uuid)
    meter_id = Column(String, ForeignKey("meters.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    reading_liters = Column(Float, nullable=False)
    raw_or_derived = Column(String, nullable=False, default="raw")  # 'raw' or 'derived'
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    meter = relationship("Meter", back_populates="readings")

    __table_args__ = (
        Index("idx_meter_timestamp", "meter_id", "timestamp"),
    )

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    meter_id = Column(String, ForeignKey("meters.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="DETECTED")
    # States: DETECTED, ACKNOWLEDGED, VERIFYING, INVESTIGATING, CONFIRMED, FALSE_ALARM, RESOLVED
    severity = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float, nullable=False)  # 0-100
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    meter = relationship("Meter", back_populates="alerts")
    evidence = relationship("AlertEvidence", back_populates="alert", uselist=False, cascade="all, delete-orphan")
    explanations = relationship("Explanation", back_populates="alert", cascade="all, delete-orphan")

class AlertEvidence(Base):
    __tablename__ = "alert_evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False, unique=True, index=True)
    current_usage_liters = Column(Float, nullable=False)
    baseline_liters = Column(Float, nullable=False)
    deviation_pct = Column(Float, nullable=False)
    persistence_intervals = Column(Integer, nullable=False)
    trend = Column(String, nullable=False)  # 'increasing', 'stable', 'decreasing'
    estimated_excess_liters = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    verification_required = Column(Boolean, nullable=False, default=True)
    raw_evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    alert = relationship("Alert", back_populates="evidence")

class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False, index=True)
    language = Column(String, nullable=False, default="en-IN")
    explanation = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # 'groq' or 'deterministic'
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    alert = relationship("Alert", back_populates="explanations")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    entity_type = Column(String, nullable=False)  # e.g., 'alert'
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # e.g., 'transition', 'acknowledge', 'resolve'
    from_state = Column(String, nullable=True)
    to_state = Column(String, nullable=True)
    performed_by = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=get_utc_now, nullable=False)
