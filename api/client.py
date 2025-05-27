import logging
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.config import API_BASE_URL, API_TOKEN, API_TIMEOUT

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Клиент для взаимодействия с API основного приложения
    """

    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        self.timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)

    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса к API

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API
            data: Данные для отправки (опционально)

        Returns:
            Ответ от API в виде словаря

        Raises:
            Exception: Если произошла ошибка при выполнении запроса
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                if method == "GET":
                    async with session.get(url, headers=self.headers, params=data) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"API error {response.status}: {error_text}")
                            return {"error": f"API error {response.status}: {error_text}"}
                        return await response.json()

                elif method == "POST":
                    async with session.post(url, headers=self.headers, json=data) as response:
                        if response.status not in (200, 201):
                            error_text = await response.text()
                            logger.error(f"API error {response.status}: {error_text}")
                            return {"error": f"API error {response.status}: {error_text}"}
                        return await response.json()

                elif method == "PUT":
                    async with session.put(url, headers=self.headers, json=data) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"API error {response.status}: {error_text}")
                            return {"error": f"API error {response.status}: {error_text}"}
                        return await response.json()

                elif method == "DELETE":
                    async with session.delete(url, headers=self.headers) as response:
                        if response.status != 204:
                            error_text = await response.text()
                            logger.error(f"API error {response.status}: {error_text}")
                            return {"error": f"API error {response.status}: {error_text}"}
                        return {"success": True}

                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при выполнении запроса к {url}: {e}")
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Необработанная ошибка при запросе к {url}: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

    async def get_user_data(self, phone_number: str) -> Dict[str, Any]:
        """
        Получение данных пользователя по номеру телефона

        Args:
            phone_number: Номер телефона пользователя

        Returns:
            Словарь с данными пользователя
        """
        return await self._make_request("GET", f"users/by-phone/{phone_number}")

    async def get_upcoming_matches(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        Получение предстоящих матчей на ближайшие дни

        Args:
            days: Количество дней для поиска

        Returns:
            Список матчей
        """
        return await self._make_request("GET", "matches/upcoming", {"days": days})

    async def get_recommended_championships(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получение рекомендуемых чемпионатов для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список рекомендуемых чемпионатов
        """
        return await self._make_request("GET", f"championships/recommended/{user_id}")

    async def confirm_notification_delivery(self, notification_id: int, delivered: bool = True) -> Dict[str, Any]:
        """
        Подтверждение доставки уведомления

        Args:
            notification_id: ID уведомления
            delivered: Флаг доставки

        Returns:
            Результат операции
        """
        data = {
            "notification_id": notification_id,
            "delivered": delivered,
            "delivered_at": datetime.now().isoformat()
        }
        return await self._make_request("POST", "notifications/confirm-delivery", data)

    async def get_user_teams(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получение команд пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список команд пользователя
        """
        return await self._make_request("GET", f"users/{user_id}/teams")

    async def get_user_championships(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получение чемпионатов пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список чемпионатов пользователя
        """
        return await self._make_request("GET", f"users/{user_id}/championships")

    async def get_user_matches(self, user_id: int, status: str = "upcoming") -> List[Dict[str, Any]]:
        """
        Получение матчей пользователя

        Args:
            user_id: ID пользователя
            status: Статус матчей ("upcoming", "past", "all")

        Returns:
            Список матчей пользователя
        """
        return await self._make_request("GET", f"users/{user_id}/matches", {"status": status})

    async def get_team_details(self, team_id: int) -> Dict[str, Any]:
        """
        Получение детальной информации о команде

        Args:
            team_id: ID команды

        Returns:
            Информация о команде
        """
        return await self._make_request("GET", f"teams/{team_id}")

    async def get_championship_details(self, tournament_id: int) -> Dict[str, Any]:
        """
        Получение детальной информации о чемпионате

        Args:
            tournament_id: ID чемпионата

        Returns:
            Информация о чемпионате
        """
        return await self._make_request("GET", f"championships/{tournament_id}")

    async def accept_team_invitation(self, invitation_id: int) -> Dict[str, Any]:
        """
        Принятие приглашения в команду

        Args:
            invitation_id: ID приглашения

        Returns:
            Результат операции
        """
        result = await self._make_request("POST", f"invitations/team/{invitation_id}/accept")
        return result

    async def decline_team_invitation(self, invitation_id: int) -> Dict[str, Any]:
        """
        Отклонение приглашения в команду

        Args:
            invitation_id: ID приглашения

        Returns:
            Результат операции
        """
        result = await self._make_request("POST", f"invitations/team/{invitation_id}/decline")
        return result

    async def accept_committee_invitation(self, invitation_id: int) -> Dict[str, Any]:
        """
        Принятие приглашения в оргкомитет

        Args:
            invitation_id: ID приглашения

        Returns:
            Результат операции
        """
        result = await self._make_request("POST", f"invitations/committee/{invitation_id}/accept")
        return result

    async def decline_committee_invitation(self, invitation_id: int) -> Dict[str, Any]:
        """
        Отклонение приглашения в оргкомитет

        Args:
            invitation_id: ID приглашения

        Returns:
            Результат операции
        """
        result = await self._make_request("POST", f"invitations/committee/{invitation_id}/decline")
        return result

    async def get_user_invitations(self, user_id: int, type: str = "all") -> List[Dict[str, Any]]:
        """
        Получение приглашений пользователя

        Args:
            user_id: ID пользователя
            type: Тип приглашений ("team", "committee", "all")

        Returns:
            Список приглашений
        """
        return await self._make_request("GET", f"users/{user_id}/invitations", {"type": type})

    async def decline_match(self, match_id: int, team_id: int, reason: str) -> Dict[str, Any]:
        """
        Отклонение участия в матче

        Args:
            match_id: ID матча
            team_id: ID команды
            reason: Причина отказа

        Returns:
            Результат операции
        """
        try:
            return await self._make_request("POST", f"match/withdraw", {
                "matchId": match_id,
                "teamId": team_id,
                "reason": reason
            })
        except Exception as e:
            logger.error(f"Ошибка при отклонении участия в матче {match_id}: {e}")
            return {"success": False, "error": str(e)}