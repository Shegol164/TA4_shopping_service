import asyncio
import asyncpg
from app.core.config import settings
from app.core.database import create_db_and_tables
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Тест подключения к базе данных"""
    try:
        logger.info("Тестирование подключения к базе данных...")
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        version = await conn.fetchval("SELECT version()")
        logger.info(f"✅ Подключение успешно! PostgreSQL версия: {version}")
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {e}")
        return False


async def create_database_if_not_exists():
    """Создает базу данных если она не существует"""
    try:
        # Попробуем подключиться к целевой базе
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        await conn.close()
        logger.info(f"База данных '{settings.POSTGRES_DB}' уже существует")
        return True
    except asyncpg.InvalidCatalogNameError:
        # База не существует, создаем её
        logger.info(f"База данных '{settings.POSTGRES_DB}' не найдена, создаем...")
        try:
            # Подключаемся к системной базе для создания новой
            sys_conn = await asyncpg.connect(
                host="localhost",
                port=int(settings.POSTGRES_PORT),
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database="postgres"
            )
            await sys_conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            await sys_conn.close()
            logger.info("✅ База данных создана успешно!")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания базы данных: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка проверки существования базы: {e}")
        return False


async def init():
    logger.info("Инициализация базы данных...")

    # Проверяем и создаем базу данных если нужно
    if not await create_database_if_not_exists():
        logger.error("Не удалось создать или подключиться к базе данных")
        return

    # Тестируем подключение
    if not await test_database_connection():
        logger.error("Не удалось подключиться к базе данных")
        return

    # Создаем таблицы
    logger.info("Создание таблиц...")
    try:
        await create_db_and_tables()
        logger.info("✅ База данных инициализирована успешно!")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")


if __name__ == "__main__":
    asyncio.run(init())