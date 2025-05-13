import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from database.connection import get_db_session
from database.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Репозиторий для работы с пользователями
    """

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            Словарь с данными пользователя или None, если пользователь не найден
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "telegram_id": user.telegram_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_active": user.is_active
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователя по ID {user_id}: {e}")
            return None

    @staticmethod
    def get_by_phone(phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по номеру телефона

        Args:
            phone_number: Номер телефона пользователя

        Returns:
            Словарь с данными пользователя или None, если пользователь не найден
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.phone_number == phone_number).first()
                if user:
                    return {
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "telegram_id": user.telegram_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_active": user.is_active
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователя по номеру телефона {phone_number}: {e}")
            return None

    @staticmethod
    def get_by_telegram_id(telegram_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по Telegram ID

        Args:
            telegram_id: Telegram ID пользователя

        Returns:
            Словарь с данными пользователя или None, если пользователь не найден
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.telegram_id == telegram_id).first()
                if user:
                    # Создаем словарь с нужными атрибутами пользователя
                    return {
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "telegram_id": user.telegram_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_active": user.is_active
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователя по Telegram ID {telegram_id}: {e}")
            return None

    @staticmethod
    def update_telegram_id(phone_number: str, telegram_id: str) -> bool:
        """
        Обновление Telegram ID пользователя

        Args:
            phone_number: Номер телефона пользователя
            telegram_id: Новый Telegram ID

        Returns:
            True, если обновление успешно, иначе False
        """
        try:
            with get_db_session() as session:
                # Сначала проверяем, существует ли пользователь с таким telegram_id
                existing_user = session.query(User).filter(User.telegram_id == telegram_id).first()
                if existing_user:
                    # Если такой пользователь уже есть, очищаем его telegram_id
                    existing_user.telegram_id = None
                    session.flush()

                # Теперь находим пользователя по номеру телефона и обновляем telegram_id
                user = session.query(User).filter(User.phone_number == phone_number).first()
                if user:
                    user.telegram_id = telegram_id
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении Telegram ID для пользователя {phone_number}: {e}")
            return False

    @staticmethod
    def get_all_active_with_telegram() -> List[Dict[str, Any]]:
        """
        Получение всех активных пользователей с привязанным Telegram ID

        Returns:
            Список словарей с данными пользователей
        """
        try:
            with get_db_session() as session:
                users = session.query(User).filter(
                    User.is_active == True,
                    User.telegram_id.isnot(None)
                ).all()

                # Преобразуем объекты User в словари
                result = []
                for user in users:
                    result.append({
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "telegram_id": user.telegram_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_active": user.is_active
                    })
                return result
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении активных пользователей с Telegram: {e}")
            return []

    @staticmethod
    def create(phone_number: str, first_name: str, last_name: str, telegram_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Создание нового пользователя

        Args:
            phone_number: Номер телефона
            first_name: Имя
            last_name: Фамилия
            telegram_id: Telegram ID (опционально)

        Returns:
            Словарь с данными созданного пользователя или None в случае ошибки
        """
        try:
            with get_db_session() as session:
                # Проверяем, существует ли пользователь с таким telegram_id
                if telegram_id:
                    existing_user = session.query(User).filter(User.telegram_id == telegram_id).first()
                    if existing_user:
                        # Если такой пользователь уже есть, очищаем его telegram_id
                        existing_user.telegram_id = None
                        session.flush()

                user = User(
                    phone_number=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                    telegram_id=telegram_id
                )
                session.add(user)
                session.flush()

                # Возвращаем словарь с данными пользователя
                return {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "telegram_id": user.telegram_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active
                }
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return None