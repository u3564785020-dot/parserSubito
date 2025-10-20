"""
Обработчики парсинга
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime

from core.database import UserRepository
from bot.keyboards import get_main_menu
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🔍 Начать поиск")
@router.message(Command("parse"))
async def cmd_start_parsing(message: Message, user_repo: UserRepository):
    """Запуск парсинга"""
    user = await user_repo.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден. Используйте /start")
        return
    
    # Проверка блокировки
    if user.is_blocked:
        await message.answer("❌ Ваш доступ к боту заблокирован.")
        return
    
    # Проверка подписки
    if not user.has_active_subscription():
        await message.answer(
            "❌ У вас нет активной подписки!\n\n"
            "Для начала парсинга необходимо активировать подписку.\n"
            "Используйте команду /prices для выбора тарифа."
        )
        return
    
    # Проверка, не запущен ли уже парсинг
    if user.parsing_active:
        await message.answer(
            "⚠️ Парсинг уже активен!\n\n"
            "Для остановки используйте кнопку '❌ Остановить отслеживание'"
        )
        return
    
    # Активация парсинга
    await user_repo.set_parsing_status(message.from_user.id, True)
    
    # Информация о настройках
    settings = user.search_settings
    settings_info = (
        f"💰 Цена: {settings.get('min_price', 5)} - {settings.get('max_price', 3000)} EUR\n"
        f"📊 Макс. объявлений: {settings.get('max_listings', 4)}\n"
        f"📝 Макс. объявлений у продавца: {settings.get('max_seller_listings', 1)}\n"
    )
    
    keywords = settings.get('keywords', [])
    if keywords:
        settings_info += f"🔑 Ключевые слова: {', '.join(keywords)}\n"
    
    await message.answer(
        "🔘 <b>Начать парсинг</b>\n\n"
        "✅ Парсинг успешно запущен!\n\n"
        "📦 <b>Площадка: Subito 🇮🇹</b>\n\n"
        "<b>Активные настройки:</b>\n"
        f"{settings_info}\n"
        "🔍 Бот начнет отправлять найденные объявления в соответствии с вашими настройками.\n\n"
        "Для остановки используйте кнопку '❌ Остановить отслеживание'",
        parse_mode="HTML"
    )
    
    logger.info(f"✅ Парсинг запущен для пользователя {message.from_user.id}")


@router.message(F.text == "❌ Остановить отслеживание")
@router.message(Command("stop_parse"))
async def cmd_stop_parsing(message: Message, user_repo: UserRepository):
    """Остановка парсинга"""
    user = await user_repo.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден. Используйте /start")
        return
    
    if not user.parsing_active:
        await message.answer("⚠️ Парсинг не был запущен.")
        return
    
    # Остановка парсинга
    await user_repo.set_parsing_status(message.from_user.id, False)
    
    await message.answer(
        "❌ <b>Остановить отслеживание</b>\n\n"
        "✅ Парсинг успешно остановлен!\n\n"
        "Для повторного запуска используйте кнопку '🔍 Начать поиск'",
        parse_mode="HTML"
    )
    
    logger.info(f"🛑 Парсинг остановлен для пользователя {message.from_user.id}")


@router.message(F.text == "🔁 Повторить последний запрос")
@router.message(Command("start_parse"))
async def cmd_repeat_parsing(message: Message, user_repo: UserRepository):
    """Повторный запуск парсинга с теми же настройками"""
    # Используем ту же логику что и при запуске
    await cmd_start_parsing(message, user_repo)

