from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Загальні поля для користувача
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

# Схема для створення (тут обов'язково передавати пароль)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Схема для оновлення (всі поля необов'язкові, міняємо тільки те, що прислали)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)

# Схема, яку сервер повертає клієнту (без пароля з міркувань безпеки)
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True