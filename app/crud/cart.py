from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.cart import Cart
from app.models.product import Product


async def add_to_cart(db: AsyncSession, user_id: int, product_id: int, quantity: int = 1):
    # Check if item already in cart
    result = await db.execute(
        select(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def remove_from_cart(db: AsyncSession, user_id: int, product_id: int):
    result = await db.execute(
        select(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
    )
    cart_item = result.scalar_one_or_none()
    if cart_item:
        await db.delete(cart_item)
        await db.commit()
    return cart_item


async def clear_cart(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    cart_items = result.scalars().all()
    for item in cart_items:
        await db.delete(item)
    await db.commit()
    return len(cart_items)


async def get_cart_items(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    return result.scalars().all()


async def get_cart_total(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(func.sum(Product.price * Cart.quantity))
        .select_from(Cart.__table__.join(Product.__table__))
        .filter(Cart.user_id == user_id)
    )
    total = result.scalar()
    return total or 0