from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils.logger import get_logger
from database.repositories.user_repository import UserRepository
from api.client import ApiClient
from bot.keyboards.keyboards import get_championship_menu_keyboard

logger = get_logger("championship_handler")

api_client = None


def register_championship_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для чемпионатов

    Args:
        dp: Диспетчер Aiogram
    """
    global api_client
    api_client = ApiClient()

    @dp.message_handler(lambda message: message.text == "Рекомендуемые чемпионаты")
    async def recommended_championships(message: types.Message):
        """
        Обработчик запроса информации о рекомендуемых чемпионатах

        Args:
            message: Сообщение от пользователя
        """
        user = UserRepository.get_by_telegram_id(str(message.from_user.id))
        if not user:
            await message.answer(
                "Ваш аккаунт не привязан к боту. Отправьте /start для привязки."
            )
            return

        try:
            user_id = user.id if hasattr(user, 'id') else user.get('id')

            if not user_id:
                await message.answer(
                    "Не удалось определить ID пользователя. Пожалуйста, попробуйте заново привязать аккаунт, отправив /start.",
                    reply_markup=get_championship_menu_keyboard()
                )
                return

            championships = await api_client.get_recommended_championships(user_id)

            if not championships:
                await message.answer(
                    "На данный момент у нас нет рекомендаций для вас. Пожалуйста, проверьте позже.",
                    reply_markup=get_championship_menu_keyboard()
                )
                return

            await message.answer(
                "🏆 Вот чемпионаты, которые могут вас заинтересовать:",
                reply_markup=get_championship_menu_keyboard()
            )

            for championship in championships:
                description = championship.get('description', '')
                if len(description) > 200:
                    description = description[:197] + "..."

                response = f"🏆 *{championship['name']}*\n\n"
                response += f"⚽ Вид спорта: {championship['sport']}\n"
                response += f"🌆 Город: {championship['city']}\n"
                response += f"👥 Размер команды: {championship['team_members_count']} участников\n"
                response += f"📅 Дедлайн подачи заявок: {championship['application_deadline']}\n\n"

                if description:
                    response += f"📝 *Описание:*\n{description}\n\n"

                response += f"Для получения подробной информации отправьте /championship_{championship['tournament_id']}"

                await message.answer(response, parse_mode="Markdown")

        except Exception as e:
            user_id_str = str(user.id if hasattr(user, 'id') else user.get('id', 'unknown'))
            logger.error(f"Ошибка при получении рекомендуемых чемпионатов для пользователя {user_id_str}: {e}")

            await message.answer(
                "Произошла ошибка при получении рекомендаций. Пожалуйста, попробуйте позже.",
                reply_markup=get_championship_menu_keyboard()
            )

    @dp.message_handler(lambda message: message.text.startswith('/championship_'))
    async def championship_details(message: types.Message):
        """
        Обработчик запроса информации о конкретном чемпионате

        Args:
            message: Сообщение от пользователя
        """
        user = UserRepository.get_by_telegram_id(str(message.from_user.id))
        if not user:
            await message.answer(
                "Ваш аккаунт не привязан к боту. Отправьте /start для привязки."
            )
            return

        try:
            championship_id = int(message.text.split('_')[1])

            championship = await api_client.get_championship_details(championship_id)

            if not championship:
                await message.answer("Чемпионат не найден.")
                return

            response = f"🏆 *{championship['name']}*\n\n"
            response += f"⚽ Вид спорта: {championship['sport']}\n"
            response += f"🌆 Город: {championship['city']}\n"
            response += f"👥 Размер команды: {championship['team_members_count']} участников\n"
            response += f"📅 Дедлайн подачи заявок: {championship['application_deadline']}\n\n"

            if 'stages' in championship and championship['stages']:
                response += f"📊 *Этапы чемпионата:*\n"
                for stage in championship['stages']:
                    status = "✅ Опубликован" if stage.get('is_published') else "⏳ Не опубликован"
                    response += f"- {stage['name']}: {status}\n"

            if championship.get('description'):
                response += f"\n📝 *Описание:*\n{championship['description']}\n"

            response += f"\n👔 Организатор: {championship.get('org_name', 'Не указан')}\n"

            if championship.get('is_stopped'):
                response += "⚠️ Чемпионат остановлен\n"

            await message.answer(response, parse_mode="Markdown")

        except ValueError:
            await message.answer("Неверный формат команды. Используйте /championship_<id>, например /championship_123")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о чемпионате: {e}")
            await message.answer(
                "Произошла ошибка при получении информации о чемпионате. Пожалуйста, попробуйте позже."
            )