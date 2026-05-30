from uuid import UUID

from core.data_structures.array import DynamicArray
from models.product import Product
from modules.product.dto import CreateProductDTO, UpdateProductDTO
from modules.product.repository import ProductRepository


class ProductUseCases:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_all(self) -> DynamicArray[Product]:
        """Fetch all products from the database and load them into a DynamicArray.

        Each product is appended one by one, exercising the array's append
        operation (O(1) amortized).  The caller receives a DynamicArray that
        supports index access, iteration, and len().

        Complexity: O(n) — one append per product.
        """
        products = self.repository.find_all()
        array: DynamicArray[Product] = DynamicArray()
        for product in products:
            array.append(product)
        return array

    def get_by_id(self, product_id: UUID) -> Product:
        """Return a single product by ID or raise ValueError if not found.

        Complexity: O(1) — single indexed lookup in the database.
        """
        product = self.repository.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        return product

    def create(self, dto: CreateProductDTO) -> Product:
        """Create and persist a new product.

        Complexity: O(1) — single insert.
        """
        product = Product(
            category_id=dto.category_id,
            name=dto.name,
            description=dto.description,
            price=dto.price,
            quantity_available=dto.quantity_available,
        )
        return self.repository.create(product)

    def update(self, product_id: UUID, dto: UpdateProductDTO) -> Product:
        """Update allowed fields of an existing product.

        Only fields explicitly provided in the DTO are changed.
        Raises ValueError if the product is not found.

        Complexity: O(1) — single fetch and update.
        """
        product = self.get_by_id(product_id)
        if dto.name is not None:
            product.name = dto.name
        if dto.description is not None:
            product.description = dto.description
        if dto.price is not None:
            product.price = dto.price
        if dto.quantity_available is not None:
            product.quantity_available = dto.quantity_available
        return self.repository.update(product)

    def delete(self, product_id: UUID) -> None:
        """Delete a product by ID or raise ValueError if not found.

        Complexity: O(1) — single fetch and delete.
        """
        product = self.get_by_id(product_id)
        self.repository.delete(product)
