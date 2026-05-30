from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self) -> list[Category]:
        """Return all categories."""
        return list(self.session.scalars(select(Category)).all())

    def find_by_id(self, category_id: UUID) -> Category | None:
        """Find a category by ID."""
        return self.session.scalars(
            select(Category).where(Category.id == category_id)
        ).first()

    def find_by_name(self, name: str) -> Category | None:
        """Find a category by exact name."""
        return self.session.scalars(
            select(Category).where(Category.name == name)
        ).first()

    def create(self, category: Category) -> Category:
        """Persist a new category and return it with generated fields populated."""
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        """Commit changes to an existing category and return the refreshed instance."""
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        """Delete a category from the database."""
        self.session.delete(category)
        self.session.commit()
