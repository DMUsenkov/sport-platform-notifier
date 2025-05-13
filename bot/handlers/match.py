from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils.logger import get_logger
from database.repositories.user_repository import UserRepository
from api.client import ApiClient
from bot.keyboards.keyboards import get_start_keyboard

logger = get_logger("match_handler")


class MatchDeclineStates(StatesGroup):
    waiting_for_reason = State()


api_client = None

match_decline_data = {}


def register_match_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для матчей

    Args:
        dp: Диспетчер Aiogram
    """
    global api_client
    api_client = ApiClient()

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('decline_match_'))
    async def decline_match_start(callback_query: types.CallbackQuery, state: FSMContext):
        """
        Обработчик для начала процесса отклонения участия в матче

        Args:
            callback_query: Запрос от кнопки
            state: Состояние FSM
        """
        await callback_query.answer("Отклонение участия в матче...")

        _, _, match_id, team_id = callback_query.data.split('_')
        match_id = int(match_id)
        team_id = int(team_id)

        async with state.proxy() as data:
            data['match_id'] = match_id
            data['team_id'] = team_id

        await callback_query.message.answer(
            "Пожалуйста, укажите причину отклонения участия в матче:"
        )

        await MatchDeclineStates.waiting_for_reason.set()

    @dp.message_handler(state=MatchDeclineStates.waiting_for_reason)
    async def decline_match_finish(message: types.Message, state: FSMContext):
        """
        Обработчик для завершения процесса отклонения участия в матче

        Args:
            message: Сообщение с причиной отклонения
            state: Состояние FSM
        """
        async with state.proxy() as data:
            match_id = data['match_id']
            team_id = data['team_id']

        reason = message.text

        try:
            result = await api_client.decline_match(match_id, team_id, reason)

            if result.get('success'):
                await message.answer(
                    "✅ Вы успешно отклонили участие в матче. Организаторы чемпионата будут уведомлены.",
                    reply_markup=get_start_keyboard()
                )
            else:
                await message.answer(
                    f"❌ Не удалось отклонить участие в матче: {result.get('error', 'неизвестная ошибка')}",
                    reply_markup=get_start_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отклонении участия в матче {match_id}: {e}")
            await message.answer(
                "❌ Произошла ошибка при отклонении участия в матче. Пожалуйста, попробуйте позже.",
                reply_markup=get_start_keyboard()
            )

        await state.finish()