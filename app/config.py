from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Твої змінні для майбутнього
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "dbname"

    # --- НАЛАШТУВАННЯ БЕЗПЕКИ ДЛЯ 5 ЛАБИ ---
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGEME_12345"  # Секретний ключ для підпису JWT
    ALGORITHM: str = "HS256"                             # Алгоритм шифрування
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30                # Час життя токена (30 хвилин)

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        # Асинхронний локальний файл SQLite
        return "sqlite+aiosqlite:///./local_vspa.db"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        # Для синхронних перевірок Alembic
        return "sqlite:///./local_vspa.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()