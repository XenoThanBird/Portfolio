"""Auth router."""

from fastapi import APIRouter, HTTPException

from app.auth import authenticate_user, create_access_token, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Use an @demo.com email to log in")
    token = create_access_token(request.email)
    return TokenResponse(
        access_token=token,
        user=UserProfile(email=user["email"], name=user["name"], roles=user["roles"]),
    )
