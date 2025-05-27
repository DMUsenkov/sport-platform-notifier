import logging
import json
import re
from aiogram import Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated, TelegramAPIError

from config.config import MAX_RPS
from utils.logger import get_logger
from database.models import NotificationType
from database.repositories.notification_repository import NotificationRepository
from api.client import ApiClient
from bot.messages.templates import (
    TEAM_APPLICATION_MESSAGE,
    APPLICATION_CANCEL_MESSAGE,
    CHAMPIONSHIP_CANCEL_MESSAGE,
    NEW_MATCH_MESSAGE,
    MATCH_RESCHEDULE_MESSAGE,
    PLAYOFF_RESULT_MESSAGE,
    MATCH_REMINDER_MESSAGE,
    NEW_CHAMPIONSHIP_MESSAGE,
    COMMITTEE_MESSAGE,
    TEAM_INVITATION_MESSAGE,
    COMMITTEE_INVITATION_MESSAGE
)
from bot.keyboards.keyboards import get_invitation_keyboard

logger = get_logger("notification_handler")
api_client = None


async def send_notification(bot, notification, user):
    """
    Отправка уведомления пользователю

    Args:
        bot: Объект бота Telegram
        notification: Объект уведомления
        user: Объект пользователя

    Returns:
        bool: True, если уведомление успешно отправлено, иначе False
    """
    if not user.telegram_id:
        logger.warning(f"Пользователь {user.id} не имеет привязанного Telegram ID")
        return False

    try:
        metadata = {}
        if notification.metadata_json:
            try:
                metadata = json.loads(notification.metadata_json)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON метаданных для уведомления {notification.id}: {e}")
                logger.error(f"Содержимое metadata_json: {notification.metadata_json}")
                metadata = {}

        message_text = ""
        markup = None

        if notification.type == NotificationType.TEAM_APPLICATION:
            message_text = TEAM_APPLICATION_MESSAGE.format(
                team_name=metadata.get("team_name", "Команда"),
                championship_name=metadata.get("championship_name", "Чемпионат"),
                application_deadline=metadata.get("application_deadline", "Не указан")
            )

        elif notification.type == NotificationType.APPLICATION_CANCEL:
            message_text = APPLICATION_CANCEL_MESSAGE.format(
                status=metadata.get("status", "отклонена"),
                team_name=metadata.get("team_name", "Команда"),
                championship_name=metadata.get("championship_name", "Чемпионат"),
                reason=metadata.get("reason", "Причина не указана")
            )

        elif notification.type == NotificationType.CHAMPIONSHIP_CANCEL:
            message_text = CHAMPIONSHIP_CANCEL_MESSAGE.format(
                status=metadata.get("status", "отменен"),
                championship_name=metadata.get("championship_name", "Чемпионат"),
                additional_info=metadata.get("additional_info", "")
            )

        elif notification.type == NotificationType.NEW_MATCH:
            message_text = NEW_MATCH_MESSAGE.format(
                championship_name=metadata.get("championship_name", "Чемпионат"),
                opponent_name=metadata.get("opponent_name", "Соперник"),
                match_date=metadata.get("match_date", "Дата не указана"),
                match_time=metadata.get("match_time", "Время не указано"),
                venue=metadata.get("venue", "Место не указано"),
                address=metadata.get("address", "Адрес не указан")
            )

        elif notification.type == NotificationType.MATCH_RESCHEDULE:
            message_text = MATCH_RESCHEDULE_MESSAGE.format(
                championship_name=metadata.get("championship_name", "Чемпионат"),
                opponent_name=metadata.get("opponent_name", "Соперник"),
                new_date=metadata.get("new_date", "Новая дата"),
                new_time=metadata.get("new_time", "Новое время"),
                new_venue=metadata.get("new_venue", "Новое место"),
                new_address=metadata.get("new_address", "Новый адрес"),
                old_date=metadata.get("old_date", "Старая дата"),
                old_time=metadata.get("old_time", "Старое время")
            )

        elif notification.type == NotificationType.PLAYOFF_RESULT:
            message_text = PLAYOFF_RESULT_MESSAGE.format(
                team_name=metadata.get("team_name", "Команда"),
                result=metadata.get("result", "прошла"),
                championship_name=metadata.get("championship_name", "Чемпионат"),
                additional_info=metadata.get("additional_info", "")
            )

        elif notification.type == NotificationType.MATCH_REMINDER:
            message_text = MATCH_REMINDER_MESSAGE.format(
                championship_name=metadata.get("championship_name", "Чемпионат"),
                opponent_name=metadata.get("opponent_name", "Соперник"),
                match_date=metadata.get("match_date", "Дата"),
                match_time=metadata.get("match_time", "Время"),
                venue=metadata.get("venue", "Место"),
                address=metadata.get("address", "Адрес")
            )

        elif notification.type == NotificationType.NEW_CHAMPIONSHIP:
            message_text = NEW_CHAMPIONSHIP_MESSAGE.format(
                championship_name=metadata.get("championship_name", "Новый чемпионат"),
                sport_type=metadata.get("sport_type", "Спорт"),
                deadline=metadata.get("deadline", "Дедлайн"),
                city=metadata.get("city", "Город"),
                description=metadata.get("description", "")
            )

        elif notification.type == NotificationType.COMMITTEE_MESSAGE:
            message_text = COMMITTEE_MESSAGE.format(
                championship_name=metadata.get("championship_name", "Чемпионат"),
                message=metadata.get("message", "Сообщение от оргкомитета")
            )

        elif notification.type == NotificationType.TEAM_INVITATION:
            message_text = TEAM_INVITATION_MESSAGE.format(
                team_name=metadata.get("team_name", "Команда"),
                sport_type=metadata.get("sport_type", "Спорт"),
                captain_name=metadata.get("captain_name", "Капитан")
            )
            invitation_id = metadata.get("invitation_id")
            if invitation_id:
                markup = get_invitation_keyboard(invitation_id, "team")
                logger.info(f"Создана клавиатура для приглашения в команду id={invitation_id}")

        elif notification.type == NotificationType.COMMITTEE_INVITATION:
            message_text = COMMITTEE_INVITATION_MESSAGE.format(
                committee_name=metadata.get("committee_name", "Оргкомитет"),
                inviter_name=metadata.get("inviter_name", "Организатор")
            )
            invitation_id = metadata.get("invitation_id")
            if invitation_id:
                markup = get_invitation_keyboard(invitation_id, "committee")
                logger.info(f"Создана клавиатура для приглашения в оргкомитет id={invitation_id}")

        else:
            message_text = f"<b>{notification.title}</b>\n\n{notification.content}"

        if not message_text.strip():
            message_text = f"<b>{notification.title}</b>\n\n{notification.content}"

        await bot.send_message(
            chat_id=user.telegram_id,
            text=message_text,
            reply_markup=markup,
            parse_mode="HTML"
        )

        NotificationRepository.mark_as_sent(notification.id)
        return True

    except BotBlocked:
        logger.warning(f"Бот заблокирован пользователем {user.id}")
        NotificationRepository.mark_as_sent(notification.id)
        return False
    except ChatNotFound:
        logger.warning(f"Чат с пользователем {user.id} не найден")
        NotificationRepository.mark_as_sent(notification.id)
        return False
    except UserDeactivated:
        logger.warning(f"Пользователь {user.id} деактивировал свой аккаунт")
        NotificationRepository.mark_as_sent(notification.id)
        return False
    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при отправке уведомления пользователю {user.id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Необработанная ошибка при отправке уведомления пользователю {user.id}: {e}")
        return False


async def process_pending_notifications(bot):
    """
    Обработка ожидающих отправки уведомлений

    Args:
        bot: Объект бота Telegram
    """
    try:
        notifications_data = NotificationRepository.get_pending_notifications(limit=MAX_RPS)

        if not notifications_data:
            return

        logger.info(f"Найдено {len(notifications_data)} неотправленных уведомлений")

        for item in notifications_data:
            notification_data = item['notification']
            user_data = item['user']

            if not user_data['telegram_id']:
                logger.warning(f"Уведомление {notification_data['id']}: пользователь не имеет Telegram ID")
                NotificationRepository.mark_as_sent(notification_data['id'])
                continue

            class MockNotification:
                def __init__(self, data):
                    self.id = data['id']
                    self.type = data['type']
                    self.title = data['title']
                    self.content = data['content']
                    self.metadata_json = data['metadata_json']

            class MockUser:
                def __init__(self, data):
                    self.id = data['id']
                    self.telegram_id = data['telegram_id']
                    self.first_name = data['first_name']
                    self.last_name = data['last_name']

            mock_notification = MockNotification(notification_data)
            mock_user = MockUser(user_data)

            success = await send_notification(bot, mock_notification, mock_user)
            if success:
                logger.info(
                    f"Уведомление {notification_data['id']} успешно отправлено пользователю {user_data['telegram_id']}")
            else:
                logger.warning(
                    f"Не удалось отправить уведомление {notification_data['id']} пользователю {user_data['telegram_id']}")

    except Exception as e:
        logger.error(f"Ошибка при обработке неотправленных уведомлений: {e}")

def register_notification_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для колбэков от уведомлений

    Args:
        dp: Диспетчер Aiogram
    """
    global api_client
    api_client = ApiClient()

    logger.info("Регистрация обработчиков для уведомлений")

    @dp.message_handler(commands=['invitations'])
    @dp.message_handler(lambda message: message.text == "Приглашения")
    async def my_invitations(message: types.Message):
        """
        Обработчик запроса информации о приглашениях пользователя

        Args:
            message: Сообщение от пользователя
        """
        telegram_id = str(message.from_user.id)
        user = UserRepository.get_by_telegram_id(telegram_id)

        if not user:
            await message.answer(
                "Ваш аккаунт не привязан к боту. Отправьте /start для привязки."
            )
            return

        await message.answer("Ищем ваши приглашения...")

        try:
            user_id = user['id'] if isinstance(user, dict) else user.id

            invitations = await api_client.get_user_invitations(user_id)

            if not invitations:
                await message.answer("У вас нет активных приглашений.")
                return

            await message.answer(f"📨 Найдено {len(invitations)} приглашений:")

            for invitation in invitations:
                try:
                    if invitation['type'] == 'team':
                        markup = get_invitation_keyboard(invitation['invitation_id'], "team")

                        await message.answer(
                            TEAM_INVITATION_MESSAGE.format(
                                team_name=invitation.get('team_name', ''),
                                sport_type=invitation.get('sport', ''),
                                captain_name=invitation.get('inviter_name', '')
                            ),
                            reply_markup=markup
                        )
                    elif invitation['type'] == 'committee':
                        markup = get_invitation_keyboard(invitation['invitation_id'], "committee")

                        await message.answer(
                            COMMITTEE_INVITATION_MESSAGE.format(
                                committee_name=invitation.get('committee_name', ''),
                                inviter_name=invitation.get('inviter_name', '')
                            ),
                            reply_markup=markup
                        )
                except Exception as e:
                    logger.error(f"Ошибка при обработке приглашения: {e}")

        except Exception as e:
            logger.error(f"Ошибка при получении приглашений пользователя {telegram_id}: {e}")
            await message.answer(
                "Произошла ошибка при получении информации о приглашениях. Пожалуйста, попробуйте позже."
            )