from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud.product import get_products, get_product, create_product, update_product, delete_product
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Product])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    products = await get_products(db, skip=skip, limit=limit)
    return products

@router.post("/", response_model=Product)
async def create_product_endpoint(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return await create_product(db, product)

@router.put("/{product_id}", response_model=Product)
async def update_product_endpoint(
    product_id: int,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_product = await update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
async def delete_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_product = await delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}