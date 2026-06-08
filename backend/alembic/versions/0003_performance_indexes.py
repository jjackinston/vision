"""Add composite performance indexes and pg_trgm full-text support.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-08

Indexes added:
  products:
    - idx_products_tracked_marketplace  (is_tracked, marketplace)   — list_products filter
    - idx_products_marketplace_score    (marketplace, opportunity_score DESC) — sort
    - idx_products_title_trgm           GIN trgm on lower(title)    — ilike search

  product_metrics:
    - idx_product_metrics_product_time  (product_id, time DESC)     — time-series lookups

  audit_logs (public schema):
    - idx_audit_logs_tenant_time        (tenant_id, created_at DESC) — admin log queries

  tenant_members (public schema):
    - idx_tenant_members_user           (user_id)                   — auth lookups
    - idx_tenant_members_tenant_user    (tenant_id, user_id)        — membership check

  sales_analytics:
    - idx_sales_analytics_product_time  (product_id, time DESC)     — inventory stockout

All indexes use CONCURRENTLY so they don't lock tables during migration.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enable pg_trgm extension (safe if already exists) ─────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── products table ─────────────────────────────────────────────────
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_tracked_marketplace "
        "ON products (is_tracked, marketplace)"
    )
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_marketplace_score "
        "ON products (marketplace, opportunity_score DESC NULLS LAST)"
    )
    # GIN trigram index accelerates ilike('%query%') on title
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_title_trgm "
        "ON products USING gin (lower(title) gin_trgm_ops)"
    )

    # ── product_metrics table ──────────────────────────────────────────
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_metrics_product_time "
        "ON product_metrics (product_id, time DESC)"
    )

    # ── audit_logs (public schema) ─────────────────────────────────────
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_tenant_time "
        "ON public.audit_logs (tenant_id, created_at DESC)"
    )

    # ── tenant_members (public schema) ────────────────────────────────
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_members_user "
        "ON public.tenant_members (user_id)"
    )
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_members_tenant_user "
        "ON public.tenant_members (tenant_id, user_id)"
    )

    # ── sales_analytics (for inventory stockout prediction join) ───────
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_analytics_product_time "
        "ON sales_analytics (product_id, time DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_products_tracked_marketplace")
    op.execute("DROP INDEX IF EXISTS idx_products_marketplace_score")
    op.execute("DROP INDEX IF EXISTS idx_products_title_trgm")
    op.execute("DROP INDEX IF EXISTS idx_product_metrics_product_time")
    op.execute("DROP INDEX IF EXISTS public.idx_audit_logs_tenant_time")
    op.execute("DROP INDEX IF EXISTS public.idx_tenant_members_user")
    op.execute("DROP INDEX IF EXISTS public.idx_tenant_members_tenant_user")
    op.execute("DROP INDEX IF EXISTS idx_sales_analytics_product_time")
