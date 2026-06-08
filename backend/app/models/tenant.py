from sqlalchemy import Column, String, Boolean, Numeric, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Plan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "plans"
    __table_args__ = {"schema": "public"}

    name = Column(String(100), nullable=False)
    stripe_price_id = Column(String(255))
    stripe_product_id = Column(String(255))
    price_monthly = Column(Numeric(10, 2))
    price_annual = Column(Numeric(10, 2))
    limits = Column(JSONB, nullable=False, default={})
    features = Column(JSONB, nullable=False, default={})
    is_active = Column(Boolean, default=True)

    tenants = relationship("Tenant", back_populates="plan")


class Tenant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    slug = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("public.plans.id"))
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    trial_ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    white_label = Column(Boolean, default=False)
    white_label_config = Column(JSONB, default={})
    settings = Column(JSONB, default={})

    plan = relationship("Plan", back_populates="tenants")
    members = relationship("TenantMember", back_populates="tenant")
    marketplace_connections = relationship("MarketplaceConnection", back_populates="tenant")


class TenantMember(Base, UUIDMixin):
    __tablename__ = "tenant_members"
    __table_args__ = {"schema": "public"}

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False, default="analyst")
    permissions = Column(JSONB, default={})
    invited_by = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    joined_at = Column(DateTime(timezone=True), server_default="now()")

    tenant = relationship("Tenant", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="memberships")


class APIKey(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "api_keys"
    __table_args__ = {"schema": "public"}

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)
    scopes = Column(ARRAY(Text), default=[])
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "public"}

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("public.tenants.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    log_metadata = Column("metadata", JSONB, default={})
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default="now()")


class MarketplaceConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "marketplace_connections"
    __table_args__ = {"schema": "public"}

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False)
    marketplace = Column(String(50), nullable=False)
    account_name = Column(String(255))
    credentials = Column(JSONB, nullable=False, default={})
    status = Column(String(50), default="active")
    last_sync_at = Column(DateTime(timezone=True))
    sync_config = Column(JSONB, default={})

    tenant = relationship("Tenant", back_populates="marketplace_connections")
