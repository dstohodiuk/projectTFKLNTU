from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models
from app.schemas import users as schemas

# 1. Отримання одного юзера за ID із його профілем
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.profile))
    )
    return result.scalar_one_or_none()

# 2. Отримання всіх юзерів
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.profile))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# 3. Перевірка юзера за email
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()

# 4. Створення юзера + автоматичне створення зв'язаного профілю
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # Створюємо самого користувача
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    await db.flush()  # Отримуємо id для db_user

    # Створюємо профіль
    db_profile = models.UserProfile(
        user_id=db_user.id,
        full_name=user.full_name,
        bio=""
    )
    db.add(db_profile)
    
    await db.commit()  # Записуємо все в базу на диск

    # СВЯТА ЗВ'ЯЗКА: Робимо чистий, свіжий асинхронний запит, 
    # щоб дістати юзера разом із його профілем безпосередньо з диска
    fresh_user_result = await db.execute(
        select(models.User)
        .where(models.User.id == db_user.id)
        .options(selectinload(models.User.profile))
    )
    return fresh_user_result.scalar_one()

# 5. Оновлення юзера
async def update_user(db: AsyncSession, user_id: int, user_in: schemas.UserUpdate):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "full_name":
            if db_user.profile:
                db_user.profile.full_name = value
        elif hasattr(db_user, key):
            setattr(db_user, key, value)
            
    await db.commit()
    
    # Повертаємо свіжий об'єкт з профілем
    return await get_user(db, user_id)

# 6. Видалення юзера
async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True