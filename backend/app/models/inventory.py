from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Date, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Warehouse(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "warehouses"

    name = Column(String(255), nullable=False)
    type = Column(String(50))  # fba, fbm, 3pl, own
    address = Column(JSONB)
    country_code = Column(String(5))
    marketplace_codes = Column(ARRAY(Text))
    active = Column(Boolean, default=True)

    inventory = relationship("Inventory", back_populates="warehouse")


class Inventory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "inventory"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"))
    marketplace = Column(String(50))
    sku = Column(String(255))
    fnsku = Column(String(255))
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_inbound = Column(Integer, default=0)
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    lead_time_days = Column(Integer, default=30)
    unit_cost = Column(Numeric(12, 4))
    stockout_date = Column(Date)
    overstock_risk = Column(Boolean, default=False)
    last_order_date = Column(Date)

    product = relationship("Product", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventory")
    events = relationship("InventoryEvent", back_populates="inventory")


class InventoryEvent(Base, UUIDMixin):
    __tablename__ = "inventory_events"

    time = Column(DateTime(timezone=True), nullable=False, index=True)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False)
    event_type = Column(String(50))
    quantity_change = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_id = Column(String(255))
    notes = Column(Text)

    inventory = relationship("Inventory", back_populates="events")
