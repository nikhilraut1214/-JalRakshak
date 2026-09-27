import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Helper to generate JWT tokens for testing or dev login."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.setdefault("aud", settings.SUPABASE_JWT_AUDIENCE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Verifies and decodes the JWT token.
    Checks signature, expiration, and expected audience.
    """
    try:
        # HS256 with SUPABASE_JWT_SECRET and strict audience validation
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=settings.SUPABASE_JWT_AUDIENCE,
            options={"verify_aud": True}
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Enforces server-side authentication:
    - Verifies Bearer JWT
    - Extracts subject identity (user_id) and metadata
    - Ensures user exists in local database or creates synced record
    - Rejects unauthenticated requests
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Bearer JWT access token is missing.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identity (sub)",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Find or sync user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # If user not found by id, check email
        if email:
            user = db.query(User).filter(User.email == email).first()
        if not user:
            role = (
                payload.get("user_metadata", {}).get("role") or
                payload.get("app_metadata", {}).get("role") or
                "RESIDENT"
            )
            org_id = (
                payload.get("user_metadata", {}).get("organization_id") or
                settings.DEFAULT_ORG_ID
            )
            user = User(
                id=user_id,
                email=email or f"{user_id}@supabase.auth",
                role=role,
                organization_id=org_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    return user
