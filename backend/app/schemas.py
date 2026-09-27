from typing import Generic, TypeVar, Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

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
    robust_z: Optional[float] = None
    mad: Optional[float] = None
    deviation_score: Optional[float] = None
    persistence_score: Optional[float] = None
    trend_score: Optional[float] = None
    loss_score: Optional[float] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_from_raw_evidence(cls, data: Any) -> Any:
        if hasattr(data, "raw_evidence_json"):
            raw = getattr(data, "raw_evidence_json", None)
            raw_dict = raw if isinstance(raw, dict) else {}
            res = {
                "id": getattr(data, "id", None),
                "alert_id": getattr(data, "alert_id", None),
                "current_usage_liters": getattr(data, "current_usage_liters", raw_dict.get("current_usage_liters")),
                "baseline_liters": getattr(data, "baseline_liters", raw_dict.get("baseline_liters")),
                "deviation_pct": getattr(data, "deviation_pct", raw_dict.get("deviation_pct")),
                "persistence_intervals": getattr(data, "persistence_intervals", raw_dict.get("persistence_intervals")),
                "trend": getattr(data, "trend", raw_dict.get("trend")),
                "estimated_excess_liters": getattr(data, "estimated_excess_liters", raw_dict.get("estimated_excess_liters")),
                "risk_score": getattr(data, "risk_score", raw_dict.get("risk_score")),
                "severity": getattr(data, "severity", raw_dict.get("severity")),
                "verification_required": getattr(data, "verification_required", raw_dict.get("verification_required", True)),
                "raw_evidence_json": raw,
                "created_at": getattr(data, "created_at", None),
                "robust_z": getattr(data, "robust_z", raw_dict.get("robust_z")),
                "mad": getattr(data, "mad", raw_dict.get("mad")),
                "deviation_score": getattr(data, "deviation_score", raw_dict.get("deviation_score")),
                "persistence_score": getattr(data, "persistence_score", raw_dict.get("persistence_score")),
                "trend_score": getattr(data, "trend_score", raw_dict.get("trend_score")),
                "loss_score": getattr(data, "loss_score", raw_dict.get("loss_score")),
            }
            if res["deviation_score"] is None and res["deviation_pct"] is not None:
                res["deviation_score"] = round(max(0.0, min(100.0, float(res["deviation_pct"]))), 1)
            if res["persistence_score"] is None and res["persistence_intervals"] is not None:
                pi = int(res["persistence_intervals"])
                res["persistence_score"] = 0.0 if pi <= 0 else (25.0 if pi == 1 else (50.0 if pi == 2 else (75.0 if pi == 3 else 100.0)))
            if res["loss_score"] is None and res["estimated_excess_liters"] is not None:
                res["loss_score"] = round(max(0.0, min(100.0, (float(res["estimated_excess_liters"]) / 1000.0) * 100.0)), 1)
            if res["trend_score"] is None and res["trend"] is not None:
                res["trend_score"] = 50.0 if res["trend"] == "increasing" else 0.0
            return res
        elif isinstance(data, dict):
            raw = data.get("raw_evidence_json")
            if isinstance(raw, dict):
                for k in ["robust_z", "mad", "deviation_score", "persistence_score", "trend_score", "loss_score"]:
                    if data.get(k) is None and k in raw:
                        data[k] = raw[k]
            if data.get("deviation_score") is None and data.get("deviation_pct") is not None:
                data["deviation_score"] = round(max(0.0, min(100.0, float(data["deviation_pct"]))), 1)
            if data.get("persistence_score") is None and data.get("persistence_intervals") is not None:
                pi = int(data["persistence_intervals"])
                data["persistence_score"] = 0.0 if pi <= 0 else (25.0 if pi == 1 else (50.0 if pi == 2 else (75.0 if pi == 3 else 100.0)))
            if data.get("loss_score") is None and data.get("estimated_excess_liters") is not None:
                data["loss_score"] = round(max(0.0, min(100.0, (float(data["estimated_excess_liters"]) / 1000.0) * 100.0)), 1)
            if data.get("trend_score") is None and data.get("trend") is not None:
                data["trend_score"] = 50.0 if data.get("trend") == "increasing" else 0.0
        return data

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

    model_config = {"extra": "forbid"}

class DemoScenarioResult(BaseModel):
    scenario: str
    seed: int
    meter_id: str
    readings_count: int
    ground_truth: str
    description: str
    meter_type: Optional[str] = "water"
    operational_schedule: Optional[str] = None
    scenario_category: Optional[str] = "BINARY_CLASSIFICATION"

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

# Evaluation benchmark schemas
class ScenarioEvaluationItem(BaseModel):
    scenario: str
    description: str
    ground_truth: str
    expected_alert: Optional[bool] = None
    actual_alert: bool
    classification: str  # TP, TN, FP, FN, GUARDRAIL_PASS, CONTEXTUAL_PASS
    scenario_category: str = "BINARY_CLASSIFICATION"  # BINARY_CLASSIFICATION, DATA_QUALITY_GUARD, CONTEXTUAL_DOMAIN
    status: str
    risk_score: float
    severity: str
    estimated_excess_liters: float
    persistence_intervals: int
    processing_latency_ms: float
    mae: Optional[float] = None
    passed: bool

class ConfusionMatrix(BaseModel):
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int

class ClassificationMetrics(BaseModel):
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    false_alert_rate: Optional[float] = None
    confusion_matrix: ConfusionMatrix

class NumericalAccuracyMetrics(BaseModel):
    benchmark_mae: Optional[float] = None
    field_telemetry_mae_status: str

class LatencyMetrics(BaseModel):
    avg_processing_latency_ms: float
    min_processing_latency_ms: float
    max_processing_latency_ms: float
    measurement_scope: str

class AiEvaluationMetrics(BaseModel):
    groq_configured: bool
    structured_output_success_rate: Optional[float] = None
    structured_output_status: str
    fallback_coverage_rate: float
    fallback_supported_languages: List[str]
    numerical_authority_preserved: bool

class WorkflowMetrics(BaseModel):
    workflow_tested: bool
    steps_total: int
    steps_completed: int
    completion_rate: float
    lifecycle_states_exercised: List[str]

class EvaluationBenchmarkResult(BaseModel):
    scenarios_tested: int
    classification: ClassificationMetrics
    numerical_accuracy: NumericalAccuracyMetrics
    latency: LatencyMetrics
    ai_metrics: AiEvaluationMetrics
    workflow: WorkflowMetrics
    items: List[ScenarioEvaluationItem]

class EvaluationRunRequest(BaseModel):
    seed: Optional[int] = 42

    model_config = {"extra": "forbid"}

class WaterImpactItem(BaseModel):
    meter_id: str
    meter_code: str
    meter_type: str
    location_label: Optional[str] = None
    alert_id: str
    severity: str
    risk_score: float
    current_usage_liters: float
    baseline_liters: float
    estimated_excess_liters: float
    potential_savings_liters: float
    is_contextual_agricultural: bool
    verification_required: bool

class WaterImpactSummaryResponse(BaseModel):
    total_estimated_excess_liters: float
    potential_savings_liters: float
    avoided_fraction_assumed: float
    active_anomalies_count: int
    contextual_agricultural_meters_count: int
    contextual_agricultural_excess_liters: float
    assumption_note: str
    items: List[WaterImpactItem]

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    role: str
    organization_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 86400
    user: UserProfile
