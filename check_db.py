import asyncio
import asyncpg
from app.core.config import settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def detailed_db_check():
    """Подробная проверка подключения к базе данных"""
    try:
        logger.info("=== Подробная проверка подключения к БД ===")
        logger.info(f"Host: localhost")
        logger.info(f"Port: {settings.POSTGRES_PORT}")
        logger.info(f"User: {settings.POSTGRES_USER}")
        logger.info(f"Database: {settings.POSTGRES_DB}")
        logger.info("========================================")

        # Попытка подключения
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            timeout=30
        )

        # Получаем информацию о подключении
        version = await conn.fetchval("SELECT version()")
        current_database = await conn.fetchval("SELECT current_database()")
        current_user = await conn.fetchval("SELECT current_user")

        logger.info(f"✅ Подключение успешно!")
        logger.info(f"PostgreSQL версия: {version}")
        logger.info(f"Текущая база: {current_database}")
        logger.info(f"Текущий пользователь: {current_user}")

        # Проверяем права пользователя
        try:
            privileges = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.table_privileges 
                WHERE grantee = $1
            """, settings.POSTGRES_USER)
            logger.info(f"Права пользователя: найдено {privileges} привилегий")
        except Exception as priv_error:
            logger.warning(f"Не удалось проверить привилегии: {priv_error}")

        await conn.close()
        return True

    except asyncpg.InvalidPasswordError:
        logger.error("❌ Неверный пароль для пользователя")
        return False
    except asyncpg.InvalidAuthorizationSpecificationError:
        logger.error("❌ Неверные учетные данные")
        return False
    except asyncpg.ConnectionDoesNotExistError:
        logger.error("❌ Сервер PostgreSQL не доступен")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {type(e).__name__}: {e}")
        return False


async def check_postgres_service():
    """Проверяет доступность PostgreSQL сервиса"""
    try:
        # Попытка подключения к системной базе
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres",
            timeout=10
        )
        version = await conn.fetchval("SELECT version()")
        logger.info(f"PostgreSQL сервис доступен: {version}")
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL сервис недоступен: {e}")
        return False


if __name__ == "__main__":
    logger.info("Запуск диагностики подключения к базе данных...")

    # Проверяем доступность PostgreSQL
    if not asyncio.run(check_postgres_service()):
        logger.error("PostgreSQL сервис не доступен. Проверьте:")
        logger.error("1. Запущен ли PostgreSQL сервис")
        logger.error("2. Правильный ли порт указан (обычно 5432)")
        logger.error("3. Правильные ли учетные данные")
    else:
        # Подробная проверка
        success = asyncio.run(detailed_db_check())
        if success:
            print("\n🎉 Диагностика пройдена успешно!")
        else:
            print("\n❌ Диагностика выявила проблемы!")
            print("Проверьте настройки в файле .env")