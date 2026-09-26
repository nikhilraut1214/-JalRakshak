from fastapi import APIRouter
from backend.app.schemas import ApiResponse

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health", response_model=ApiResponse[dict])
def get_health():
    return ApiResponse(
        data={
            "status": "healthy",
            "service": "JalRakshak AI Backend",
            "version": "1.0.0"
        }
    )
