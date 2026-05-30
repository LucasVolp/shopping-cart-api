from uuid import UUID

from core.data_structures.array import DynamicArray
from models.category import Category
from modules.category.dto import CreateCategoryDTO, UpdateCategoryDTO
from modules.category.repository import CategoryRepository


class CategoryUseCases:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def get_all(self) -> DynamicArray[Category]:
        """Fetch all categories and load them into a DynamicArray.

        Complexity: O(n) — one append per category.
        """
        categories = self.repository.find_all()
        array: DynamicArray[Category] = DynamicArray()
        for category in categories:
            array.append(category)
        return array

    def get_by_id(self, category_id: UUID) -> Category:
        """Return a category by ID or raise ValueError if not found."""
        category = self.repository.find_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        return category

    def create(self, dto: CreateCategoryDTO) -> Category:
        """Create a new category.

        Raises ValueError if a category with the same name already exists.
        """
        if self.repository.find_by_name(dto.name):
            raise ValueError("Category name already exists")
        return self.repository.create(Category(name=dto.name))

    def update(self, category_id: UUID, dto: UpdateCategoryDTO) -> Category:
        """Update a category's name.

        Raises ValueError if the category is not found or if the name is taken.
        """
        category = self.get_by_id(category_id)
        if dto.name is not None:
            if self.repository.find_by_name(dto.name):
                raise ValueError("Category name already exists")
            category.name = dto.name
        return self.repository.update(category)

    def delete(self, category_id: UUID) -> None:
        """Delete a category by ID or raise ValueError if not found."""
        category = self.get_by_id(category_id)
        self.repository.delete(category)
