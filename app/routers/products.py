from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.schemas import users as schemas
from app import models

router = APIRouter(
    prefix="/products",
    tags=["Products & Categories"]
)

# 1. POST — Створення категорії
@router.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    db_category = models.Category(name=category_in.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

# 2. GET — Отримання всіх категорій
@router.get("/categories", response_model=List[schemas.CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category))
    return result.scalars().all()

# 3. POST — Створення товару в категорії (One-to-Many)
@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = models.Product(
        title=product_in.title,
        price=product_in.price,
        description=product_in.description,
        category_id=product_in.category_id
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# 4. GET — Отримання всіх товарів
@router.get("/", response_model=List[schemas.ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Product))
    return result.scalars().all()