"""Remaining ORM models: Competitor, Supplier, Listing, PPC, Trend, AgentRun, Workflow, Analytics, Notification, MarketplaceAsset."""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Competitor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "competitors"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    asin = Column(String(20))
    marketplace = Column(String(50), nullable=False)
    seller_id = Column(String(100))
    brand = Column(String(255))
    title = Column(String(1000))
    price = Column(Numeric(12, 2))
    review_count = Column(Integer)
    review_rating = Column(Numeric(3, 2))
    monthly_sales = Column(Integer)
    monthly_revenue = Column(Numeric(12, 2))
    weakness_analysis = Column(JSONB, default={})
    threat_level = Column(String(20))
    tracked_since = Column(DateTime(timezone=True), server_default="now()")

    product = relationship("Product", back_populates="competitors")


class Supplier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suppliers"

    name = Column(String(255), nullable=False)
    country = Column(String(100))
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website = Column(Text)
    alibaba_url = Column(Text)
    trust_score = Column(Numeric(5, 2))
    risk_score = Column(Numeric(5, 2))
    quality_score = Column(Numeric(5, 2))
    reliability_score = Column(Numeric(5, 2))
    avg_lead_time_days = Column(Integer)
    min_order_qty = Column(Integer)
    payment_terms = Column(String(255))
    shipping_methods = Column(ARRAY(Text))
    certifications = Column(ARRAY(Text))
    notes = Column(Text)
    ai_analysis = Column(JSONB, default={})

    products = relationship("SupplierProduct", back_populates="supplier")


class SupplierProduct(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "supplier_products"

    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    supplier_sku = Column(String(255))
    unit_cost = Column(Numeric(12, 4), nullable=False)
    moq = Column(Integer)
    sample_cost = Column(Numeric(10, 2))
    lead_time_days = Column(Integer)
    is_preferred = Column(Boolean, default=False)
    last_quoted_at = Column(DateTime(timezone=True))

    supplier = relationship("Supplier", back_populates="products")


class Listing(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "listings"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(50), nullable=False)
    external_id = Column(String(255))
    title = Column(String(1000))
    bullet_points = Column(ARRAY(Text))
    description = Column(Text)
    a_plus_content = Column(JSONB)
    backend_keywords = Column(ARRAY(Text))
    images = Column(JSONB)
    price = Column(Numeric(12, 2))
    sale_price = Column(Numeric(12, 2))
    status = Column(String(50), default="draft")
    seo_score = Column(Numeric(5, 2))
    completeness_score = Column(Numeric(5, 2))
    ai_generated = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    last_synced_at = Column(DateTime(timezone=True))

    product = relationship("Product", back_populates="listings")


class PPCCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ppc_campaigns"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    marketplace = Column(String(50), nullable=False)
    campaign_id = Column(String(255))
    name = Column(String(500))
    type = Column(String(50))
    status = Column(String(50))
    daily_budget = Column(Numeric(10, 2))
    spend_today = Column(Numeric(10, 2))
    impressions = Column(Integer)
    clicks = Column(Integer)
    orders = Column(Integer)
    revenue = Column(Numeric(12, 2))
    acos = Column(Numeric(5, 2))
    roas = Column(Numeric(5, 2))
    tacos = Column(Numeric(5, 2))
    ai_recommendations = Column(JSONB, default={})

    product = relationship("Product", back_populates="ppc_campaigns")


class Trend(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trends"

    topic = Column(String(500), nullable=False)
    source = Column(String(50))
    category = Column(String(255))
    trend_score = Column(Numeric(5, 2))
    momentum_score = Column(Numeric(5, 2))
    viral_score = Column(Numeric(5, 2))
    lifespan_prediction = Column(String(50))
    peak_date_estimate = Column(DateTime(timezone=True))
    related_products = Column(ARRAY(Text))
    data_points = Column(JSONB, default={})
    ai_analysis = Column(JSONB, default={})
    detected_at = Column(DateTime(timezone=True), server_default="now()")


class AgentRun(Base, UUIDMixin):
    __tablename__ = "agent_runs"

    agent_type = Column(String(100), nullable=False)
    status = Column(String(50), default="running")
    input = Column(JSONB, default={})
    output = Column(JSONB, default={})
    steps = Column(JSONB, default=[])
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6))
    error = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default="now()")
    completed_at = Column(DateTime(timezone=True))


class Workflow(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflows"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(100))
    trigger_config = Column(JSONB, default={})
    steps = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    run_count = Column(Integer, default=0)


class SalesAnalytic(Base, UUIDMixin):
    __tablename__ = "sales_analytics"

    time = Column(DateTime(timezone=True), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(50), nullable=False)
    orders = Column(Integer, default=0)
    units_sold = Column(Integer, default=0)
    gross_revenue = Column(Numeric(14, 2), default=0)
    refunds = Column(Numeric(14, 2), default=0)
    platform_fees = Column(Numeric(14, 2), default=0)
    ad_spend = Column(Numeric(14, 2), default=0)
    cogs = Column(Numeric(14, 2), default=0)
    net_profit = Column(Numeric(14, 2), default=0)
    roi = Column(Numeric(6, 4))

    product = relationship("Product", back_populates="sales_analytics")


class Notification(Base, UUIDMixin):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)
    type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    body = Column(Text)
    action_url = Column(Text)
    extra_data = Column("metadata", JSONB, default={})
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default="now()")


class MarketplaceAsset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "marketplace_assets"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    type = Column(String(50))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), default=0)
    downloads = Column(Integer, default=0)
    rating = Column(Numeric(3, 2))
    rating_count = Column(Integer, default=0)
    asset_data = Column(JSONB, nullable=False, default={})
    tags = Column(ARRAY(Text))
    preview_images = Column(ARRAY(Text))
    is_published = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)


