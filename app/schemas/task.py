from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


TaskStatus = Literal["pending", "in-progress", "completed"]
TaskPriority = Literal["low", "medium", "high"]


# ── Request bodies ────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    status: TaskStatus = "pending"
    priority: TaskPriority = "medium"
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None


# ── Nested owner inside task (admin view) ─────────────────────────────

class OwnerOut(BaseModel):
    id: UUID
    name: str
    email: str

    model_config = {"from_attributes": True}


# ── Response bodies ───────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    user_id: UUID
    owner: Optional[OwnerOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class TaskListResponse(BaseModel):
    status: str = "success"
    data: dict


class TaskResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: dict
