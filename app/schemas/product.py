from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    price: Decimal

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    is_active: bool | None = None

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True