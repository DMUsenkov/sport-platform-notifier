import logging
from aiogram import Dispatcher, types

from utils.logger import get_logger
from api.client import ApiClient

logger = get_logger("callback_handlers")
api_client = None


def register_callback_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для колбэков инлайн-кнопок

    Args:
        dp: Диспетчер Aiogram
    """
    global api_client
    api_client = ApiClient()

    @dp.callback_query_handler(lambda c: c.data == 'about')
    async def help_about_callback(callback_query: types.CallbackQuery):
        await callback_query.answer()
        await callback_query.message.reply(
            "О боте:\n\n"
            "Этот бот предназначен для отправки уведомлений пользователям онлайн-платформы "
            "для поиска и управления любительскими спортивными соревнованиями.\n\n"
            "Через этот бот вы будете получать актуальную информацию о чемпионатах, "
            "матчах и командах, в которых вы участвуете."
        )

    @dp.callback_query_handler(lambda c: c.data == 'types')
    async def help_notification_types_callback(callback_query: types.CallbackQuery):
        await callback_query.answer()
        await callback_query.message.reply(
            "Типы уведомлений:\n\n"
            "• Заявки на участие в чемпионатах\n"
            "• Отмена или отклонение заявок\n"
            "• Отмена или завершение чемпионатов\n"
            "• Назначение новых матчей\n"
            "• Перенос матчей\n"
            "• Результаты прохождения в плей-офф\n"
            "• Напоминания о матчах\n"
            "• Новые интересные чемпионаты\n"
            "• Сообщения от оргкомитетов\n"
            "• Приглашения в команды\n"
            "• Приглашения в оргкомитеты"
        )

    @dp.callback_query_handler(lambda c: c.data == 'phone')
    async def help_change_phone_callback(callback_query: types.CallbackQuery):
        await callback_query.answer()
        await callback_query.message.reply(
            "Как привязать другой номер телефона:\n\n"
            "1. Отправьте команду /changephone\n"
            "2. Введите новый номер телефона или отправьте контакт\n"
            "3. Ваш аккаунт будет привязан к новому номеру телефона\n\n"
            "Обратите внимание, что номер телефона должен быть зарегистрирован в системе."
        )

    @dp.callback_query_handler(lambda c: c.data == 'support')
    async def help_support_callback(callback_query: types.CallbackQuery):
        await callback_query.answer()
        await callback_query.message.reply(
            "Связаться с поддержкой:\n\n"
            "По всем вопросам, связанным с работой бота или платформы, "
            "пожалуйста, обращайтесь по адресу электронной почты:\n"
            "support@sports-platform.ru\n\n"
            "Или позвоните нам по телефону:\n"
            "+7 (800) 123-45-67"
        )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_team_'))
    async def accept_team_invitation_callback(callback_query: types.CallbackQuery):
        await callback_query.answer("Обрабатываем ваше решение...")

        try:
            invitation_id = int(callback_query.data.split('_')[2])

            result = await api_client.accept_team_invitation(invitation_id)

            if result and result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n✅ Вы приняли приглашение! Вы теперь участник команды {result.get('team_name', '')}.",
                    reply_markup=None
                )
            else:
                error_msg = result.get('error', 'неизвестная ошибка') if result else 'нет ответа от API'
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось принять приглашение: {error_msg}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке принятия приглашения в команду: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_team_'))
    async def decline_team_invitation_callback(callback_query: types.CallbackQuery):
        await callback_query.answer("Обрабатываем ваше решение...")

        try:
            invitation_id = int(callback_query.data.split('_')[2])

            result = await api_client.decline_team_invitation(invitation_id)

            if result and result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение.",
                    reply_markup=None
                )
            else:
                error_msg = result.get('error', 'неизвестная ошибка') if result else 'нет ответа от API'
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось отклонить приглашение: {error_msg}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке отклонения приглашения в команду: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('accept_committee_'))
    async def accept_committee_invitation_callback(callback_query: types.CallbackQuery):
        await callback_query.answer("Обрабатываем ваше решение...")

        try:
            invitation_id = int(callback_query.data.split('_')[2])

            result = await api_client.accept_committee_invitation(invitation_id)

            if result and result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n✅ Вы приняли приглашение! Вы теперь член оргкомитета {result.get('committee_name', '')}.",
                    reply_markup=None
                )
            else:
                error_msg = result.get('error', 'неизвестная ошибка') if result else 'нет ответа от API'
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось принять приглашение: {error_msg}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке принятия приглашения в оргкомитет: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_committee_'))
    async def decline_committee_invitation_callback(callback_query: types.CallbackQuery):
        await callback_query.answer("Обрабатываем ваше решение...")

        try:
            invitation_id = int(callback_query.data.split('_')[2])

            result = await api_client.decline_committee_invitation(invitation_id)

            if result and result.get('success'):
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Вы отклонили приглашение.",
                    reply_markup=None
                )
            else:
                error_msg = result.get('error', 'неизвестная ошибка') if result else 'нет ответа от API'
                await callback_query.message.edit_text(
                    f"{callback_query.message.text}\n\n❌ Не удалось отклонить приглашение: {error_msg}",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке отклонения приглашения в оргкомитет: {e}")
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n❌ Произошла ошибка при обработке приглашения. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )