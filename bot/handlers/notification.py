import logging
import json
from aiogram import Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated, TelegramAPIError

from config.config import MAX_RPS
from utils.logger import get_logger
from database.models import NotificationType
from database.repositories.notification_repository import NotificationRepository
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
    telegram_id = user.telegram_id if hasattr(user, 'telegram_id') else user.get('telegram_id')

    if not telegram_id:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.warning(f"Пользователь {user_id} не имеет привязанного Telegram ID")
        return False

    try:
        metadata_json = notification.metadata_json if hasattr(notification, 'metadata_json') else notification.get(
            'metadata_json')
        metadata = json.loads(metadata_json) if metadata_json else {}

        notification_type = notification.type if hasattr(notification, 'type') else notification.get('type')

        message_text = ""
        markup = None

        if notification_type == NotificationType.TEAM_APPLICATION:
            message_text = TEAM_APPLICATION_MESSAGE.format(
                team_name=metadata.get("team_name", ""),
                championship_name=metadata.get("championship_name", ""),
                application_deadline=metadata.get("application_deadline", "")
            )

        elif notification_type == NotificationType.APPLICATION_CANCEL:
            message_text = APPLICATION_CANCEL_MESSAGE.format(
                status=metadata.get("status", "отклонена"),
                team_name=metadata.get("team_name", ""),
                championship_name=metadata.get("championship_name", ""),
                reason=metadata.get("reason", "Причина не указана")
            )

        elif notification_type == NotificationType.CHAMPIONSHIP_CANCEL:
            message_text = CHAMPIONSHIP_CANCEL_MESSAGE.format(
                status=metadata.get("status", "отменен"),
                championship_name=metadata.get("championship_name", ""),
                additional_info=metadata.get("additional_info", "")
            )

        elif notification_type == NotificationType.NEW_MATCH:
            message_text = NEW_MATCH_MESSAGE.format(
                championship_name=metadata.get("championship_name", ""),
                opponent_name=metadata.get("opponent_name", ""),
                match_date=metadata.get("match_date", ""),
                match_time=metadata.get("match_time", ""),
                venue=metadata.get("venue", ""),
                address=metadata.get("address", "")
            )

        elif notification_type == NotificationType.MATCH_RESCHEDULE:
            message_text = MATCH_RESCHEDULE_MESSAGE.format(
                championship_name=metadata.get("championship_name", ""),
                opponent_name=metadata.get("opponent_name", ""),
                new_date=metadata.get("new_date", ""),
                new_time=metadata.get("new_time", ""),
                new_venue=metadata.get("new_venue", ""),
                new_address=metadata.get("new_address", ""),
                old_date=metadata.get("old_date", ""),
                old_time=metadata.get("old_time", "")
            )

        elif notification_type == NotificationType.PLAYOFF_RESULT:
            message_text = PLAYOFF_RESULT_MESSAGE.format(
                team_name=metadata.get("team_name", ""),
                result=metadata.get("result", "прошла"),
                championship_name=metadata.get("championship_name", ""),
                additional_info=metadata.get("additional_info", "")
            )

        elif notification_type == NotificationType.MATCH_REMINDER:
            message_text = MATCH_REMINDER_MESSAGE.format(
                championship_name=metadata.get("championship_name", ""),
                opponent_name=metadata.get("opponent_name", ""),
                match_date=metadata.get("match_date", ""),
                match_time=metadata.get("match_time", ""),
                venue=metadata.get("venue", ""),
                address=metadata.get("address", "")
            )

        elif notification_type == NotificationType.NEW_CHAMPIONSHIP:
            message_text = NEW_CHAMPIONSHIP_MESSAGE.format(
                championship_name=metadata.get("championship_name", ""),
                sport_type=metadata.get("sport_type", ""),
                deadline=metadata.get("deadline", ""),
                city=metadata.get("city", ""),
                description=metadata.get("description", "")
            )

        elif notification_type == NotificationType.COMMITTEE_MESSAGE:
            message_text = COMMITTEE_MESSAGE.format(
                championship_name=metadata.get("championship_name", ""),
                message=metadata.get("message", "")
            )

        elif notification_type == NotificationType.TEAM_INVITATION:
            message_text = TEAM_INVITATION_MESSAGE.format(
                team_name=metadata.get("team_name", ""),
                sport_type=metadata.get("sport_type", ""),
                captain_name=metadata.get("captain_name", "")
            )
            invitation_id = metadata.get("invitation_id")
            if invitation_id:
                markup = get_invitation_keyboard(invitation_id, "team")

        elif notification_type == NotificationType.COMMITTEE_INVITATION:
            message_text = COMMITTEE_INVITATION_MESSAGE.format(
                committee_name=metadata.get("committee_name", ""),
                inviter_name=metadata.get("inviter_name", "")
            )
            invitation_id = metadata.get("invitation_id")
            if invitation_id:
                markup = get_invitation_keyboard(invitation_id, "committee")

        else:
            content = notification.content if hasattr(notification, 'content') else notification.get('content', '')
            message_text = content

        await bot.send_message(
            chat_id=telegram_id,
            text=message_text,
            reply_markup=markup,
            parse_mode="HTML"
        )

        notification_id = notification.id if hasattr(notification, 'id') else notification.get('id')
        if notification_id:
            NotificationRepository.mark_as_sent(notification_id)

        return True

    except BotBlocked:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.warning(f"Бот заблокирован пользователем {user_id}")
        return False
    except ChatNotFound:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.warning(f"Чат с пользователем {user_id} не найден")
        return False
    except UserDeactivated:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.warning(f"Пользователь {user_id} деактивировал свой аккаунт")
        return False
    except TelegramAPIError as e:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.error(f"Ошибка Telegram API при отправке уведомления пользователю {user_id}: {e}")
        return False
    except Exception as e:
        user_id = user.id if hasattr(user, 'id') else user.get('id', 'unknown')
        logger.error(f"Необработанная ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False


async def process_pending_notifications(bot):
    """
    Обработка ожидающих отправки уведомлений

    Args:
        bot: Объект бота Telegram
    """
    try:
        notifications = NotificationRepository.get_pending_notifications(limit=MAX_RPS)

        if not notifications:
            return

        logger.info(f"Найдено {len(notifications)} неотправленных уведомлений")

        for notification in notifications:
            user = notification.user
            if not user or not user.telegram_id:
                logger.warning(f"Уведомление {notification.id}: пользователь не найден или не имеет Telegram ID")
                NotificationRepository.mark_as_sent(notification.id)
                continue

            await send_notification(bot, notification, user)

    except Exception as e:
        logger.error(f"Ошибка при обработке неотправленных уведомлений: {e}")


def register_notification_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для колбэков от уведомлений

    Args:
        dp: Диспетчер Aiogram
    """

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_team_'))
    async def accept_team_invitation(callback_query: types.CallbackQuery):
        await callback_query.answer("Вы приняли приглашение в команду!")
        invitation_id = int(callback_query.data.split('_')[2])
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n\n✅ Вы приняли приглашение!",
            reply_markup=None
        )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_team_'))
    async def decline_team_invitation(callback_query: types.CallbackQuery):
        await callback_query.answer("Вы отклонили приглашение в команду!")
        invitation_id = int(callback_query.data.split('_')[2])
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение!",
            reply_markup=None
        )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_committee_'))
    async def accept_committee_invitation(callback_query: types.CallbackQuery):
        await callback_query.answer("Вы приняли приглашение в оргкомитет!")
        invitation_id = int(callback_query.data.split('_')[2])
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n\n✅ Вы приняли приглашение!",
            reply_markup=None
        )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_committee_'))
    async def decline_committee_invitation(callback_query: types.CallbackQuery):
        await callback_query.answer("Вы отклонили приглашение в оргкомитет!")
        invitation_id = int(callback_query.data.split('_')[2])
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение!",
            reply_markup=None
        )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_team_'))
    async def accept_team_invitation(callback_query: types.CallbackQuery):
        """
        Обработчик для принятия приглашения в команду

        Args:
            callback_query: Запрос от кнопки
        """
        await callback_query.answer("Обрабатываем ваше решение...")

        invitation_id = int(callback_query.data.split('_')[2])

        try:
            result = await api_client.accept_team_invitation(invitation_id)

            if result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n✅ Вы приняли приглашение! Вы теперь участник команды {result.get('team_name', '')}.",
                    reply_markup=None
                )
            else:
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось принять приглашение: {result.get('error', 'неизвестная ошибка')}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при принятии приглашения в команду {invitation_id}: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_team_'))
    async def decline_team_invitation(callback_query: types.CallbackQuery):
        """
        Обработчик для отклонения приглашения в команду

        Args:
            callback_query: Запрос от кнопки
        """
        await callback_query.answer("Обрабатываем ваше решение...")

        invitation_id = int(callback_query.data.split('_')[2])

        try:
            result = await api_client.decline_team_invitation(invitation_id)

            if result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение.",
                    reply_markup=None
                )
            else:
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось отклонить приглашение: {result.get('error', 'неизвестная ошибка')}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при отклонении приглашения в команду {invitation_id}: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_committee_'))
    async def accept_committee_invitation(callback_query: types.CallbackQuery):
        """
        Обработчик для принятия приглашения в оргкомитет

        Args:
            callback_query: Запрос от кнопки
        """
        await callback_query.answer("Обрабатываем ваше решение...")

        invitation_id = int(callback_query.data.split('_')[2])

        try:
            result = await api_client.accept_committee_invitation(invitation_id)

            if result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n✅ Вы приняли приглашение! Вы теперь член оргкомитета {result.get('committee_name', '')}.",
                    reply_markup=None
                )
            else:
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось принять приглашение: {result.get('error', 'неизвестная ошибка')}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при принятии приглашения в оргкомитет {invitation_id}: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_committee_'))
    async def decline_committee_invitation(callback_query: types.CallbackQuery):
        """
        Обработчик для отклонения приглашения в оргкомитет

        Args:
            callback_query: Запрос от кнопки
        """
        await callback_query.answer("Обрабатываем ваше решение...")

        invitation_id = int(callback_query.data.split('_')[2])

        try:
            result = await api_client.decline_committee_invitation(invitation_id)

            if result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение.",
                    reply_markup=None
                )
            else:
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось отклонить приглашение: {result.get('error', 'неизвестная ошибка')}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при отклонении приглашения в оргкомитет {invitation_id}: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )