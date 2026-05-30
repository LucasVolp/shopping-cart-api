from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.product import Product


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self) -> list[Product]:
        """Return all products with their category eagerly loaded."""
        return list(
            self.session.scalars(
                select(Product).options(selectinload(Product.category))
            ).all()
        )

    def find_by_id(self, product_id: UUID) -> Product | None:
        """Find a product by ID with its category eagerly loaded."""
        return self.session.scalars(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        ).first()

    def create(self, product: Product) -> Product:
        """Persist a new product and return it with generated fields populated."""
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        """Commit changes to an existing product and return the refreshed instance."""
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        """Delete a product from the database."""
        self.session.delete(product)
        self.session.commit()
