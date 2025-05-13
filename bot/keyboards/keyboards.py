from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для запроса номера телефона

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопкой запроса номера телефона
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Отправить номер телефона", request_contact=True))
    return keyboard


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """
    Основная клавиатура для работы с ботом

    Returns:
        ReplyKeyboardMarkup: Основная клавиатура с кнопками меню
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои матчи"))
    keyboard.add(KeyboardButton("Мои чемпионаты"), KeyboardButton("Мои команды"))
    keyboard.add(KeyboardButton("Рекомендуемые чемпионаты"), KeyboardButton("Приглашения"))
    keyboard.add(KeyboardButton("Помощь"))
    return keyboard


def get_help_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для меню помощи

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками помощи
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("О боте", callback_data="help_about"),
        InlineKeyboardButton("Типы уведомлений", callback_data="help_notification_types"),
        InlineKeyboardButton("Как привязать другой номер", callback_data="help_change_phone"),
        InlineKeyboardButton("Связаться с поддержкой", callback_data="help_support")
    )
    return keyboard


def get_invitation_keyboard(invitation_id: int, invitation_type: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для ответа на приглашение

    Args:
        invitation_id: Идентификатор приглашения
        invitation_type: Тип приглашения ("team" или "committee")

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками принятия или отказа от приглашения
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Принять", callback_data=f"accept_{invitation_type}_{invitation_id}"),
        InlineKeyboardButton("Отклонить", callback_data=f"decline_{invitation_type}_{invitation_id}")
    )
    return keyboard


def get_match_actions_keyboard(match_id: int, team_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для действий с матчем

    Args:
        match_id: ID матча
        team_id: ID команды пользователя

    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями для матча
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Отклонить участие", callback_data=f"decline_match_{match_id}_{team_id}")
    )
    return keyboard


def get_team_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Расширенная клавиатура для работы с командами

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками меню команд
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои команды"))
    keyboard.add(KeyboardButton("Приглашения"), KeyboardButton("Мои матчи"))
    keyboard.add(KeyboardButton("Главное меню"))
    return keyboard


def get_championship_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для работы с чемпионатами

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками меню чемпионатов
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои чемпионаты"))
    keyboard.add(KeyboardButton("Рекомендуемые чемпионаты"))
    keyboard.add(KeyboardButton("Главное меню"))
    return keyboard

def get_match_actions_keyboard(match_id: int, team_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для действий с матчем

    Args:
        match_id: ID матча
        team_id: ID команды пользователя

    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями для матча
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Отклонить участие", callback_data=f"decline_match_{match_id}_{team_id}")
    )
    return keyboard


def get_team_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Расширенная клавиатура для работы с командами

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками меню команд
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои команды"))
    keyboard.add(KeyboardButton("Приглашения"), KeyboardButton("Мои матчи"))
    keyboard.add(KeyboardButton("Главное меню"))
    return keyboard


def get_championship_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для работы с чемпионатами

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками меню чемпионатов
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои чемпионаты"))
    keyboard.add(KeyboardButton("Рекомендуемые чемпионаты"))
    keyboard.add(KeyboardButton("Главное меню"))
    return keyboard


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """
    Основная клавиатура для работы с ботом

    Returns:
        ReplyKeyboardMarkup: Основная клавиатура с кнопками меню
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мои матчи"))
    keyboard.add(KeyboardButton("Мои чемпионаты"), KeyboardButton("Мои команды"))
    keyboard.add(KeyboardButton("Рекомендуемые чемпионаты"), KeyboardButton("Приглашения"))
    keyboard.add(KeyboardButton("Помощь"))
    return keyboard