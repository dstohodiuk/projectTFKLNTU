from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import users as schemas
from app import models, crud
from app.core import security

router = APIRouter(
    prefix="/auth",
    tags=["Authentication (JWT & Cookies)"]
)

# 1. РЕЄСТРАЦІЯ (Пароль зберігається ТІЛЬКИ в соленому вигляді)
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Перевіряємо, чи немає вже такого емейлу в базі
    db_user = await crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # ГЕНЕРУЄМО СОЛЕНИЙ ХЕШ ПАРОЛЯ
    pwd_hash = security.get_password_hash(user_in.password)
    
    # Передаємо в CRUD оригінальну схему та окремо згенерований хеш
    new_user = await crud.create_user(db, user_in, hashed_password=pwd_hash)
    return new_user

# 2. АУТЕНТИФІКАЦІЯ (Вхід з генерацією JWT та записом в Cookies)
@router.post("/login")
async def login_user(response: Response, user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Шукаємо користувача за email
    db_user = await crud.get_user_by_email(db, email=user_in.email)
    
    # Перевіряємо, чи існує юзер і чи збігається введений чистий пароль з хешем з БД
    if not db_user or not security.verify_password(user_in.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Створюємо JWT токен, записуючи туди email
    access_token = security.create_access_token(data={"sub": db_user.email})
    
    # КЛАДЕМО ТОКЕН В COOKIES
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,       # Захист від крадіжки токена через JS (XSS атаки)
        max_age=1800,        # Токен живе в браузері 30 хвилин
        samesite="lax"
    )
    
    return {"message": "Successfully logged in", "username": db_user.username}

# 3. ЛОГАУТ (Вихід — просто стираємо куки)
@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}