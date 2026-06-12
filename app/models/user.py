import uuid
from passlib.context import CryptContext
from sqlalchemy import Column, String, Enum as SAEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    role = Column(SAEnum("user", "admin", name="user_role"), nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    # ── Password helpers ──────────────────────────────────────────────

    def set_password(self, raw: str) -> None:
        self.password = pwd_context.hash(raw)

    def verify_password(self, raw: str) -> bool:
        return pwd_context.verify(raw, self.password)

    def to_safe_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
