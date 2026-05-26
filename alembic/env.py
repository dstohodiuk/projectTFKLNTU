import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

# Імпортуємо наш конфіг та базовий клас моделей
from app.config import settings
from app.database import Base

# Зчитуємо конфігурацію Alembic
config = context.config

# Налаштовуємо логування, якщо конфіг-файл існує
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Підключаємо метадані моделей
target_metadata = Base.metadata

# --- ДІАГНОСТИКА ТА ХАК ---
raw_url = str(settings.DATABASE_URL_SYNC)
print(f"\n[DEBUG] Початковий URL з конфігу: {raw_url}\n")

# Примусово чистимо і збираємо асинхронний URL, якщо у твоєму файлі config.py
# використовується звичайний формат або Pydantic PostgresDsn
if "postgresql+asyncpg://" not in raw_url:
    if "postgresql://" in raw_url:
        final_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif "postgres://" in raw_url:
        final_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    else:
        # Якщо там взагалі якийсь кастомний рядок, силою ліпимо префікс
        final_url = f"postgresql+asyncpg://{raw_url.split('://')[-1]}"
else:
    final_url = raw_url

print(f"\n[DEBUG] Модифікований URL для Alembic: {final_url}\n")

# Прописуємо в конфіг Alembic виключно асинхронний URL
config.set_main_option("sqlalchemy.url", final_url)


def run_migrations_offline() -> None:
    """Запуск міграцій в offline режимі."""
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
    """Фактичне виконання міграцій всередині транзакції."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск міграцій в online режимі за допомогою асинхронного драйвера asyncpg."""
    from sqlalchemy.ext.asyncio import create_async_engine

    target_url = config.get_main_option("sqlalchemy.url")
    print(f"\n[DEBUG] URL безпосередньо в create_async_engine: {target_url}\n")

    connectable = create_async_engine(
        target_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())