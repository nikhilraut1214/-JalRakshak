from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Meter, Reading, User
from backend.app.schemas import (
    ApiResponse, DemoScenarioRequest, DemoScenarioResult
)
from backend.app.auth import get_current_user
from backend.app.authorization import verify_meter_access
from backend.app.scenarios import generate_scenario_readings, CANONICAL_SCENARIO_SPECS

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.post("/scenario", response_model=ApiResponse[DemoScenarioResult])
def run_demo_scenario(
    payload: DemoScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scen_name = payload.scenario.upper()
    seed = payload.seed if payload.seed is not None else 42

    try:
        readings_data, ground_truth, desc = generate_scenario_readings(scen_name, seed=seed)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    spec = CANONICAL_SCENARIO_SPECS.get(scen_name, {})
    context = spec.get("contextual_requirements") or {}
    meter_type = context.get("meter_type", "water")
    operational_schedule = context.get("operational_schedule")

    location_label = "Scenario Lab Sandbox"
    if operational_schedule:
        location_label = f"Farm Irrigation Zone (Schedule: {operational_schedule})"

    # Always create an isolated demo meter for the scenario sandbox with contextual metadata
    meter = Meter(
        name=f"Demo Meter ({scen_name})",
        location_label=location_label,
        meter_type=meter_type,
        owner_id=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(meter)
    db.commit()
    db.refresh(meter)
    meter_id = meter.id

    # Insert seeded readings
    for r in readings_data:
        reading = Reading(
            meter_id=meter_id,
            timestamp=r["timestamp"],
            reading_liters=r["reading_liters"],
            raw_or_derived="raw"
        )
        db.add(reading)

    db.commit()

    return ApiResponse(
        data=DemoScenarioResult(
            scenario=scen_name,
            seed=seed,
            meter_id=meter_id,
            readings_count=len(readings_data),
            ground_truth=ground_truth,
            description=desc,
            meter_type=meter_type,
            operational_schedule=operational_schedule,
            scenario_category=spec.get("semantic_category", "BINARY_CLASSIFICATION")
        )
    )
