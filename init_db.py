import asyncio
from app.core.database import create_db_and_tables
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def init():
    logger.info("Инициализация базы данных...")
    try:
        await create_db_and_tables()
        logger.info("✅ База данных инициализирована успешно!")
        logger.info("Теперь можно запустить приложение: uvicorn app.main:app --reload")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        logger.info("Попробуйте:")
        logger.info("1. Запустить diagnose_db.py для диагностики")
        logger.info("2. Запустить create_db.py для создания базы")
        logger.info("3. Проверить, запущен ли PostgreSQL сервис")

if __name__ == "__main__":
    asyncio.run(init())