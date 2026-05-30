from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db.base import Base


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("quantity_available >= 0", name="ck_product_quantity_available_non_negative"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity_available = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
