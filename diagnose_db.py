import asyncio
import asyncpg
import psycopg2
from app.core.config import settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def diagnose_postgres_async():
    """Диагностика PostgreSQL через asyncpg"""
    logger.info("=== Диагностика PostgreSQL (асинхронная) ===")

    try:
        logger.info(f"Попытка подключения к PostgreSQL...")
        logger.info(f"Хост: localhost:{settings.POSTGRES_PORT}")
        logger.info(f"Пользователь: {settings.POSTGRES_USER}")
        logger.info(f"База данных: {settings.POSTGRES_DB}")

        # Попытка подключения
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            timeout=10
        )

        version = await conn.fetchval("SELECT version()")
        logger.info(f"✅ Успешное подключение!")
        logger.info(f"Версия PostgreSQL: {version}")

        # Проверим существующие таблицы
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        logger.info(f"Существующие таблицы: {[table['table_name'] for table in tables]}")

        await conn.close()
        return True

    except asyncpg.InvalidPasswordError:
        logger.error("❌ Неверный пароль пользователя")
        return False
    except asyncpg.UndefinedTableError:
        logger.error("❌ Таблица не найдена")
        return False
    except asyncpg.ConnectionDoesNotExistError:
        logger.error("❌ Сервис PostgreSQL не запущен")
        return False
    except ConnectionRefusedError:
        logger.error("❌ Отказано в подключении - PostgreSQL не запущен")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {type(e).__name__}: {e}")
        return False


def diagnose_postgres_sync():
    """Диагностика PostgreSQL через psycopg2"""
    logger.info("=== Диагностика PostgreSQL (синхронная) ===")

    try:
        logger.info(f"Попытка синхронного подключения...")
        conn = psycopg2.connect(
            host="localhost",
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        logger.info(f"✅ Успешное синхронное подключение!")
        logger.info(f"Версия PostgreSQL: {version}")

        cur.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        logger.error(f"❌ Ошибка операции: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка синхронного подключения: {type(e).__name__}: {e}")
        return False


async def check_postgres_service():
    """Проверка доступности PostgreSQL сервиса"""
    logger.info("=== Проверка доступности PostgreSQL сервиса ===")

    try:
        # Попробуем подключиться к системной базе postgres
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres",
            timeout=5
        )

        logger.info("✅ PostgreSQL сервис доступен")
        await conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ PostgreSQL сервис недоступен: {type(e).__name__}: {e}")
        return False


async def main():
    logger.info("Начало диагностики PostgreSQL...")

    # Проверим сервис
    service_ok = await check_postgres_service()

    if service_ok:
        # Проверим конкретную базу данных
        async_ok = await diagnose_postgres_async()
        sync_ok = diagnose_postgres_sync()

        if async_ok and sync_ok:
            logger.info("✅ Все проверки пройдены успешно!")
        else:
            logger.warning("⚠️  Сервис работает, но есть проблемы с подключением к базе данных")
    else:
        logger.error("❌ PostgreSQL сервис не запущен или недоступен")
        logger.info("Попробуйте:")
        logger.info("1. Запустить PostgreSQL сервис")
        logger.info("2. Проверить настройки в файле .env")
        logger.info("3. Убедиться, что порт 5432 не занят другим приложением")


if __name__ == "__main__":
    asyncio.run(main())