import io
import csv
import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Set, Tuple
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.app.config import settings
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

    # Check duplicate timestamp for meter
    existing = db.query(Reading).filter(
        Reading.meter_id == payload.meter_id,
        Reading.timestamp == payload.timestamp
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A reading for meter '{payload.meter_id}' at timestamp '{payload.timestamp.isoformat()}' already exists."
        )

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
def upload_readings_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Filename validation
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file."
        )

    # 2. File size bounded check
    content = file.file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty."
        )

    if len(content) > settings.CSV_MAX_FILE_SIZE_BYTES:
        max_mb = settings.CSV_MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum permitted limit ({max_mb}MB)."
        )

    # 3. UTF-8 decoding with BOM support
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode CSV as UTF-8. Only valid UTF-8 encoded files are supported."
        )

    # 4. CSV Structure and Header Validation
    lines = decoded.splitlines()
    if not lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no rows."
        )

    reader = csv.reader(lines)
    try:
        raw_header = next(reader)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no header."
        )

    clean_header = [col.strip() for col in raw_header]
    if not any(clean_header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV header is empty."
        )

    if len(clean_header) != len(set(clean_header)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate column names detected in CSV header."
        )

    if "meter_id" not in clean_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required column 'meter_id'."
        )

    if "timestamp" not in clean_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required column 'timestamp'."
        )

    reading_col = None
    if "reading" in clean_header:
        reading_col = "reading"
    elif "reading_liters" in clean_header:
        reading_col = "reading_liters"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required reading column: CSV must contain 'reading' or 'reading_liters'."
        )

    allowed_cols = {"meter_id", "timestamp", "reading", "reading_liters"}
    unexpected_cols = set(clean_header) - allowed_cols
    if unexpected_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected column(s) in CSV: {', '.join(sorted(unexpected_cols))}."
        )

    meter_idx = clean_header.index("meter_id")
    ts_idx = clean_header.index("timestamp")
    val_idx = clean_header.index(reading_col)

    # 5. Row-Level Pre-Validation (Phase 1)
    validated_rows: List[Tuple[int, str, datetime, float]] = []
    seen_in_file: Set[Tuple[str, datetime]] = set()

    for row_idx, row in enumerate(reader, start=2):
        # Skip purely blank lines
        if not row or not any(field.strip() for field in row):
            continue

        if len(row) <= max(meter_idx, ts_idx, val_idx):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Malformed CSV structure; expected {len(clean_header)} columns but found {len(row)}."
            )

        m_id = row[meter_idx].strip()
        ts_str = row[ts_idx].strip()
        liters_str = row[val_idx].strip()

        if not m_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Missing required field 'meter_id'."
            )
        if not ts_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Missing required field 'timestamp'."
            )
        if not liters_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Missing required field '{reading_col}'."
            )

        # Parse timestamp
        try:
            clean_ts = ts_str.replace("Z", "+00:00")
            parsed_ts = datetime.fromisoformat(clean_ts)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Invalid timestamp format '{ts_str}'. Expected ISO 8601 format."
            )

        if parsed_ts.tzinfo is None:
            parsed_ts = parsed_ts.replace(tzinfo=timezone.utc)
        else:
            parsed_ts = parsed_ts.astimezone(timezone.utc)

        # Future timestamp check (reject timestamps clearly in the future > 24h)
        now_utc = datetime.now(timezone.utc)
        if parsed_ts > now_utc + timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Future timestamp '{ts_str}' is not permitted."
            )

        # Parse numeric reading
        try:
            liters = float(liters_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Non-numeric reading value '{liters_str}'."
            )

        if math.isnan(liters) or math.isinf(liters):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Invalid reading value '{liters_str}' (NaN or Infinity not permitted)."
            )

        if liters < 0.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Negative reading '{liters_str}' is not permitted."
            )

        # Intra-file duplicate check
        file_key = (m_id, parsed_ts)
        if file_key in seen_in_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Duplicate reading for meter '{m_id}' at timestamp '{ts_str}' within the uploaded file."
            )
        seen_in_file.add(file_key)

        validated_rows.append((row_idx, m_id, parsed_ts, liters))

    if not validated_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no data rows."
        )

    if len(validated_rows) > settings.CSV_MAX_ROWS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Row count ({len(validated_rows)}) exceeds maximum permitted limit ({settings.CSV_MAX_ROWS} rows)."
        )

    # 6. Meter Authorization & Existence (Batch Query — No N+1)
    unique_meter_ids = list({m_id for _, m_id, _, _ in validated_rows})
    meters_in_db = db.query(Meter).filter(Meter.id.in_(unique_meter_ids)).all()
    meter_map = {m.id: m for m in meters_in_db}

    for m_id in unique_meter_ids:
        if m_id not in meter_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meter '{m_id}' not found."
            )
        verify_meter_access(current_user, meter_map[m_id])

    # 7. Database Duplicate Pre-Check (Batch Query)
    existing_readings = (
        db.query(Reading.meter_id, Reading.timestamp)
        .filter(Reading.meter_id.in_(unique_meter_ids))
        .all()
    )
    existing_set: Set[Tuple[str, datetime]] = set()
    for em_id, ets in existing_readings:
        if ets.tzinfo is None:
            existing_set.add((em_id, ets.replace(tzinfo=timezone.utc)))
        else:
            existing_set.add((em_id, ets.astimezone(timezone.utc)))

    for row_idx, m_id, parsed_ts, _ in validated_rows:
        if (m_id, parsed_ts) in existing_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_idx}: Duplicate reading: A reading for meter '{m_id}' at timestamp '{parsed_ts.isoformat()}' already exists in the database."
            )

    # 8. Atomic Insertion (Phase 2)
    readings_to_add = [
        Reading(
            meter_id=m_id,
            timestamp=parsed_ts,
            reading_liters=liters,
            raw_or_derived="raw"
        )
        for _, m_id, parsed_ts, liters in validated_rows
    ]

    try:
        db.add_all(readings_to_add)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction error during readings ingestion."
        )

    return ApiResponse(
        data={
            "inserted_readings_count": len(readings_to_add),
            "meters_updated": len(unique_meter_ids)
        }
    )
