from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils.logger import get_logger
from database.repositories.user_repository import UserRepository
from api.client import ApiClient
from bot.keyboards.keyboards import get_championship_menu_keyboard, get_start_keyboard

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
            wait_message = await message.answer("Ищем чемпионаты, которые могут вас заинтересовать...")

            user_id = user.id if hasattr(user, 'id') else user['id'] if isinstance(user,
                                                                                   dict) and 'id' in user else None

            if user_id is None:
                raise ValueError("Не удалось определить ID пользователя")

            championships = await api_client.get_recommended_championships(user_id)

            if championships is None or not isinstance(championships, list) or len(championships) == 0:
                await message.answer(
                    "На данный момент у нас нет рекомендаций для вас. Пожалуйста, проверьте позже.",
                    reply_markup=get_start_keyboard()
                )
                return

            valid_championships = [c for c in championships if isinstance(c, dict) and c.get('name')]
            if not valid_championships:
                await message.answer(
                    "На данный момент у нас нет рекомендаций для вас. Пожалуйста, проверьте позже.",
                    reply_markup=get_start_keyboard()
                )
                return

            await message.answer(
                "🏆 Вот чемпионаты, которые могут вас заинтересовать:",
                reply_markup=get_start_keyboard()
            )

            def escape_markdown(text):
                if not text:
                    return ""
                special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.',
                                 '!']
                for char in special_chars:
                    text = text.replace(char, '\\' + char)
                return text

            count_sent = 0
            for championship in valid_championships:
                try:
                    name = escape_markdown(championship.get('name', 'Без названия'))
                    sport = escape_markdown(championship.get('sport', 'Не указан'))
                    city = escape_markdown(championship.get('city', 'Не указан'))
                    team_size = championship.get('team_members_count', '-')
                    deadline = escape_markdown(championship.get('application_deadline', 'Не указан'))

                    description = championship.get('description', '')
                    if len(description) > 200:
                        description = description[:197] + "..."
                    description = escape_markdown(description)

                    response = f"🏆 <b>{name}</b>\n\n"
                    response += f"⚽ Вид спорта: {sport}\n"
                    response += f"🌆 Город: {city}\n"
                    response += f"👥 Размер команды: {team_size} участников\n"
                    response += f"📅 Дедлайн подачи заявок: {deadline}\n\n"

                    if description:
                        response += f"📝 <b>Описание:</b>\n{description}\n\n"

                    tournament_id = championship.get('tournament_id', championship.get('id'))
                    if tournament_id:
                        response += f"Для получения подробной информации отправьте /championship_{tournament_id}"

                    await message.answer(response, parse_mode="HTML")
                    count_sent += 1
                except Exception as e:
                    logger.error(f"Ошибка при обработке информации о чемпионате: {e}")

                    try:
                        name = championship.get('name', 'Без названия')
                        sport = championship.get('sport', 'Не указан')
                        city = championship.get('city', 'Не указан')
                        team_size = championship.get('team_members_count', '-')
                        deadline = championship.get('application_deadline', 'Не указан')

                        plain_response = f"🏆 {name}\n\n"
                        plain_response += f"⚽ Вид спорта: {sport}\n"
                        plain_response += f"🌆 Город: {city}\n"
                        plain_response += f"👥 Размер команды: {team_size} участников\n"
                        plain_response += f"📅 Дедлайн подачи заявок: {deadline}\n"

                        tournament_id = championship.get('tournament_id', championship.get('id'))
                        if tournament_id:
                            plain_response += f"\nДля получения подробной информации отправьте /championship_{tournament_id}"

                        await message.answer(plain_response)
                        count_sent += 1
                    except Exception as e2:
                        logger.error(f"Не удалось отправить даже простое сообщение: {e2}")

            if count_sent == 0:
                await message.answer(
                    "К сожалению, не удалось загрузить информацию о рекомендуемых чемпионатах. Пожалуйста, попробуйте позже.",
                    reply_markup=get_start_keyboard()
                )

        except Exception as e:
            user_id_for_log = "неизвестно"
            try:
                if hasattr(user, 'id'):
                    user_id_for_log = user.id
                elif isinstance(user, dict) and 'id' in user:
                    user_id_for_log = user['id']
            except:
                pass

            logger.error(f"Ошибка при получении рекомендуемых чемпионатов для пользователя {user_id_for_log}: {e}")
            await message.answer(
                "Произошла ошибка при получении рекомендаций. Пожалуйста, попробуйте позже.",
                reply_markup=get_start_keyboard()
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
            wait_message = await message.answer("Загружаем информацию о чемпионате...")

            try:
                championship_id = int(message.text.split('_')[1])
            except (IndexError, ValueError) as e:
                await message.answer(
                    "Неверный формат команды. Используйте /championship_<id>, например /championship_123")
                return

            user_id = user.id if hasattr(user, 'id') else user['id'] if isinstance(user,
                                                                                   dict) and 'id' in user else None

            if user_id is None:
                raise ValueError("Не удалось определить ID пользователя")

            championship = await api_client.get_championship_details(championship_id)

            if isinstance(championship, dict) and "error" in championship:
                error_msg = championship["error"]

                if "404" in error_msg or "not found" in error_msg.lower():
                    await message.answer(
                        f"❌ Чемпионат с ID {championship_id} не найден.\n\n"
                        f"Пожалуйста, проверьте правильность ID. Возможно, вы хотели посмотреть информацию о другом чемпионате?\n\n"
                        f"Попробуйте команду «Рекомендуемые чемпионаты» для получения актуального списка.",
                        reply_markup=get_start_keyboard()
                    )
                elif "403" in error_msg or "access" in error_msg.lower():
                    await message.answer(
                        f"❌ У вас нет доступа к информации о чемпионате с ID {championship_id}.\n\n"
                        f"Возможно, этот чемпионат закрыт или предназначен для других участников.",
                        reply_markup=get_start_keyboard()
                    )
                elif "401" in error_msg:
                    await message.answer("Требуется повторная авторизация. Отправьте команду /start.")
                else:
                    await message.answer(
                        f"❌ Ошибка при получении информации о чемпионате: {error_msg}\n\n"
                        f"Пожалуйста, попробуйте позже.",
                        reply_markup=get_start_keyboard()
                    )
                return

            if not championship or not isinstance(championship, dict):
                await message.answer(
                    f"❌ Чемпионат с ID {championship_id} не найден или у вас нет доступа к нему.\n\n"
                    f"Проверьте правильность ID и попробуйте снова.",
                    reply_markup=get_start_keyboard()
                )
                return

            name = championship.get('name', f'Чемпионат #{championship_id}')
            sport = championship.get('sport', 'Не указан')
            city = championship.get('city', 'Не указан')
            team_members_count = championship.get('team_members_count', '-')
            application_deadline = championship.get('application_deadline', 'Не указан')
            description = championship.get('description', '')
            org_name = championship.get('org_name', 'Не указан')
            is_stopped = championship.get('is_stopped', False)


            response = f"🏆 <b>{name}</b>\n\n"
            response += f"⚽ Вид спорта: {sport}\n"
            response += f"🌆 Город: {city}\n"
            response += f"👥 Размер команды: {team_members_count} участников\n"
            response += f"📅 Дедлайн подачи заявок: {application_deadline}\n\n"

            if 'stages' in championship and championship['stages']:
                response += f"📊 <b>Этапы чемпионата:</b>\n"
                for stage in championship['stages']:
                    status = "✅ Опубликован" if stage.get('is_published') else "⏳ Не опубликован"
                    response += f"- {stage.get('name', 'Этап')}: {status}\n"
                response += "\n"

            if description:
                if len(description) > 500:
                    description = description[:497] + "..."
                response += f"📝 <b>Описание:</b>\n{description}\n\n"

            response += f"👔 Организатор: {org_name}\n"

            if is_stopped:
                response += "⚠️ Чемпионат остановлен\n"

            await message.answer(response, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Ошибка при получении информации о чемпионате: {e}")
            await message.answer(
                "❌ Произошла ошибка при получении информации о чемпионате. Пожалуйста, попробуйте позже.",
                reply_markup=get_start_keyboard()
            )