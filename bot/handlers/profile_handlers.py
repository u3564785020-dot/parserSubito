"""
Обработчики профиля пользователя
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime

from core.database import UserRepository
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "👤 Профиль")
@router.message(Command("profile"))
async def cmd_profile(message: Message, user_repo: UserRepository):
    """Просмотр профиля пользователя"""
    user = await user_repo.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден. Используйте /start")
        return
    
    # Форматирование информации о подписке
    if user.subscription_end and user.subscription_end > datetime.utcnow():
        remaining = user.subscription_end - datetime.utcnow()
        hours = int(remaining.total_seconds() / 3600)
        minutes = int((remaining.total_seconds() % 3600) / 60)
        subscription_info = f"✅ Активна ({hours}ч {minutes}мин)"
    else:
        subscription_info = "❌ Не активна"
    
    # Статус парсинга
    parsing_status = "🟢 Активен" if user.parsing_active else "🔴 Остановлен"
    
    # Настройки поиска
    settings = user.search_settings
    
    profile_text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"👤 Имя: {user.first_name or 'Не указано'}\n"
        f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n\n"
        f"📦 <b>Площадка: Subito 🇮🇹</b>\n\n"
        f"⏱ <b>Подписка:</b> {subscription_info}\n"
        f"🔍 <b>Парсинг:</b> {parsing_status}\n\n"
        f"<b>⚙️ Настройки Subito (🇮🇹)</b>\n\n"
        f"💰 Минимальная цена: {settings.get('min_price', 5)} EUR\n"
        f"💸 Максимальная цена: {settings.get('max_price', 3000)} EUR\n"
        f"📊 Количество объявлений: {settings.get('max_listings', 4)}\n"
        f"⭐ Максимальный рейтинг: {settings.get('max_rating', 0)}\n"
        f"❤️ Макс. лайков: {settings.get('max_likes', 0)}\n"
        f"📝 Макс. объявлений у продавца: {settings.get('max_seller_listings', 1)}\n"
        f"📅 Дата регистрации: {settings.get('seller_registration_year', 2025)}\n"
        f"👁️ Макс. просмотров в GabaParser: {settings.get('max_views', 0)}\n"
    )
    
    # Ключевые слова
    keywords = settings.get('keywords', [])
    if keywords:
        profile_text += f"\n🔑 Ключевые слова: {', '.join(keywords)}"
    
    await message.answer(profile_text, parse_mode="HTML")

