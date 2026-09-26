from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Alert, Explanation, User
from backend.app.schemas import (
    ApiResponse, ExplainRequest, ExplainResponse, EvidenceDetail
)
from backend.app.auth import get_current_user
from backend.app.authorization import verify_alert_access
from backend.app.explanations import generate_explanation
from backend.app.rate_limiter import explain_rate_limiter

router = APIRouter(prefix="/api/explain", tags=["explain"])

@router.post("", response_model=ApiResponse[ExplainResponse])
def explain_alert(
    payload: ExplainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == payload.alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{payload.alert_id}' not found"
        )
    verify_alert_access(current_user, alert)

    if not alert.evidence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert has no attached analytical evidence to explain."
        )

    # Enforce per-user rate limit (10 requests/minute) before calling LLM
    explain_rate_limiter.check_rate_limit(current_user.id)

    ev = alert.evidence
    evidence_detail = EvidenceDetail(
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

    lang = payload.language or "en-IN"
    if lang not in ["en-IN", "mr-IN", "hi-IN"]:
        lang = "en-IN"

    explanation_text, source = generate_explanation(evidence_detail, language=lang)

    # Persist explanation record
    explanation_record = Explanation(
        alert_id=alert.id,
        language=lang,
        explanation=explanation_text,
        source=source
    )
    db.add(explanation_record)
    db.commit()

    return ApiResponse(
        data=ExplainResponse(
            alert_id=alert.id,
            language=lang,
            explanation=explanation_text,
            source=source
        )
    )
