import uuid
from sqlalchemy import Column, String, Text, Enum as SAEnum, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum("pending", "in-progress", "completed", name="task_status"),
        nullable=False,
        default="pending",
    )
    priority = Column(
        SAEnum("low", "medium", "high", name="task_priority"),
        nullable=False,
        default="medium",
    )
    due_date = Column(Date, nullable=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="tasks")
