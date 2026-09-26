from typing import Generic, TypeVar, Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiError(BaseModel):
    code: str
    message: str

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ApiError] = None

# User schemas
class UserBase(BaseModel):
    email: str
    role: str = "RESIDENT"
    organization_id: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}

# Meter schemas
class MeterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location_label: str = Field(..., min_length=1, max_length=100)
    meter_type: str = Field(default="water")

class MeterResponse(BaseModel):
    id: str
    name: str
    location_label: str
    meter_type: str
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# Reading schemas
class ReadingCreate(BaseModel):
    meter_id: str
    timestamp: datetime
    reading_liters: float = Field(..., ge=0.0)

class ReadingResponse(BaseModel):
    id: str
    meter_id: str
    timestamp: datetime
    reading_liters: float
    raw_or_derived: str
    created_at: datetime

    model_config = {"from_attributes": True}

# Evidence schemas
class EvidenceDetail(BaseModel):
    current_usage_liters: float
    baseline_liters: float
    deviation_pct: float
    persistence_intervals: int
    trend: str
    estimated_excess_liters: float
    risk_score: float
    severity: str
    verification_required: bool = True
    robust_z: Optional[float] = None
    mad: Optional[float] = None
    deviation_score: Optional[float] = None
    persistence_score: Optional[float] = None
    trend_score: Optional[float] = None
    loss_score: Optional[float] = None

class AlertEvidenceResponse(BaseModel):
    id: str
    alert_id: str
    current_usage_liters: float
    baseline_liters: float
    deviation_pct: float
    persistence_intervals: int
    trend: str
    estimated_excess_liters: float
    risk_score: float
    severity: str
    verification_required: bool
    raw_evidence_json: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# Alert schemas
class AlertResponse(BaseModel):
    id: str
    meter_id: str
    status: str
    severity: str
    risk_score: float
    created_at: datetime
    updated_at: datetime
    evidence: Optional[AlertEvidenceResponse] = None

    model_config = {"from_attributes": True}

class ResolveRequest(BaseModel):
    resolution: str  # CONFIRMED, FALSE_ALARM, RESOLVED, or INVESTIGATING
    note: Optional[str] = None

# Explain schemas
class ExplainRequest(BaseModel):
    alert_id: str
    language: str = "en-IN"  # en-IN, mr-IN, hi-IN

class ExplainResponse(BaseModel):
    alert_id: str
    language: str
    explanation: str
    source: str  # 'groq' or 'deterministic'

# Demo scenario schemas
class DemoScenarioRequest(BaseModel):
    scenario: str  # NORMAL_HOME, SINGLE_SPIKE, PERSISTENT_LEAK, BURST_USE, FARM_IRRIGATION, DATA_QUALITY
    seed: Optional[int] = 42
    meter_id: Optional[str] = None

class DemoScenarioResult(BaseModel):
    scenario: str
    seed: int
    meter_id: str
    readings_count: int
    ground_truth: str
    description: str

# Analyze schemas
class InsufficientHistoryDetail(BaseModel):
    status: str = "INSUFFICIENT_HISTORY"
    message: str = "Not enough historical readings to establish a reliable baseline."
    readings_count: int
    required_count: int

class AnalyzeResult(BaseModel):
    meter_id: str
    status: str  # 'SUCCESS' or 'INSUFFICIENT_HISTORY'
    message: Optional[str] = None
    evidence: Optional[EvidenceDetail] = None
    alert: Optional[AlertResponse] = None
    insufficient_history: Optional[InsufficientHistoryDetail] = None

# Dashboard summary schemas
class DashboardSummaryResponse(BaseModel):
    total_meters: int
    active_alerts_count: int
    critical_alerts_count: int
    high_alerts_count: int
    recent_consumption_liters: float
    expected_baseline_liters: float
    recent_trend: str
    max_risk_score: float
    overall_severity: str
    insufficient_history_meters_count: int
    next_verification_action: Optional[str] = None
    evidence_highlights: List[EvidenceDetail] = []
