from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.enums.enums import PaymentMethod, PaymentStatus


class UpdatePaymentStatusDTO(BaseModel):
    payment_status: PaymentStatus


class PaymentDTO(BaseModel):
    id: UUID
    order_id: UUID
    total_amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
