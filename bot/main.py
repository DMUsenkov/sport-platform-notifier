import asyncio
import logging
import sys
import datetime
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config.config import TELEGRAM_BOT_TOKEN
from utils.logger import setup_logger
from database.connection import init_db
from bot.handlers.user import register_user_handlers
from bot.handlers.notification import register_notification_handlers, process_pending_notifications
from bot.handlers.match import register_match_handlers
from bot.handlers.championship import register_championship_handlers
from bot.handlers.callback_handlers import register_callback_handlers
from database.repositories.notification_repository import NotificationRepository

logger = setup_logger("bot")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_callback_handlers(dp)
register_user_handlers(dp)
register_notification_handlers(dp)
register_match_handlers(dp)
register_championship_handlers(dp)

background_tasks_running = False


async def check_notifications_periodically():
    while background_tasks_running:
        try:
            await process_pending_notifications(bot)

            now = datetime.datetime.now()
            if now.hour == 12 and now.minute == 0:
                count = NotificationRepository.create_match_reminder_notifications()
                logger.info(f"Создано {count} напоминаний о матчах")

            if now.hour == 3 and now.minute == 0:
                count = NotificationRepository.delete_old_sent_notifications(days=30)
                logger.info(f"Удалено {count} старых уведомлений")

        except Exception as e:
            logger.error(f"Ошибка при выполнении фоновых задач: {e}")

        await asyncio.sleep(10)


async def on_startup(dispatcher):
    """
    Функция, выполняемая при запуске бота

    Args:
        dispatcher: Диспетчер Aiogram
    """
    global background_tasks_running
    try:
        init_db()
        logger.info("База данных инициализирована")

        background_tasks_running = True
        asyncio.create_task(check_notifications_periodically())
        logger.info("Фоновая задача проверки уведомлений запущена")

        logger.info("Бот успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)


async def on_shutdown(dispatcher):
    """
    Функция, выполняемая при остановке бота

    Args:
        dispatcher: Диспетчер Aiogram
    """
    global background_tasks_running
    try:
        background_tasks_running = False
        logger.info("Фоновые задачи остановлены")

        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()
        logger.info("Хранилище состояний закрыто")

        logger.info("Бот успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        allowed_updates=['message', 'callback_query']
    )