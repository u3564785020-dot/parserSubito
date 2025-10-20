"""
Менеджер подключения к MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """Менеджер подключения к MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self, uri: str, db_name: str) -> None:
        """Подключение к MongoDB"""
        try:
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client[db_name]
            
            # Проверка подключения
            await self.client.admin.command('ping')
            logger.info(f"✅ Успешное подключение к MongoDB: {db_name}")
            
            # Создание индексов
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            raise
    
    async def _create_indexes(self) -> None:
        """Создание индексов для коллекций"""
        try:
            # Индекс для пользователей
            await self.db.users.create_index("telegram_id", unique=True)
            
            # Индекс для статистики
            await self.db.statistics.create_index("date")
            
            logger.info("✅ Индексы созданы")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка создания индексов: {e}")
    
    async def disconnect(self) -> None:
        """Отключение от MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Отключение от MongoDB")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Получение объекта базы данных"""
        if self.db is None:
            raise RuntimeError("База данных не подключена")
        return self.db


# Глобальный экземпляр
mongodb = MongoDB()

