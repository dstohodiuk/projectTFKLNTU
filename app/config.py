from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Зберігаємо твої змінні для майбутнього, коли Docker оживе
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "dbname"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        # Переходимо на асинхронний локальний файл SQLite
        return "sqlite+aiosqlite:///./local_vspa.db"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        # Для синхронних перевірок Alembic
        return "sqlite:///./local_vspa.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()