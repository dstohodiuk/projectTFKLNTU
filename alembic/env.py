import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

# Імпортуємо наш конфіг, базовий клас моделей та самі моделі
from app.config import settings
from app.database import Base, engine  # <--- Додали імпорт нашого engine
from app import models 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаємо метадані наших моделей для автогенерації
target_metadata = Base.metadata

# Підставляємо URL бази даних з Pydantic Settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Використовуємо наш готовий асинхронний двигун, який вже знає про новий .env
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())