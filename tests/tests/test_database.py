# tests/test_database.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


@pytest.mark.asyncio
async def test_database_connection():
    """Тест подключения к базе данных"""
    try:
        engine = create_async_engine(
            settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
            echo=False
        )

        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            assert result.scalar() == 1

        await engine.dispose()
        assert True
    except Exception as e:
        pytest.fail(f"Не удалось подключиться к базе данных: {e}")


@pytest.mark.asyncio
async def test_database_creation():
    """Тест создания таблиц"""
    from app.core.database import create_db_and_tables
    try:
        await create_db_and_tables()
        assert True
    except Exception as e:
        pytest.fail(f"Ошибка создания таблиц: {e}")