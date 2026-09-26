from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Alert, Meter, User
from backend.app.schemas import (
    ApiResponse, AlertResponse, AlertEvidenceResponse, ResolveRequest
)
from backend.app.auth import get_current_user
from backend.app.authorization import verify_alert_access, can_access_meter
from backend.app.alerts import transition_alert_state

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

def build_alert_response(alert: Alert) -> AlertResponse:
    ev_resp = None
    if alert.evidence:
        ev_resp = AlertEvidenceResponse.model_validate(alert.evidence)
    return AlertResponse(
        id=alert.id,
        meter_id=alert.meter_id,
        status=alert.status,
        severity=alert.severity,
        risk_score=alert.risk_score,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        evidence=ev_resp
    )

@router.get("", response_model=ApiResponse[List[AlertResponse]])
def list_alerts(
    meter_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert).join(Meter, Alert.meter_id == Meter.id)

    if meter_id:
        query = query.filter(Alert.meter_id == meter_id)
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if status:
        query = query.filter(Alert.status == status.upper())
    if from_date:
        query = query.filter(Alert.created_at >= from_date)
    if to_date:
        query = query.filter(Alert.created_at <= to_date)

    alerts = query.order_by(Alert.created_at.desc()).all()

    # Filter by user authorization
    authorized_alerts = [
        build_alert_response(a) for a in alerts if can_access_meter(current_user, a.meter)
    ]
    return ApiResponse(data=authorized_alerts)

@router.get("/{id}", response_model=ApiResponse[AlertResponse])
def get_alert_detail(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{id}' not found"
        )
    verify_alert_access(current_user, alert)
    return ApiResponse(data=build_alert_response(alert))

@router.post("/{id}/acknowledge", response_model=ApiResponse[AlertResponse])
def acknowledge_alert(
    id: str,
    note: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{id}' not found"
        )
    verify_alert_access(current_user, alert)

    # Transition DETECTED -> ACKNOWLEDGED
    transitioned_alert = transition_alert_state(
        db=db,
        alert=alert,
        target_state="ACKNOWLEDGED",
        user=current_user,
        note=note or "Alert acknowledged by user"
    )
    return ApiResponse(data=build_alert_response(transitioned_alert))

@router.post("/{id}/resolve", response_model=ApiResponse[AlertResponse])
def resolve_or_transition_alert(
    id: str,
    payload: ResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{id}' not found"
        )
    verify_alert_access(current_user, alert)

    target = payload.resolution.upper()
    # Transition according to state machine
    transitioned_alert = transition_alert_state(
        db=db,
        alert=alert,
        target_state=target,
        user=current_user,
        note=payload.note or f"Action taken: {target}"
    )
    return ApiResponse(data=build_alert_response(transitioned_alert))
