from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, Alert, AlertEvidence, User
from backend.app.schemas import (
    ApiResponse, DashboardSummaryResponse, EvidenceDetail
)
from backend.app.auth import get_current_user
from backend.app.authorization import can_access_meter
from backend.app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    all_meters = db.query(Meter).all()
    auth_meters = [m for m in all_meters if can_access_meter(current_user, m)]
    auth_meter_ids = [m.id for m in auth_meters]

    if not auth_meter_ids:
        return ApiResponse(
            data=DashboardSummaryResponse(
                total_meters=0,
                active_alerts_count=0,
                critical_alerts_count=0,
                high_alerts_count=0,
                recent_consumption_liters=0.0,
                expected_baseline_liters=0.0,
                recent_trend="stable",
                max_risk_score=0.0,
                overall_severity="LOW",
                insufficient_history_meters_count=0,
                next_verification_action="Create or import meters and readings to begin monitoring.",
                evidence_highlights=[]
            )
        )

    # Active alerts
    active_alerts = (
        db.query(Alert)
        .filter(Alert.meter_id.in_(auth_meter_ids))
        .filter(Alert.status.notin_(["RESOLVED", "FALSE_ALARM"]))
        .all()
    )

    critical_count = sum(1 for a in active_alerts if a.severity == "CRITICAL")
    high_count = sum(1 for a in active_alerts if a.severity == "HIGH")
    max_risk = max([a.risk_score for a in active_alerts], default=0.0)

    if max_risk >= 85.0:
        overall_sev = "CRITICAL"
    elif max_risk >= 70.0:
        overall_sev = "HIGH"
    elif max_risk >= 40.0:
        overall_sev = "MEDIUM"
    else:
        overall_sev = "LOW"

    # Count meters with insufficient history
    insufficient_count = 0
    total_recent = 0.0
    total_baseline = 0.0
    evidence_highlights: List[EvidenceDetail] = []

    for m in auth_meters:
        reading_count = db.query(Reading).filter(Reading.meter_id == m.id).count()
        if reading_count < settings.MIN_BASELINE_READINGS:
            insufficient_count += 1

    # Fetch recent alert evidences
    for a in active_alerts[:5]:
        if a.evidence:
            ev = a.evidence
            total_recent += ev.current_usage_liters
            total_baseline += ev.baseline_liters
            evidence_highlights.append(
                EvidenceDetail(
                    current_usage_liters=ev.current_usage_liters,
                    baseline_liters=ev.baseline_liters,
                    deviation_pct=ev.deviation_pct,
                    persistence_intervals=ev.persistence_intervals,
                    trend=ev.trend,
                    estimated_excess_liters=ev.estimated_excess_liters,
                    risk_score=ev.risk_score,
                    severity=ev.severity,
                    verification_required=ev.verification_required
                )
            )

    # Determine recommended next verification action
    if critical_count > 0:
        next_action = "CRITICAL PRIORITY: Inspect physical meter and isolate primary distribution valves for flagged meters immediately."
    elif high_count > 0:
        next_action = "HIGH PRIORITY: Acknowledge detected alerts and initiate on-site fixture verification."
    elif active_alerts:
        next_action = "Review active alerts and conduct zero-consumption test during scheduled off-hours."
    elif insufficient_count > 0:
        next_action = f"Import historical readings for {insufficient_count} meter(s) to establish reliable baselines."
    else:
        next_action = "All authorized meters operating within expected baseline thresholds. Continue normal monitoring."

    recent_trend = "increasing" if (evidence_highlights and any(e.trend == "increasing" for e in evidence_highlights)) else "stable"

    return ApiResponse(
        data=DashboardSummaryResponse(
            total_meters=len(auth_meters),
            active_alerts_count=len(active_alerts),
            critical_alerts_count=critical_count,
            high_alerts_count=high_count,
            recent_consumption_liters=round(total_recent, 1),
            expected_baseline_liters=round(total_baseline, 1),
            recent_trend=recent_trend,
            max_risk_score=round(max_risk, 1),
            overall_severity=overall_sev,
            insufficient_history_meters_count=insufficient_count,
            next_verification_action=next_action,
            evidence_highlights=evidence_highlights
        )
    )
