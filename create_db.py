import asyncio
import asyncpg
import psycopg2
from app.core.config import settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def create_database():
    """Создание базы данных через системную базу postgres"""
    logger.info("=== Создание базы данных ===")

    try:
        # Подключаемся к системной базе postgres для создания новой базы
        logger.info("Подключение к системной базе postgres...")
        conn = await asyncpg.connect(
            host="localhost",
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres"  # Системная база
        )

        # Проверим, существует ли база данных
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.POSTGRES_DB
        )

        if result:
            logger.info(f"База данных '{settings.POSTGRES_DB}' уже существует")
        else:
            # Создаем базу данных
            logger.info(f"Создание базы данных '{settings.POSTGRES_DB}'...")
            await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            logger.info(f"✅ База данных '{settings.POSTGRES_DB}' создана успешно!")

        await conn.close()
        return True

    except asyncpg.InvalidPasswordError:
        logger.error("❌ Неверный пароль пользователя PostgreSQL")
        logger.info("Проверьте настройки в файле .env")
        return False
    except ConnectionRefusedError:
        logger.error("❌ Отказано в подключении - PostgreSQL не запущен")
        logger.info("Запустите PostgreSQL сервис и повторите попытку")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка создания базы данных: {type(e).__name__}: {e}")
        return False


def create_user_if_not_exists():
    """Создание пользователя если он не существует"""
    logger.info("=== Проверка/создание пользователя ===")

    try:
        # Подключаемся к системной базе как суперпользователь
        conn = psycopg2.connect(
            host="localhost",
            port=settings.POSTGRES_PORT,
            user="postgres",  # Стандартный суперпользователь
            password="postgres",  # Пароль суперпользователя (измените при необходимости)
            database="postgres"
        )

        cur = conn.cursor()

        # Проверим существование пользователя
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (settings.POSTGRES_USER,))
        user_exists = cur.fetchone()

        if not user_exists:
            logger.info(f"Создание пользователя '{settings.POSTGRES_USER}'...")
            cur.execute(f"CREATE USER {settings.POSTGRES_USER} WITH PASSWORD %s", (settings.POSTGRES_PASSWORD,))
            logger.info(f"✅ Пользователь '{settings.POSTGRES_USER}' создан")
        else:
            logger.info(f"Пользователь '{settings.POSTGRES_USER}' уже существует")

        # Дадим права на базу данных
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {settings.POSTGRES_DB} TO {settings.POSTGRES_USER}")
        logger.info(f"Права на базу данных выданы пользователю '{settings.POSTGRES_USER}'")

        cur.close()
        conn.commit()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        logger.warning(f"Не удалось подключиться как суперпользователь: {e}")
        logger.info("Пропуск создания пользователя - попробуйте создать вручную")
        return False
    except Exception as e:
        logger.error(f"Ошибка при работе с пользователем: {type(e).__name__}: {e}")
        return False


async def main():
    logger.info("Начало процесса создания базы данных...")

    # Попробуем создать пользователя (если есть права)
    create_user_if_not_exists()

    # Создаем базу данных
    success = await create_database()

    if success:
        logger.info("✅ Процесс завершен успешно!")
        logger.info("Теперь можно запустить init_db.py")
    else:
        logger.error("❌ Процесс завершен с ошибками")
        logger.info("Проверьте:")
        logger.info("1. Запущен ли PostgreSQL сервис")
        logger.info("2. Правильность учетных данных в .env")
        logger.info("3. Достаточно ли прав у пользователя")


if __name__ == "__main__":
    asyncio.run(main())