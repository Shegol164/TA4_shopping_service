import asyncio
import asyncpg
from app.core.config import settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_db_connection():
    try:
        logger.info("Попытка подключения к базе данных...")
        logger.info(
            f"URL: postgresql://{settings.POSTGRES_USER}:***@localhost:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")

        # Попытка подключения к базе данных
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        version = await conn.fetchval("SELECT version()")
        logger.info(f"✅ Успешное подключение к базе данных!")
        logger.info(f"Версия PostgreSQL: {version}")
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False


async def create_test_user():
    """Создает тестового пользователя для проверки"""
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

        # Проверим существование таблиц
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        logger.info(f"Существующие таблицы: {[table['tablename'] for table in tables]}")

        await conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при работе с базой данных: {e}")
        return False


if __name__ == "__main__":
    print("Проверка подключения к базе данных...")
    result = asyncio.run(check_db_connection())
    if result:
        print("✅ Подключение успешно!")
        print("Проверка таблиц...")
        asyncio.run(create_test_user())
    else:
        print("❌ Не удалось подключиться к базе данных")