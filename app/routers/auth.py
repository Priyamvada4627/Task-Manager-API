from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.jwt import generate_access_token, generate_refresh_token, verify_refresh_token
from app.core.exceptions import ConflictError, UnauthorizedError
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate email
    result = await db.execute(
        select(User).where(User.email == body.email.lower().strip())
    )
    if result.scalar_one_or_none():
        raise ConflictError("A user with this email already exists")

    # Role guard — same logic as the JS version
    allowed_role = (
        "admin"
        if body.role == "admin" and settings.ALLOW_ADMIN_SIGNUP
        else "user"
    )

    user = User(name=body.name, email=body.email.lower().strip(), role=allowed_role)
    user.set_password(body.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "message": "User registered successfully",
        "data": {
            "user": user.to_safe_dict(),
            "access_token": generate_access_token(str(user.id), user.role),
            "refresh_token": generate_refresh_token(str(user.id), user.role),
        },
    }


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == body.email.lower().strip())
    )
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(body.password):
        raise UnauthorizedError("Invalid email or password")

    return {
        "status": "success",
        "message": "Logged in successfully",
        "data": {
            "user": user.to_safe_dict(),
            "access_token": generate_access_token(str(user.id), user.role),
            "refresh_token": generate_refresh_token(str(user.id), user.role),
        },
    }


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = verify_refresh_token(body.get_token())

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User no longer exists")

    return {
        "status": "success",
        "data": {"access_token": generate_access_token(str(user.id), user.role)},
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"status": "success", "data": {"user": current_user.to_safe_dict()}}
