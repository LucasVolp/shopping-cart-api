from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from models.enums.enums import CartStatus


class AddCartItemDTO(BaseModel):
    product_id: UUID
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        """Ensure the quantity is at least one."""
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v


class UpdateCartItemDTO(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        """Ensure the updated quantity is at least one."""
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v


class CartItemProductDTO(BaseModel):
    id: UUID
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class CartItemDTO(BaseModel):
    id: UUID
    product: CartItemProductDTO
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class CartDTO(BaseModel):
    id: UUID
    user_id: UUID
    status: CartStatus
    items: list[CartItemDTO] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
