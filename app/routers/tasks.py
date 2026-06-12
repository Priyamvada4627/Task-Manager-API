from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.middleware.auth import get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        due_date=body.due_date,
        user_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return {
        "status": "success",
        "message": "Task created successfully",
        "data": {"task": _serialize(task)},
    }


@router.get("/")
async def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[UUID] = Query(None, alias="userId"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if status_filter:
        filters.append(Task.status == status_filter)
    if priority:
        filters.append(Task.priority == priority)

    if current_user.role == "admin":
        if user_id:
            filters.append(Task.user_id == user_id)
    else:
        filters.append(Task.user_id == current_user.id)

    offset = (page - 1) * limit

    # Count
    count_q = select(func.count()).select_from(Task).where(*filters)
    total = (await db.execute(count_q)).scalar_one()

    # Rows — include owner for admins
    base_q = (
        select(Task)
        .where(*filters)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if current_user.role == "admin":
        base_q = base_q.options(selectinload(Task.owner))

    rows = (await db.execute(base_q)).scalars().all()

    return {
        "status": "success",
        "data": {
            "tasks": [_serialize(t, include_owner=current_user.role == "admin") for t in rows],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": -(-total // limit),  # ceiling division
            },
        },
    }


@router.get("/{task_id}")
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_task_or_404(db, task_id, include_owner=True)
    _check_ownership(current_user, task)
    return {"status": "success", "data": {"task": _serialize(task, include_owner=True)}}


@router.patch("/{task_id}")
async def update_task(
    task_id: UUID,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_task_or_404(db, task_id)
    _check_ownership(current_user, task)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    return {
        "status": "success",
        "message": "Task updated successfully",
        "data": {"task": _serialize(task)},
    }


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_task_or_404(db, task_id)
    _check_ownership(current_user, task)

    await db.delete(task)
    await db.commit()

    return {"status": "success", "message": "Task deleted successfully", "data": None}


# ── Helpers ───────────────────────────────────────────────────────────

async def _get_task_or_404(
    db: AsyncSession, task_id: UUID, include_owner: bool = False
) -> Task:
    q = select(Task).where(Task.id == task_id)
    if include_owner:
        q = q.options(selectinload(Task.owner))
    task = (await db.execute(q)).scalar_one_or_none()
    if not task:
        raise NotFoundError("Task not found")
    return task


def _check_ownership(user: User, task: Task) -> None:
    if user.role != "admin" and task.user_id != user.id:
        raise ForbiddenError("You do not have permission to access this task")


def _serialize(task: Task, include_owner: bool = False) -> dict:
    d = {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "user_id": str(task.user_id),
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    if include_owner and task.owner:
        d["owner"] = {
            "id": str(task.owner.id),
            "name": task.owner.name,
            "email": task.owner.email,
        }
    return d
