from fastapi import HTTPException, status
from backend.app.models import User, Meter, Alert

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def can_access_meter(user: User, meter: Meter) -> bool:
    """
    Checks if a user is authorized to access a given meter.
    Rule:
    1. ADMINISTRATOR has system-level access.
    2. RESIDENT can only access meters they own (meter.owner_id == user.id).
    3. SOCIETY_MANAGER, FARM_OPERATOR, INSTITUTION_ADMIN can access meters they own OR
       meters belonging to the same organization/group (meter.organization_id == user.organization_id).
    """
    if user.role == "ADMINISTRATOR":
        return True

    if meter.owner_id == user.id:
        return True

    if user.role in ["SOCIETY_MANAGER", "FARM_OPERATOR", "INSTITUTION_ADMIN"]:
        if meter.organization_id and meter.organization_id == user.organization_id:
            return True

    return False

def verify_meter_access(user: User, meter: Meter) -> None:
    if not can_access_meter(user, meter):
        raise AuthorizationError("You do not have permission to access this meter.")

def get_authorized_meters_query(db, user: User):
    """
    Returns an optimized SQLAlchemy query for meters accessible by the user,
    enforcing the identical RBAC matrix at the SQL level:
    1. ADMINISTRATOR: All meters in the system.
    2. RESIDENT: Only meters owned by the user (owner_id == user.id).
    3. SOCIETY_MANAGER, FARM_OPERATOR, INSTITUTION_ADMIN:
       Meters owned by user OR belonging to user's organization.
    """
    if user.role == "ADMINISTRATOR":
        return db.query(Meter)
    elif user.role in ["SOCIETY_MANAGER", "FARM_OPERATOR", "INSTITUTION_ADMIN"]:
        if user.organization_id:
            return db.query(Meter).filter(
                (Meter.owner_id == user.id) |
                (Meter.organization_id == user.organization_id)
            )
        else:
            return db.query(Meter).filter(Meter.owner_id == user.id)
    else:
        return db.query(Meter).filter(Meter.owner_id == user.id)

def verify_alert_access(user: User, alert: Alert) -> None:
    """
    Checks if a user is authorized to view or mutate an alert.
    Alert authorization follows the underlying meter's authorization.
    Fails closed if the alert has no associated meter.
    """
    if not alert.meter:
        raise AuthorizationError("Alert has no associated meter and cannot be accessed.")
    verify_meter_access(user, alert.meter)

def verify_role_in(user: User, allowed_roles: list[str]) -> None:
    if user.role not in allowed_roles:
        raise AuthorizationError(f"Action requires one of roles: {', '.join(allowed_roles)}")
