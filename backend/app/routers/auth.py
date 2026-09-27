from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import (
    ApiResponse, LoginRequest, LoginResponse, UserProfile
)
from backend.app.auth import create_access_token, decode_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

CANONICAL_DEMO_USERS = {
    "admin@jalrakshak.local": {"role": "ADMINISTRATOR", "organization_id": None},
    "manager@jalrakshak.local": {"role": "SOCIETY_MANAGER", "organization_id": "org-community"},
    "farmer@jalrakshak.local": {"role": "FARM_OPERATOR", "organization_id": "org-farm"},
    "institution@jalrakshak.local": {"role": "INSTITUTION_ADMIN", "organization_id": "org-campus"},
    "resident@jalrakshak.local": {"role": "RESIDENT", "organization_id": "org-community"},
}

@router.post("/login", response_model=ApiResponse[LoginResponse])
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()
    is_production = settings.ENVIRONMENT.lower() == "production"

    # In production, external provider configuration is mandatory
    if is_production and (not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production authentication error: External authentication service (Supabase) is not configured."
        )

    # 1. If Supabase is configured with an active URL and anon key, attempt Supabase Auth
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        try:
            import httpx
            sb_resp = httpx.post(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "email": email,
                    "password": payload.password or ""
                },
                timeout=5.0
            )
            if sb_resp.status_code == 200:
                sb_data = sb_resp.json()
                access_token = sb_data.get("access_token")
                # Decode Supabase token and get or sync user
                decoded = decode_token(access_token)
                sub_id = decoded.get("sub")
                user = db.query(User).filter(User.id == sub_id).first()
                if not user:
                    user = db.query(User).filter(User.email == email).first()
                if not user:
                    role = decoded.get("user_metadata", {}).get("role") or "RESIDENT"
                    org_id = decoded.get("user_metadata", {}).get("organization_id")
                    user = User(id=sub_id, email=email, role=role, organization_id=org_id)
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                return ApiResponse(
                    data=LoginResponse(
                        access_token=access_token,
                        token_type="Bearer",
                        expires_in=sb_data.get("expires_in", 86400),
                        user=UserProfile.model_validate(user)
                    )
                )
            else:
                if is_production:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials: Authentication failed with external provider.",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
        except HTTPException:
            raise
        except Exception as e:
            if is_production:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"External authentication service unavailable: {str(e)}"
                )

    # In production, local demo authentication MUST NEVER be executed
    if is_production:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Local and demo credential authentication is strictly disabled in production.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 2. Local database / demo account credential verification (Development/Test only)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        if email in CANONICAL_DEMO_USERS:
            spec = CANONICAL_DEMO_USERS[email]
            user = User(
                email=email,
                role=spec["role"],
                organization_id=spec["organization_id"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials: User does not exist.",
                headers={"WWW-Authenticate": "Bearer"}
            )

    # Validate password if provided
    # Accept standard password or common test credentials in development
    if payload.password and payload.password not in ["JalRakshak@2026", "Admin123!", "password", "password123"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: Password incorrect.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Issue authoritative signed JWT token
    token_claims = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "user_metadata": {
            "role": user.role,
            "organization_id": user.organization_id
        },
        "app_metadata": {
            "role": user.role
        }
    }
    token = create_access_token(token_claims)

    return ApiResponse(
        data=LoginResponse(
            access_token=token,
            token_type="Bearer",
            expires_in=86400,
            user=UserProfile.model_validate(user)
        )
    )

@router.get("/me", response_model=ApiResponse[UserProfile])
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return ApiResponse(data=UserProfile.model_validate(current_user))

@router.post("/logout", response_model=ApiResponse[Dict[str, str]])
def logout(
    current_user: User = Depends(get_current_user)
):
    return ApiResponse(
        data={
            "message": "Session terminated on client. Note that stateless JWT tokens remain cryptographically valid until expiration."
        }
    )

@router.get("/demo-accounts", response_model=ApiResponse[List[Dict[str, Any]]])
def list_demo_accounts():
    if settings.ENVIRONMENT.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo accounts endpoint is disabled in production environment."
        )
    accounts = [
        {"email": "resident@jalrakshak.local", "role": "RESIDENT", "label": "Resident (Flat 4B)"},
        {"email": "manager@jalrakshak.local", "role": "SOCIETY_MANAGER", "label": "Society Manager (Community)"},
        {"email": "farmer@jalrakshak.local", "role": "FARM_OPERATOR", "label": "Farm Operator (Irrigation)"},
        {"email": "institution@jalrakshak.local", "role": "INSTITUTION_ADMIN", "label": "Institution Admin (Campus)"},
        {"email": "admin@jalrakshak.local", "role": "ADMINISTRATOR", "label": "System Administrator"},
    ]
    return ApiResponse(data=accounts)
