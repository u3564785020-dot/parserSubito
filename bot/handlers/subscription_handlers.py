"""
Обработчики подписки
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from bot.keyboards import get_subscription_keyboard, get_main_menu
from core.database import UserRepository
from config import SUBSCRIPTION_PLANS
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "💰 ПРАЙС")
@router.message(Command("prices"))
async def cmd_prices(message: Message, user_repo: UserRepository):
    """Просмотр тарифов"""
    user = await user_repo.get_user(message.from_user.id)
    
    # Информация о текущей подписке
    subscription_info = ""
    if user and user.subscription_end and user.subscription_end > datetime.utcnow():
        remaining = user.subscription_end - datetime.utcnow()
        hours = int(remaining.total_seconds() / 3600)
        minutes = int((remaining.total_seconds() % 3600) / 60)
        subscription_info = f"\n⏱ <b>Ваша текущая подписка:</b> {hours}ч {minutes}мин\n"
    
    prices_text = (
        "💰 <b>ПРАЙС / БОНУСНАЯ СИСТЕМА</b>\n\n"
        "Выберите тариф для активации парсинга:\n\n"
        "⏱ <b>1 час</b> - Тестовый период\n"
        "📅 <b>24 часа</b> - Оптимальный выбор\n"
        "📆 <b>48 часов</b> - Максимальная выгода\n"
        f"{subscription_info}\n"
        "💡 <i>Примечание: Система оплаты будет добавлена позже.\n"
        "Сейчас вы можете получить бонусные часы от администратора.</i>"
    )
    
    await message.answer(
        prices_text,
        reply_markup=get_subscription_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("sub_"))
async def process_subscription(callback: CallbackQuery, user_repo: UserRepository):
    """Обработка выбора подписки"""
    plan = callback.data.replace("sub_", "")
    
    if plan not in SUBSCRIPTION_PLANS:
        await callback.answer("❌ Неверный тариф", show_alert=True)
        return
    
    hours = SUBSCRIPTION_PLANS[plan]
    
    # Информационное сообщение (пока без оплаты)
    info_text = (
        f"📋 <b>Выбран тариф: {plan}</b>\n\n"
        f"⏱ Длительность: {hours} час(ов)\n\n"
        "💡 Система оплаты будет добавлена в следующих версиях.\n"
        "Для получения бонусных часов обратитесь к администратору."
    )
    
    await callback.message.answer(info_text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.answer("📋 Главное меню", reply_markup=get_main_menu())
    await callback.answer()

