from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.middleware.auth import require_role
from app.models.user import User
from app.schemas.admin import UpdateRoleRequest

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_only = Depends(require_role("admin"))


@router.get("/users", dependencies=[admin_only])
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit

    total = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    rows = (
        await db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()

    return {
        "status": "success",
        "data": {
            "users": [u.to_safe_dict() for u in rows],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": -(-total // limit),
            },
        },
    }


@router.patch("/users/{user_id}/role", dependencies=[admin_only])
async def update_user_role(
    user_id: UUID,
    body: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")

    user.role = body.role
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "message": "User role updated successfully",
        "data": {"user": user.to_safe_dict()},
    }
