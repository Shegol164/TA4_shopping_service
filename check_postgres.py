import socket
import subprocess
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_port_open(host, port):
    """Проверяет, открыт ли порт"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Ошибка проверки порта: {e}")
        return False


def check_postgres_service():
    """Проверяет статус службы PostgreSQL в Windows"""
    try:
        # Проверяем через sc query (Windows)
        result = subprocess.run(['sc', 'query', 'postgresql'],
                                capture_output=True, text=True, timeout=10)
        if 'RUNNING' in result.stdout:
            logger.info("✅ Служба PostgreSQL запущена")
            return True
        elif 'STOPPED' in result.stdout:
            logger.info("❌ Служба PostgreSQL остановлена")
            return False
        else:
            logger.info("❓ Служба PostgreSQL не найдена")
            return False
    except Exception as e:
        logger.error(f"Ошибка проверки службы: {e}")
        return False


def start_postgres_service():
    """Пытается запустить службу PostgreSQL"""
    try:
        logger.info("Попытка запустить службу PostgreSQL...")
        result = subprocess.run(['net', 'start', 'postgresql'],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logger.info("✅ Служба PostgreSQL запущена успешно")
            time.sleep(5)  # Даем время на полный запуск
            return True
        else:
            logger.error(f"❌ Не удалось запустить службу PostgreSQL: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Ошибка запуска службы: {e}")
        return False


def main():
    port = "5432"
    host = "localhost"

    logger.info("Проверка PostgreSQL...")

    # Проверяем порт
    if is_port_open(host, port):
        logger.info("✅ Порт 5432 открыт")
    else:
        logger.info("❌ Порт 5432 закрыт")

        # Проверяем службу
        if check_postgres_service():
            logger.info("Служба запущена, но порт недоступен")
        else:
            # Пытаемся запустить службу
            if start_postgres_service():
                # Проверяем порт снова
                time.sleep(5)
                if is_port_open(host, port):
                    logger.info("✅ Порт 5432 теперь открыт")
                else:
                    logger.error("❌ Порт 5432 по-прежнему закрыт")
            else:
                logger.error("❌ Не удалось запустить PostgreSQL")
                logger.info("Пожалуйста, запустите PostgreSQL вручную")
                return False

    return True


if __name__ == "__main__":
    main()