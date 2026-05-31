from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db.base import Base
from models.enums import CartStatus


class Cart(Base):
    __tablename__ = "cart"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    status = Column(Enum(CartStatus), nullable=False, default=CartStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
