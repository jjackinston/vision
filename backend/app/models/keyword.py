from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ARRAY, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Keyword(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "keywords"

    keyword = Column(String(500), nullable=False)
    marketplace = Column(String(50), nullable=False)
    monthly_searches = Column(Integer)
    search_volume_trend = Column(Numeric(5, 2))
    cpc = Column(Numeric(8, 4))
    competition_level = Column(String(20))
    difficulty_score = Column(Numeric(5, 2))
    opportunity_score = Column(Numeric(5, 2), index=True)
    ppc_score = Column(Numeric(5, 2))
    seo_score = Column(Numeric(5, 2))
    intent = Column(String(50))
    cluster_id = Column(UUID(as_uuid=True))
    parent_keyword = Column(String(500))
    related_keywords = Column(ARRAY(Text), default=[])
    ai_analysis = Column(JSONB, default={})
    last_updated = Column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("keyword", "marketplace"),)

    product_keywords = relationship("ProductKeyword", back_populates="keyword")


class KeywordMetric(Base, UUIDMixin):
    __tablename__ = "keyword_metrics"

    time = Column(DateTime(timezone=True), nullable=False, index=True)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    search_volume = Column(Integer)
    cpc = Column(Numeric(8, 4))
    ranking_products = Column(Integer)
    top_3_asins = Column(ARRAY(Text))
    sponsored_count = Column(Integer)


class ProductKeyword(Base, UUIDMixin):
    __tablename__ = "product_keywords"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    organic_rank = Column(Integer)
    sponsored_rank = Column(Integer)
    indexed = Column(Boolean, default=False)
    relevance_score = Column(Numeric(5, 2))
    updated_at = Column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("product_id", "keyword_id"),)

    product = relationship("Product", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="product_keywords")
