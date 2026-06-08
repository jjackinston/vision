from sqlalchemy import Column, String, Boolean, Numeric, Integer, Text, ARRAY, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"

    asin = Column(String(20), index=True)
    walmart_item_id = Column(String(50))
    shopify_product_id = Column(String(100))
    ebay_item_id = Column(String(100))
    tiktok_product_id = Column(String(100))
    etsy_listing_id = Column(String(100))
    title = Column(String(1000), nullable=False)
    brand = Column(String(255))
    category = Column(String(255))
    subcategory = Column(String(255))
    marketplace = Column(String(50), nullable=False, index=True)
    image_urls = Column(ARRAY(Text), default=[])
    current_price = Column(Numeric(12, 2))
    buy_box_price = Column(Numeric(12, 2))
    cost = Column(Numeric(12, 2))
    weight_lbs = Column(Numeric(8, 3))
    dimensions = Column(JSONB)
    is_tracked = Column(Boolean, default=False, index=True)
    is_own_product = Column(Boolean, default=False)
    tags = Column(ARRAY(Text), default=[])
    notes = Column(Text)
    opportunity_score = Column(Numeric(5, 2), index=True)
    risk_score = Column(Numeric(5, 2))
    profit_score = Column(Numeric(5, 2))
    competition_score = Column(Numeric(5, 2))
    market_entry_score = Column(Numeric(5, 2))
    ai_analysis = Column(JSONB, default={})

    keywords = relationship("ProductKeyword", back_populates="product")
    competitors = relationship("Competitor", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")
    listings = relationship("Listing", back_populates="product")
    ppc_campaigns = relationship("PPCCampaign", back_populates="product")
    sales_analytics = relationship("SalesAnalytic", back_populates="product")


class ProductMetric(Base, UUIDMixin):
    """TimescaleDB hypertable — partitioned by time."""
    __tablename__ = "product_metrics"

    from sqlalchemy import DateTime
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    marketplace = Column(String(50), nullable=False)
    price = Column(Numeric(12, 2))
    bsr_rank = Column(Integer)
    bsr_category = Column(String(255))
    review_count = Column(Integer)
    review_rating = Column(Numeric(3, 2))
    estimated_sales = Column(Integer)
    estimated_revenue = Column(Numeric(12, 2))
    seller_count = Column(Integer)
    buy_box_seller = Column(String(255))
    stock_level = Column(String(50))
    extra_data = Column("metadata", JSONB, default={})
