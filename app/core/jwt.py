from datetime import datetime, timedelta, timezone
from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


def _make_token(payload: dict, secret: str, expires_days: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    return jwt.encode({**payload, "exp": expire}, secret, algorithm="HS256")


def generate_access_token(user_id: str, role: str) -> str:
    return _make_token(
        {"sub": user_id, "role": role},
        settings.JWT_SECRET,
        settings.JWT_EXPIRES_IN,
    )


def generate_refresh_token(user_id: str, role: str) -> str:
    return _make_token(
        {"sub": user_id, "role": role},
        settings.JWT_REFRESH_SECRET,
        settings.JWT_REFRESH_EXPIRES_IN,
    )


def _decode(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise UnauthorizedError("Your session has expired. Please log in again.")
    except JWTError:
        raise UnauthorizedError("Invalid authentication token.")


def verify_access_token(token: str) -> dict:
    return _decode(token, settings.JWT_SECRET)


def verify_refresh_token(token: str) -> dict:
    return _decode(token, settings.JWT_REFRESH_SECRET)
