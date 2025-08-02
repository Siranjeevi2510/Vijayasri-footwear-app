from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # 'admin', 'inventory', 'sales', 'billing'

class UserLogin(BaseModel):
    username: str
    password: str

class Product(BaseModel):
    name: str
    category: str
    size: str
    color: str
    stock: int
    price: float

class SaleItem(BaseModel):
    product_id: str
    quantity: int

class Sale(BaseModel):
    items: List[SaleItem]
    customer: Optional[str] = None

class ExportResponse(BaseModel):
    status: str
    detail: str