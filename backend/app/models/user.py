from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    clerk_id = Column(String(255), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))

    memberships = relationship("TenantMember", foreign_keys="TenantMember.user_id", back_populates="user")
