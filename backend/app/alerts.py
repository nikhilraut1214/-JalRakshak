from typing import Dict, Set
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models import Alert, AuditEvent, User

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "DETECTED": {"ACKNOWLEDGED"},
    "ACKNOWLEDGED": {"VERIFYING"},
    "VERIFYING": {"CONFIRMED", "FALSE_ALARM", "INVESTIGATING"},
    "INVESTIGATING": {"RESOLVED"},
    "CONFIRMED": {"RESOLVED"},
    "FALSE_ALARM": {"RESOLVED"},
    "RESOLVED": set()  # Terminal state
}

def transition_alert_state(
    db: Session,
    alert: Alert,
    target_state: str,
    user: User,
    note: str = ""
) -> Alert:
    """
    Validates and executes an alert state transition.
    Enforces the locked transition matrix.
    Logs an audit event for every transition.
    """
    current_state = alert.status

    allowed_targets = ALLOWED_TRANSITIONS.get(current_state, set())
    if target_state not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid alert state transition from '{current_state}' to '{target_state}'. "
                f"Allowed transitions from '{current_state}': {sorted(list(allowed_targets)) or 'None (terminal)'}"
            )
        )

    # Perform transition
    alert.status = target_state

    # Create audit record
    audit = AuditEvent(
        entity_type="alert",
        entity_id=alert.id,
        action="transition",
        from_state=current_state,
        to_state=target_state,
        performed_by=user.id,
        note=note or f"Transitioned from {current_state} to {target_state}"
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert
