"""
Модель пользователя
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class User:
    """Модель пользователя бота"""
    
    def __init__(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        subscription_end: Optional[datetime] = None,
        is_blocked: bool = False,
        created_at: Optional[datetime] = None,
        search_settings: Optional[Dict[str, Any]] = None,
        parsing_active: bool = False,
        seen_listings: Optional[list] = None
    ):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.subscription_end = subscription_end
        self.is_blocked = is_blocked
        self.created_at = created_at or datetime.utcnow()
        self.search_settings = search_settings or self._default_search_settings()
        self.parsing_active = parsing_active
        self.seen_listings = seen_listings or []
    
    @staticmethod
    def _default_search_settings() -> Dict[str, Any]:
        """Настройки поиска по умолчанию"""
        return {
            "min_price": 5,
            "max_price": 3000,
            "max_listings": 4,
            "max_rating": 0,
            "max_likes": 0,
            "max_seller_listings": 1,
            "seller_registration_year": 2025,
            "max_views": 0,
            "keywords": []
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для MongoDB"""
        return {
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "subscription_end": self.subscription_end,
            "is_blocked": self.is_blocked,
            "created_at": self.created_at,
            "search_settings": self.search_settings,
            "parsing_active": self.parsing_active,
            "seen_listings": self.seen_listings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Создание объекта из словаря MongoDB"""
        return cls(
            telegram_id=data["telegram_id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            subscription_end=data.get("subscription_end"),
            is_blocked=data.get("is_blocked", False),
            created_at=data.get("created_at"),
            search_settings=data.get("search_settings"),
            parsing_active=data.get("parsing_active", False),
            seen_listings=data.get("seen_listings", [])
        )
    
    def has_active_subscription(self) -> bool:
        """Проверка активности подписки"""
        if not self.subscription_end:
            return False
        return datetime.utcnow() < self.subscription_end
    
    def add_subscription_hours(self, hours: int) -> None:
        """Добавление часов к подписке"""
        if not self.subscription_end or self.subscription_end < datetime.utcnow():
            # Если подписка истекла или отсутствует, начинаем с текущего момента
            self.subscription_end = datetime.utcnow() + timedelta(hours=hours)
        else:
            # Если подписка активна, добавляем к существующему времени
            self.subscription_end += timedelta(hours=hours)
    
    def add_seen_listing(self, listing_id: str) -> None:
        """Добавление просмотренного объявления"""
        if listing_id not in self.seen_listings:
            self.seen_listings.append(listing_id)
            # Ограничиваем список последними 1000 объявлениями
            if len(self.seen_listings) > 1000:
                self.seen_listings = self.seen_listings[-1000:]
    
    def is_listing_seen(self, listing_id: str) -> bool:
        """Проверка, было ли объявление уже отправлено"""
        return listing_id in self.seen_listings

