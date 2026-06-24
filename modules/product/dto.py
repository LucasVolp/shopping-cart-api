from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class CreateProductDTO(BaseModel):
    category_id: UUID
    name: str
    description: str
    price: float
    quantity_available: int
    image_url: str | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """Ensure the price is greater than zero."""
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v

    @field_validator("quantity_available")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int) -> int:
        """Ensure the initial stock is not negative."""
        if v < 0:
            raise ValueError("Quantity must be zero or greater")
        return v


class UpdateProductDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity_available: int | None = None
    image_url: str | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float | None) -> float | None:
        """Ensure the updated price is greater than zero when provided."""
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than zero")
        return v

    @field_validator("quantity_available")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int | None) -> int | None:
        """Ensure the updated stock is not negative when provided."""
        if v is not None and v < 0:
            raise ValueError("Quantity must be zero or greater")
        return v


class CategorySummaryDTO(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ProductDTO(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    quantity_available: int
    image_url: str | None = None
    category: CategorySummaryDTO
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
