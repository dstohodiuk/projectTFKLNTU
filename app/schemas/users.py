from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ProfileResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


# Що приймаємо при створені юзера
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# Що приймаємо при оновленні юзера
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None

# Що повертаємо клієнту (включає вкладений профіль)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str
    price: float
    description: Optional[str] = None
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    category_id: int

    class Config:
        from_attributes = True