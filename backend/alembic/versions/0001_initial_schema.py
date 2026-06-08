"""Initial schema — public tables

Revision ID: 0001
Revises:
Create Date: 2026-06-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table("plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("stripe_price_id", sa.String(255)),
        sa.Column("stripe_product_id", sa.String(255)),
        sa.Column("price_monthly", sa.Numeric(10, 2)),
        sa.Column("price_annual", sa.Numeric(10, 2)),
        sa.Column("limits", JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("features", JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )

    op.create_table("users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("clerk_id", sa.String(255), unique=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("avatar_url", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )

    op.create_table("tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("public.plans.id")),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("stripe_subscription_id", sa.String(255)),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("white_label", sa.Boolean, server_default="false"),
        sa.Column("white_label_config", JSONB, server_default=sa.text("'{}'")),
        sa.Column("settings", JSONB, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )

    op.create_table("tenant_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="'analyst'"),
        sa.Column("permissions", JSONB, server_default=sa.text("'{}'")),
        sa.Column("invited_by", UUID(as_uuid=True), sa.ForeignKey("public.users.id")),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "user_id"),
        schema="public",
    )

    op.create_table("marketplace_connections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("marketplace", sa.String(50), nullable=False),
        sa.Column("account_name", sa.String(255)),
        sa.Column("credentials", JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("status", sa.String(50), server_default="'pending'"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True)),
        sa.Column("sync_config", JSONB, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )

    op.create_table("api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("public.tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("public.users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("scopes", ARRAY(sa.Text), server_default=sa.text("'{}'")),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )

    op.create_table("audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True)),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(100)),
        sa.Column("resource_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'")),
        sa.Column("ip_address", INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )
    op.create_index("idx_audit_logs_tenant", "audit_logs", ["tenant_id", "created_at"], schema="public")


def downgrade() -> None:
    op.drop_index("idx_audit_logs_tenant", "audit_logs", schema="public")
    op.drop_table("audit_logs", schema="public")
    op.drop_table("api_keys", schema="public")
    op.drop_table("marketplace_connections", schema="public")
    op.drop_table("tenant_members", schema="public")
    op.drop_table("tenants", schema="public")
    op.drop_table("users", schema="public")
    op.drop_table("plans", schema="public")
