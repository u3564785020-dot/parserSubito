"""
Главный файл Telegram-бота для парсинга Subito.it
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, MONGO_URI, MONGO_DB_NAME
from core.database import mongodb, UserRepository
from bot.handlers import (
    basic_handlers,
    profile_handlers,
    settings_handlers,
    subscription_handlers,
    parsing_handlers,
    admin_handlers
)
from bot.utils import ParsingScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    
    # Проверка наличия токена
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен! Проверьте переменные окружения.")
        return
    
    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Подключение к MongoDB
    try:
        await mongodb.connect(MONGO_URI, MONGO_DB_NAME)
    except Exception as e:
        logger.error(f"❌ Не удалось подключиться к MongoDB: {e}")
        return
    
    # Создание репозитория пользователей
    user_repo = UserRepository(mongodb.get_database())
    
    # Регистрация middleware для передачи user_repo в handlers
    @dp.message.middleware()
    async def user_repo_middleware(handler, event, data):
        data['user_repo'] = user_repo
        return await handler(event, data)
    
    @dp.callback_query.middleware()
    async def callback_user_repo_middleware(handler, event, data):
        data['user_repo'] = user_repo
        return await handler(event, data)
    
    # Регистрация роутеров
    dp.include_router(basic_handlers.router)
    dp.include_router(profile_handlers.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(subscription_handlers.router)
    dp.include_router(parsing_handlers.router)
    dp.include_router(admin_handlers.router)
    
    # Инициализация и запуск планировщика
    scheduler = ParsingScheduler(bot, user_repo)
    scheduler.start()
    
    logger.info("✅ Бот запущен и готов к работе!")
    
    try:
        # Запуск polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Остановка планировщика
        scheduler.stop()
        
        # Отключение от MongoDB
        await mongodb.disconnect()
        
        # Закрытие сессии бота
        await bot.session.close()
        
        logger.info("🛑 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

