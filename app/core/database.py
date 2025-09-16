from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_engine_with_retry():
    """Создает движок с обработкой ошибок и повторными попытками"""
    try:
        # URL для подключения
        db_url = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
        logger.info(f"Попытка подключения к: {db_url}")

        engine = create_async_engine(
            db_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=30,
            connect_args={
                "server_settings": {
                    "statement_timeout": "30000",
                    "idle_in_transaction_session_timeout": "30000"
                },
                "command_timeout": 30
            }
        )
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Error creating database engine: {e}")
        raise


# Создание движка
try:
    engine = create_engine_with_retry()
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None

if engine:
    # Создание асинхронной сессии
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    AsyncSessionLocal = None

Base = declarative_base()


async def get_db():
    if not AsyncSessionLocal:
        raise Exception("Database engine not initialized")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables(max_retries=3, retry_delay=2):
    """Создает таблицы с повторными попытками"""
    if not engine:
        raise Exception("Database engine not initialized")

    for attempt in range(max_retries):
        try:
            logger.info(f"Попытка {attempt + 1} создания таблиц...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Таблицы созданы успешно")
            return
        except Exception as e:
            logger.error(f"Попытка {attempt + 1} не удалась: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Ожидание {retry_delay} секунд перед повторной попыткой...")
                await asyncio.sleep(retry_delay)
            else:
                raise Exception(f"Не удалось создать таблицы после {max_retries} попыток: {e}")