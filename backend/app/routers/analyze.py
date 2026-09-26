from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, Alert, AlertEvidence, User
from backend.app.schemas import (
    ApiResponse, AnalyzeResult, EvidenceDetail, InsufficientHistoryDetail,
    AlertResponse, AlertEvidenceResponse
)
from backend.app.auth import get_current_user
from backend.app.authorization import verify_meter_access
from backend.app.analytics import compute_baseline_and_anomaly
from backend.app.evidence import build_evidence_packet

router = APIRouter(prefix="/api/analyze", tags=["analyze"])

@router.post("/{meter_id}", response_model=ApiResponse[AnalyzeResult])
def analyze_meter(
    meter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meter '{meter_id}' not found"
        )
    verify_meter_access(current_user, meter)

    # Fetch readings ordered chronologically
    readings = (
        db.query(Reading)
        .filter(Reading.meter_id == meter_id)
        .order_by(Reading.timestamp.asc())
        .all()
    )

    readings_data = [
        {"timestamp": r.timestamp, "reading_liters": r.reading_liters}
        for r in readings
    ]

    # Perform deterministic analytics
    analytics_output = compute_baseline_and_anomaly(readings_data)

    if analytics_output["status"] == "INSUFFICIENT_HISTORY":
        return ApiResponse(
            data=AnalyzeResult(
                meter_id=meter_id,
                status="INSUFFICIENT_HISTORY",
                message=analytics_output["message"],
                insufficient_history=InsufficientHistoryDetail(
                    status="INSUFFICIENT_HISTORY",
                    message=analytics_output["message"],
                    readings_count=analytics_output["readings_count"],
                    required_count=analytics_output["required_count"]
                )
            )
        )

    evidence_packet = build_evidence_packet(analytics_output)

    # Check alert decision: if risk >= 40 (MEDIUM, HIGH, CRITICAL)
    alert_resp = None
    if evidence_packet.risk_score >= 40.0:
        # Check if active non-resolved alert exists
        active_alert = (
            db.query(Alert)
            .filter(Alert.meter_id == meter_id)
            .filter(Alert.status.notin_(["RESOLVED", "FALSE_ALARM"]))
            .order_by(Alert.created_at.desc())
            .first()
        )

        if not active_alert:
            # Create new Alert in DETECTED state
            active_alert = Alert(
                meter_id=meter_id,
                status="DETECTED",
                severity=evidence_packet.severity,
                risk_score=evidence_packet.risk_score
            )
            db.add(active_alert)
            db.commit()
            db.refresh(active_alert)

            # Create associated AlertEvidence
            alert_ev = AlertEvidence(
                alert_id=active_alert.id,
                current_usage_liters=evidence_packet.current_usage_liters,
                baseline_liters=evidence_packet.baseline_liters,
                deviation_pct=evidence_packet.deviation_pct,
                persistence_intervals=evidence_packet.persistence_intervals,
                trend=evidence_packet.trend,
                estimated_excess_liters=evidence_packet.estimated_excess_liters,
                risk_score=evidence_packet.risk_score,
                severity=evidence_packet.severity,
                verification_required=evidence_packet.verification_required,
                raw_evidence_json=analytics_output
            )
            db.add(alert_ev)
            db.commit()
            db.refresh(active_alert)
        else:
            # Update existing alert severity and risk if changed
            active_alert.severity = evidence_packet.severity
            active_alert.risk_score = evidence_packet.risk_score
            if active_alert.evidence:
                active_alert.evidence.current_usage_liters = evidence_packet.current_usage_liters
                active_alert.evidence.baseline_liters = evidence_packet.baseline_liters
                active_alert.evidence.deviation_pct = evidence_packet.deviation_pct
                active_alert.evidence.persistence_intervals = evidence_packet.persistence_intervals
                active_alert.evidence.trend = evidence_packet.trend
                active_alert.evidence.estimated_excess_liters = evidence_packet.estimated_excess_liters
                active_alert.evidence.risk_score = evidence_packet.risk_score
                active_alert.evidence.severity = evidence_packet.severity
            db.commit()
            db.refresh(active_alert)

        ev_resp = None
        if active_alert.evidence:
            ev_resp = AlertEvidenceResponse.model_validate(active_alert.evidence)

        alert_resp = AlertResponse(
            id=active_alert.id,
            meter_id=active_alert.meter_id,
            status=active_alert.status,
            severity=active_alert.severity,
            risk_score=active_alert.risk_score,
            created_at=active_alert.created_at,
            updated_at=active_alert.updated_at,
            evidence=ev_resp
        )

    return ApiResponse(
        data=AnalyzeResult(
            meter_id=meter_id,
            status="SUCCESS",
            message="Analysis completed successfully.",
            evidence=evidence_packet,
            alert=alert_resp
        )
    )
