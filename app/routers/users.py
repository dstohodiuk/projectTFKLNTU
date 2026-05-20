from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.users import UserCreate, UserUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Тимчасова база даних у вигляді звичайного словника
USERS_DB = {}
current_id = 0

# POST — Створення юзера
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate):
    global current_id
    
    # Перевірка, чи емейл вже зайнятий
    for user in USERS_DB.values():
        if user["email"] == user_in.email:
            raise HTTPException(status_code=400, detail="Email already registered")
            
    current_id += 1
    new_user = {
        "id": current_id,
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "password": user_in.password
    }
    USERS_DB[current_id] = new_user
    return new_user

# GET (All) — Отримання списку всіх юзерів
@router.get("/", response_model=List[UserResponse])
async def get_users():
    return list(USERS_DB.values())

# GET (One) — Отримання юзера по id
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS_DB[user_id]

# PUT — Оновлення юзера
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
        
    stored_user_data = USERS_DB[user_id]
    # Метод model_dump(exclude_unset=True) бере тільки ті поля, які клієнт явно передав на оновлення
    update_data = user_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        stored_user_data[key] = value
        
    USERS_DB[user_id] = stored_user_data
    return stored_user_data

# DELETE — Видалення юзера
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    del USERS_DB[user_id]
    return None