import logging
import sys
from logging.handlers import RotatingFileHandler
import os

from config.config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name="sports_platform_notifier"):
    """
    Настройка логирования для приложения

    Args:
        name: Имя логгера

    Returns:
        Настроенный объект логгера
    """
    logger = logging.getLogger(name)

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logs_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, f"{name}.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name=None):
    """
    Получение логгера для компонента приложения

    Args:
        name: Имя компонента (опционально)

    Returns:
        Объект логгера
    """
    if name:
        return logging.getLogger(f"sports_platform_notifier.{name}")
    return logging.getLogger("sports_platform_notifier")