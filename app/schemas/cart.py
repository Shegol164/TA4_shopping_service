from pydantic import BaseModel
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class CartTotal(BaseModel):
    total: Decimal