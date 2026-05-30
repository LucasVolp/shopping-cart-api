from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.product.dto import CreateProductDTO, ProductDTO, UpdateProductDTO
from modules.product.repository import ProductRepository
from modules.product.use_cases import ProductUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> ProductUseCases:
    """Dependency that wires the repository and use case for injection."""
    return ProductUseCases(ProductRepository(db))


@router.get("/", response_model=list[ProductDTO])
def list_products(use_case: ProductUseCases = Depends(get_use_case)):
    """List all products.

    Internally the use case stores results in a DynamicArray before returning.
    The router converts it to a plain list for JSON serialisation.
    """
    return list(use_case.get_all())


@router.get("/{product_id}", response_model=ProductDTO)
def get_product(product_id: UUID, use_case: ProductUseCases = Depends(get_use_case)):
    """Get a single product by ID."""
    try:
        return use_case.get_by_id(product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=ProductDTO, status_code=status.HTTP_201_CREATED)
def create_product(dto: CreateProductDTO, use_case: ProductUseCases = Depends(get_use_case)):
    """Create a new product."""
    return use_case.create(dto)


@router.put("/{product_id}", response_model=ProductDTO)
def update_product(
    product_id: UUID,
    dto: UpdateProductDTO,
    use_case: ProductUseCases = Depends(get_use_case),
):
    """Update a product's fields."""
    try:
        return use_case.update(product_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, use_case: ProductUseCases = Depends(get_use_case)):
    """Delete a product by ID."""
    try:
        use_case.delete(product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
