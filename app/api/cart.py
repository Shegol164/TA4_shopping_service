from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud.cart import add_to_cart, remove_from_cart, clear_cart, get_cart_items, get_cart_total
from app.schemas.cart import CartItemCreate, CartItem, CartTotal
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/add")
async def add_to_cart_endpoint(
    cart_item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    cart_item = await add_to_cart(db, current_user.id, cart_item.product_id, cart_item.quantity)
    return {"message": "Item added to cart", "cart_item": cart_item}

@router.delete("/remove")
async def remove_from_cart_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    cart_item = await remove_from_cart(db, current_user.id, product_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": "Item removed from cart"}

@router.delete("/clear")
async def clear_cart_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    count = await clear_cart(db, current_user.id)
    return {"message": f"Cart cleared, {count} items removed"}

@router.get("/items", response_model=List[CartItem])
async def get_cart_items_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    cart_items = await get_cart_items(db, current_user.id)
    return cart_items

@router.get("/total", response_model=CartTotal)
async def get_cart_total_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    total = await get_cart_total(db, current_user.id)
    return {"total": total}