import io
import csv
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, User
from backend.app.schemas import ApiResponse, ReadingCreate, ReadingResponse
from backend.app.auth import get_current_user
from backend.app.authorization import verify_meter_access

router = APIRouter(prefix="/api/readings", tags=["readings"])

@router.post("", response_model=ApiResponse[ReadingResponse], status_code=status.HTTP_201_CREATED)
def submit_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meter = db.query(Meter).filter(Meter.id == payload.meter_id).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meter '{payload.meter_id}' not found"
        )
    verify_meter_access(current_user, meter)

    reading = Reading(
        meter_id=payload.meter_id,
        timestamp=payload.timestamp,
        reading_liters=payload.reading_liters,
        raw_or_derived="raw"
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return ApiResponse(data=reading)

@router.post("/upload", response_model=ApiResponse[Dict[str, Any]])
async def upload_readings_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check filename
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file."
        )

    content = await file.read()
    # Reject oversized CSV (e.g. > 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum permitted limit (10MB)."
        )

    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode CSV as UTF-8."
        )

    reader = csv.DictReader(io.StringIO(decoded))
    required_cols = {"meter_id", "timestamp", "reading_liters"}
    if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV must contain columns: {', '.join(sorted(list(required_cols)))}"
        )

    added_count = 0
    meter_cache = {}

    for row_idx, row in enumerate(reader, start=1):
        m_id = row.get("meter_id", "").strip()
        ts_str = row.get("timestamp", "").strip()
        liters_str = row.get("reading_liters", "").strip()

        if not m_id or not ts_str or not liters_str:
            continue

        if m_id not in meter_cache:
            meter = db.query(Meter).filter(Meter.id == m_id).first()
            if not meter:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Row {row_idx}: Meter '{m_id}' not found."
                )
            verify_meter_access(current_user, meter)
            meter_cache[m_id] = meter

        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            liters = float(liters_str)
            if liters < 0:
                raise ValueError("Negative reading")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Invalid timestamp or reading_liters: {e}"
            )

        reading = Reading(
            meter_id=m_id,
            timestamp=ts,
            reading_liters=liters,
            raw_or_derived="raw"
        )
        db.add(reading)
        added_count += 1

    db.commit()
    return ApiResponse(
        data={
            "inserted_readings_count": added_count,
            "meters_updated": len(meter_cache)
        }
    )
