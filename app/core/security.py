from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from app.config import settings

# 1. Хешування чистого пароля ("1234" -> солений хеш)
def get_password_hash(password: str) -> str:
    # Перетворюємо рядок у байти, генеруємо сіль і робимо хеш
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')  # Повертаємо назад як рядок для БД

# 2. Перевірка: чи збігається введений пароль із хешем з бази
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

# 3. Генерація JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)