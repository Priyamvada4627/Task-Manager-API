from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request bodies ────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)
    role: Literal["user", "admin"] = "user"

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    # Frontend sends camelCase (refreshToken); snake_case also accepted
    model_config = {"populate_by_name": True}

    refreshToken: str = Field(None)
    refresh_token: str = Field(None)

    def get_token(self) -> str:
        return self.refreshToken or self.refresh_token or ""


# ── Response bodies ───────────────────────────────────────────────────

class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokensOut(BaseModel):
    access_token: str
    refresh_token: str


class RegisterResponse(BaseModel):
    status: str = "success"
    message: str
    data: dict


class LoginResponse(BaseModel):
    status: str = "success"
    message: str
    data: dict


class RefreshResponse(BaseModel):
    status: str = "success"
    data: dict


class MeResponse(BaseModel):
    status: str = "success"
    data: dict
