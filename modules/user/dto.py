from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUserDTO(BaseModel):
    name: str
    email: EmailStr
    password: str


class UpdateUserDTO(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserDTO(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderSummaryDTO(BaseModel):
    id: UUID
    status: str
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailDTO(UserDTO):
    orders: list[OrderSummaryDTO] = []
