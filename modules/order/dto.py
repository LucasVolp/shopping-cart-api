from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.enums.enums import OrderStatus, PaymentMethod, PaymentStatus


class CheckoutDTO(BaseModel):
    payment_method: PaymentMethod


class OrderItemDTO(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    unit_price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class PaymentSummaryDTO(BaseModel):
    id: UUID
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class OrderDTO(BaseModel):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetailDTO(OrderDTO):
    items: list[OrderItemDTO] = []
    payment: PaymentSummaryDTO | None = None
