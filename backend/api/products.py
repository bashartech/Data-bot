from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.engine import get_session
from repositories.product_repo import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])


class ProductResponse(BaseModel):
    id: UUID
    product_name: str
    category: str
    description: str
    price: float
    stock: int
    manufacturer: str
    created_at: str


class ProductDetailResponse(ProductResponse):
    specifications: str | None = None
    warranty: str | None = None
    country: str | None = None
    weight: float | None = None


@router.get("")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ProductRepository(session)
    products = await repo.list_all(skip=skip, limit=limit)
    return [
        ProductResponse(
            id=p.id,
            product_name=p.product_name,
            category=p.category,
            description=p.description,
            price=p.price,
            stock=p.stock,
            manufacturer=p.manufacturer,
            created_at=p.created_at.isoformat(),
        )
        for p in products
    ]


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ProductRepository(session)
    products = await repo.search(q, limit=limit)
    return [
        ProductResponse(
            id=p.id,
            product_name=p.product_name,
            category=p.category,
            description=p.description,
            price=p.price,
            stock=p.stock,
            manufacturer=p.manufacturer,
            created_at=p.created_at.isoformat(),
        )
        for p in products
    ]


@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductDetailResponse(
        id=product.id,
        product_name=product.product_name,
        category=product.category,
        description=product.description,
        price=product.price,
        stock=product.stock,
        manufacturer=product.manufacturer,
        created_at=product.created_at.isoformat(),
        specifications=product.detail.specifications if product.detail else None,
        warranty=product.detail.warranty if product.detail else None,
        country=product.detail.country if product.detail else None,
        weight=product.detail.weight if product.detail else None,
    )
