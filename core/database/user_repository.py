"""
Репозиторий для работы с пользователями
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.models import User
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users
    
    async def create_user(self, user: User) -> bool:
        """Создание нового пользователя"""
        try:
            await self.collection.insert_one(user.to_dict())
            logger.info(f"✅ Пользователь создан: {user.telegram_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя: {e}")
            return False
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по telegram_id"""
        try:
            data = await self.collection.find_one({"telegram_id": telegram_id})
            if data:
                return User.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            return None
    
    async def update_user(self, user: User) -> bool:
        """Обновление данных пользователя"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": user.telegram_id},
                {"$set": user.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя: {e}")
            return False
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> User:
        """Получение или создание пользователя"""
        user = await self.get_user(telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            await self.create_user(user)
        return user
    
    async def update_search_settings(
        self,
        telegram_id: int,
        settings: Dict[str, Any]
    ) -> bool:
        """Обновление настроек поиска"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"search_settings": settings}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка обновления настроек: {e}")
            return False
    
    async def set_parsing_status(self, telegram_id: int, status: bool) -> bool:
        """Установка статуса парсинга"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"parsing_active": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка установки статуса парсинга: {e}")
            return False
    
    async def add_subscription_hours(self, telegram_id: int, hours: int) -> bool:
        """Добавление часов к подписке"""
        user = await self.get_user(telegram_id)
        if user:
            user.add_subscription_hours(hours)
            return await self.update_user(user)
        return False
    
    async def block_user(self, telegram_id: int) -> bool:
        """Блокировка пользователя"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"is_blocked": True, "parsing_active": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка блокировки пользователя: {e}")
            return False
    
    async def unblock_user(self, telegram_id: int) -> bool:
        """Разблокировка пользователя"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"is_blocked": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка разблокировки пользователя: {e}")
            return False
    
    async def add_seen_listing(self, telegram_id: int, listing_id: str) -> bool:
        """Добавление просмотренного объявления"""
        try:
            result = await self.collection.update_one(
                {"telegram_id": telegram_id},
                {"$addToSet": {"seen_listings": listing_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Ошибка добавления просмотренного объявления: {e}")
            return False
    
    async def get_active_parsers(self) -> List[User]:
        """Получение списка пользователей с активным парсингом"""
        try:
            cursor = self.collection.find({
                "parsing_active": True,
                "is_blocked": False,
                "subscription_end": {"$gt": datetime.utcnow()}
            })
            users = []
            async for data in cursor:
                users.append(User.from_dict(data))
            return users
        except Exception as e:
            logger.error(f"❌ Ошибка получения активных парсеров: {e}")
            return []
    
    async def get_all_users(self) -> List[User]:
        """Получение всех пользователей"""
        try:
            cursor = self.collection.find({})
            users = []
            async for data in cursor:
                users.append(User.from_dict(data))
            return users
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователей: {e}")
            return []
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        try:
            # Убираем @ если есть
            username = username.lstrip('@')
            data = await self.collection.find_one({"username": username})
            if data:
                return User.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя по username: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        try:
            total_users = await self.collection.count_documents({})
            active_subscriptions = await self.collection.count_documents({
                "subscription_end": {"$gt": datetime.utcnow()}
            })
            active_parsers = await self.collection.count_documents({
                "parsing_active": True
            })
            blocked_users = await self.collection.count_documents({
                "is_blocked": True
            })
            
            return {
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "active_parsers": active_parsers,
                "blocked_users": blocked_users
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}

