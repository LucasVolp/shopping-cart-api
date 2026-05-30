from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateCategoryDTO(BaseModel):
    name: str


class UpdateCategoryDTO(BaseModel):
    name: str | None = None


class CategoryDTO(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
