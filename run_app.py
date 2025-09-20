import uvicorn
import asyncio
import logging
from app.core.database import create_db_and_tables
from app.main import app

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Запуск приложения...")

    # Инициализация базы данных
    try:
        await create_db_and_tables()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        return

    # Запуск сервера
    logger.info("🚀 Запуск сервера...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    asyncio.run(main())