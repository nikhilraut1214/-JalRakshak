from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, Alert, AlertEvidence, User
from backend.app.schemas import (
    ApiResponse, DashboardSummaryResponse, EvidenceDetail,
    WaterImpactItem, WaterImpactSummaryResponse
)
from backend.app.auth import get_current_user
from backend.app.authorization import get_authorized_meters_query
from backend.app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_meters = get_authorized_meters_query(db, current_user).all()
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

    # Count meters with insufficient history via single aggregated query (eliminates N+1 loop)
    insufficient_count = 0
    total_recent = 0.0
    total_baseline = 0.0
    evidence_highlights: List[EvidenceDetail] = []

    reading_counts = (
        db.query(Reading.meter_id, func.count(Reading.id))
        .filter(Reading.meter_id.in_(auth_meter_ids))
        .group_by(Reading.meter_id)
        .all()
    )
    counts_map = {m_id: count for m_id, count in reading_counts}
    for m in auth_meters:
        if counts_map.get(m.id, 0) < settings.MIN_BASELINE_READINGS:
            insufficient_count += 1

    # Fetch recent alert evidences
    for a in active_alerts[:5]:
        if a.evidence:
            ev = a.evidence
            total_recent += ev.current_usage_liters
            total_baseline += ev.baseline_liters
            raw = ev.raw_evidence_json if isinstance(ev.raw_evidence_json, dict) else {}
            dev_score = raw.get("deviation_score")
            if dev_score is None and ev.deviation_pct is not None:
                dev_score = round(max(0.0, min(100.0, float(ev.deviation_pct))), 1)
            pers_score = raw.get("persistence_score")
            if pers_score is None and ev.persistence_intervals is not None:
                pi = int(ev.persistence_intervals)
                pers_score = 0.0 if pi <= 0 else (25.0 if pi == 1 else (50.0 if pi == 2 else (75.0 if pi == 3 else 100.0)))
            loss_score = raw.get("loss_score")
            if loss_score is None and ev.estimated_excess_liters is not None:
                loss_score = round(max(0.0, min(100.0, (float(ev.estimated_excess_liters) / settings.LOSS_REFERENCE_LITERS) * 100.0)), 1)
            trend_score = raw.get("trend_score")
            if trend_score is None and ev.trend is not None:
                trend_score = 50.0 if ev.trend == "increasing" else 0.0

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
                    verification_required=ev.verification_required,
                    robust_z=raw.get("robust_z"),
                    mad=raw.get("mad"),
                    deviation_score=dev_score,
                    persistence_score=pers_score,
                    trend_score=trend_score,
                    loss_score=loss_score,
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

@router.get("/water-impact", response_model=ApiResponse[WaterImpactSummaryResponse])
def get_water_impact(
    avoided_fraction: float = Query(0.70, ge=0.0, le=1.0),
    meter_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    avoided_fraction = max(0.0, min(1.0, float(avoided_fraction)))
    if meter_id is not None:
        target_meter = db.query(Meter).filter(Meter.id == meter_id).first()
        if not target_meter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meter '{meter_id}' not found"
            )
        from backend.app.authorization import verify_meter_access
        verify_meter_access(current_user, target_meter)
        auth_meters = [target_meter]
    else:
        auth_meters = get_authorized_meters_query(db, current_user).all()

    auth_meter_ids = [m.id for m in auth_meters]
    meter_map = {m.id: m for m in auth_meters}

    empty_response = WaterImpactSummaryResponse(
        total_estimated_excess_liters=0.0,
        potential_savings_liters=0.0,
        avoided_fraction_assumed=round(avoided_fraction, 2),
        active_anomalies_count=0,
        contextual_agricultural_meters_count=0,
        contextual_agricultural_excess_liters=0.0,
        assumption_note=(
            "Potential savings are analytical projections based on an assumed avoidable fraction "
            "(e.g., prompt human shutoff avoiding a percentage of subsequent excess). "
            "They are never presented as guaranteed physical measurements. "
            "Scheduled agricultural irrigation is operational consumption and excluded from domestic waste savings."
        ),
        items=[],
    )

    if not auth_meter_ids:
        return ApiResponse(data=empty_response)

    # Active alerts (excluding resolved / false alarm)
    active_alerts = (
        db.query(Alert)
        .filter(Alert.meter_id.in_(auth_meter_ids))
        .filter(Alert.status.notin_(["RESOLVED", "FALSE_ALARM"]))
        .order_by(Alert.created_at.desc())
        .all()
    )

    # Deduplicate by meter (taking latest active alert per meter to prevent duplicate aggregation)
    latest_alerts_by_meter = {}
    for a in active_alerts:
        if a.meter_id not in latest_alerts_by_meter:
            latest_alerts_by_meter[a.meter_id] = a

    total_domestic_excess = 0.0
    total_savings = 0.0
    contextual_agri_count = 0
    contextual_agri_excess = 0.0
    items: List[WaterImpactItem] = []

    for a in latest_alerts_by_meter.values():
        m = meter_map.get(a.meter_id)
        if not m:
            continue
        m_type = (m.meter_type or "").lower()
        is_agri = (m_type == "agricultural")

        ev = a.evidence
        if ev is None:
            continue

        curr_usage = float(ev.current_usage_liters or 0.0)
        baseline = float(ev.baseline_liters or 0.0)
        excess = max(0.0, float(ev.estimated_excess_liters or 0.0))

        if is_agri:
            contextual_agri_count += 1
            contextual_agri_excess += excess
            item_savings = 0.0
        else:
            total_domestic_excess += excess
            item_savings = round(excess * avoided_fraction, 1)
            total_savings += item_savings

        m_code = getattr(m, "meter_code", None) or m.name
        items.append(
            WaterImpactItem(
                meter_id=str(m.id),
                meter_code=m_code,
                meter_type=m.meter_type or "domestic",
                location_label=m.location_label,
                alert_id=str(a.id),
                severity=a.severity,
                risk_score=round(a.risk_score, 1),
                current_usage_liters=round(curr_usage, 1),
                baseline_liters=round(baseline, 1),
                estimated_excess_liters=round(excess, 1),
                potential_savings_liters=round(item_savings, 1),
                is_contextual_agricultural=is_agri,
                verification_required=ev.verification_required if ev else True,
            )
        )

    # Potential savings cannot exceed domestic excess
    total_savings = min(total_savings, total_domestic_excess)

    return ApiResponse(
        data=WaterImpactSummaryResponse(
            total_estimated_excess_liters=round(total_domestic_excess, 1),
            potential_savings_liters=round(total_savings, 1),
            avoided_fraction_assumed=round(avoided_fraction, 2),
            active_anomalies_count=len([i for i in items if not i.is_contextual_agricultural]),
            contextual_agricultural_meters_count=contextual_agri_count,
            contextual_agricultural_excess_liters=round(contextual_agri_excess, 1),
            assumption_note=(
                "Potential savings are analytical projections based on an assumed avoidable fraction "
                "(e.g., prompt human shutoff avoiding a percentage of subsequent excess). "
                "They are never presented as guaranteed physical measurements. "
                "Scheduled agricultural irrigation is operational consumption and excluded from domestic waste savings."
            ),
            items=items,
        )
    )
