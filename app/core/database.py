from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Создание асинхронного движка с расширенной обработкой ошибок
def create_engine_with_retry():
    try:
        db_url = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
        logger.info(f"Попытка подключения к: {db_url}")

        engine = create_async_engine(
            db_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "timeout": 30,
                "command_timeout": 30,
            }
        )
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Error creating database engine: {e}")
        raise


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
        raise Exception("Database engine is not available")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_connection():
    """Тест подключения к базе данных"""
    if not engine:
        logger.error("Database engine is not initialized")
        return False

    try:
        async with engine.connect() as conn:
            # Используем text() для SQL выражений
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


async def create_db_and_tables(max_retries=3):
    if not engine:
        logger.warning("Database engine is not available, skipping table creation")
        return

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to create database tables...")
            # Сначала проверим подключение
            if not await test_connection():
                raise Exception("Database connection failed")

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            return
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Подождем перед повторной попыткой
            else:
                logger.error("Failed to create database tables after all retries")
                raise