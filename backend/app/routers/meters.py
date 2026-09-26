from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, User
from backend.app.schemas import (
    ApiResponse, MeterCreate, MeterResponse, ReadingResponse
)
from backend.app.auth import get_current_user
from backend.app.authorization import verify_meter_access, get_authorized_meters_query

router = APIRouter(prefix="/api/meters", tags=["meters"])

@router.get("", response_model=ApiResponse[List[MeterResponse]])
def list_meters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # SQL-level RBAC filtering avoids loading all tenants' meters into memory
    authorized_meters = get_authorized_meters_query(db, current_user).all()
    return ApiResponse(data=authorized_meters)

@router.post("", response_model=ApiResponse[MeterResponse], status_code=status.HTTP_201_CREATED)
def create_meter(
    payload: MeterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rule: owner_id is set server-side from authenticated user; never trust client
    meter = Meter(
        name=payload.name,
        location_label=payload.location_label,
        meter_type=payload.meter_type,
        owner_id=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(meter)
    db.commit()
    db.refresh(meter)
    return ApiResponse(data=meter)

@router.get("/{id}/readings", response_model=ApiResponse[List[ReadingResponse]])
def get_meter_readings(
    id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meter = db.query(Meter).filter(Meter.id == id).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meter '{id}' not found"
        )
    verify_meter_access(current_user, meter)

    readings = (
        db.query(Reading)
        .filter(Reading.meter_id == id)
        .order_by(Reading.timestamp.asc())
        .limit(limit)
        .all()
    )
    return ApiResponse(data=readings)
