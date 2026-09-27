from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import (
    ApiResponse,
    EvaluationBenchmarkResult,
    EvaluationRunRequest,
)
from backend.app.auth import get_current_user
from backend.app.evaluation import run_evaluation_benchmark

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.post("/run", response_model=ApiResponse[EvaluationBenchmarkResult])
def execute_evaluation_benchmark(
    payload: Optional[EvaluationRunRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seed = payload.seed if payload and payload.seed is not None else 42
    results = run_evaluation_benchmark(seed=seed, db=db, current_user=current_user)
    return ApiResponse(data=results)


@router.get("/benchmark", response_model=ApiResponse[EvaluationBenchmarkResult])
def get_evaluation_benchmark(
    seed: int = Query(42, description="Random seed for reproducible scenario generation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = run_evaluation_benchmark(seed=seed, db=db, current_user=current_user)
    return ApiResponse(data=results)
