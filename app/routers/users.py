import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app import crud, models
# Імпортуємо модуль users як schemas, щоб працював твій response_model=schemas.UserResponse
from app.schemas import users as schemas 
from app.config import settings

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# =================================================================
# 0. ЗАЛЕЖНІСТЬ (DEPENDENCY) ДЛЯ АВТЕНТИФІКАЦІЇ КОРИСТУВАЧА ЧЕРЕЗ COOKIES
# =================================================================
async def get_current_user(db: AsyncSession = Depends(get_db), access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated (Missing token in cookies)"
        )
    
    # Прибираємо префікс "Bearer ", якщо він автоматично додався
    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token
    
    try:
        # Розшифровуємо JWT токен за допомогою нашого SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired or is invalid")
        
    # Шукаємо користувача в базі по email, який дістали з токена
    db_user = await crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return db_user


# =================================================================
# ЗАХИЩЕНІ РУЧКИ (ВИМАГАЮТЬ АВТЕНТИФІКАЦІЇ)
# =================================================================

# 1. GET /users/me — Отримання профілю поточного залогіненого користувача
@router.get("/me", response_model=schemas.UserResponse)
async def get_my_profile(current_user: models.User = Depends(get_current_user)):
    # Сюди пустить ТІЛЬКИ якщо користувач залогінений
    return current_user

# 2. PUT /users/me/profile — Оновлення інформації у своєму профілі
@router.put("/me/profile", response_model=schemas.UserResponse)
async def update_my_profile(
    user_in: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Оновлюємо дані саме того юзера, який зараз авторизований
    db_user = await crud.update_user(db=db, user_id=current_user.id, user_in=user_in)
    return db_user




# POST — Створення юзера (з перевіркою емейлу через БД)
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user_in)

# GET (All) — Отримання списку всіх юзерів з бази
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

# GET (One) — Отримання юзера по id
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# PUT — Оновлення юзера по id
@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.update_user(db=db, user_id=user_id, user_in=user_in)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# DELETE — Видалення юзера
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None