from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app import crud
# Імпортуємо модуль users як schemas, щоб працював твій response_model=schemas.UserResponse
from app.schemas import users as schemas 

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 1. POST — Створення юзера (з перевіркою емейлу через БД)
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user_in)

# 2. GET (All) — Отримання списку всіх юзерів з бази
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

# 3. GET (One) — Отримання юзера по id
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 4. PUT — Оновлення юзера
@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.update_user(db=db, user_id=user_id, user_in=user_in)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 5. DELETE — Видалення юзера
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None