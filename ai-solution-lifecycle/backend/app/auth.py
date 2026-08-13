"""
Mock JWT authentication for demo mode.
Accepts any @demo.com email. Replace with real SSO in production.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(email: str) -> str:
    """Generate a JWT token for the given email."""
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        "roles": ["admin", "analyst"] if "admin" in email else ["analyst"],
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return user profile. FastAPI dependency."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return {
            "email": email,
            "name": email.split("@")[0].replace(".", " ").title(),
            "roles": payload.get("roles", ["analyst"]),
        }
    except JWTError:
        raise credentials_exception


def authenticate_user(email: str, password: str) -> dict | None:
    """Mock auth: accept any @demo.com email with any password."""
    if email.endswith("@demo.com"):
        return {
            "email": email,
            "name": email.split("@")[0].replace(".", " ").title(),
            "roles": ["admin", "analyst"] if "admin" in email else ["analyst"],
        }
    return None
