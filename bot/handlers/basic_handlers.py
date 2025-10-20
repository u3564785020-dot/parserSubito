"""
Базовые обработчики команд
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_menu, get_main_menu_admin, get_admin_menu
from bot.filters import IsAdminFilter
from core.database import UserRepository
from config import ADMIN_ID
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработчик команды /start"""
    await state.clear()
    
    # Создание или получение пользователя
    user = await user_repo.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    # Проверка блокировки
    if user.is_blocked:
        await message.answer(
            "❌ Ваш доступ к боту заблокирован.\n"
            "Для получения дополнительной информации обратитесь в поддержку."
        )
        return
    
    welcome_text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "🔄 <b>Перезапустить бота</b>\n"
        "Бот успешно перезапущен и готов к работе.\n\n"
        "📦 <b>Площадка: Subito 🇮🇹</b>\n\n"
        "Используйте меню ниже для навигации:"
    )
    
    # Выбор клавиатуры в зависимости от прав
    if message.from_user.id == ADMIN_ID:
        keyboard = get_main_menu_admin()
        welcome_text += "\n\n👑 <b>Режим администратора активирован</b>"
    else:
        keyboard = get_main_menu()
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "🔙 Вернуться в главное меню")
@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    # Показываем соответствующее меню в зависимости от роли пользователя
    if message.from_user.id == ADMIN_ID:
        keyboard = get_main_menu_admin()
        text = "📋 Главное меню (Администратор)"
    else:
        keyboard = get_main_menu()
        text = "📋 Главное меню"
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "👑 Админ-панель")
async def cmd_admin_panel(message: Message, state: FSMContext):
    """Переход в админ-панель"""
    await state.clear()
    
    admin_text = (
        "👑 <b>Панель администратора</b>\n\n"
        "Добро пожаловать в панель управления ботом!\n\n"
        "Доступные функции:\n"
        "📊 Статистика - просмотр статистики бота\n"
        "👥 Управление пользователями - управление пользователями\n"
        "🎁 Добавить бонусные часы - начисление времени подписки\n"
        "🚫 Заблокировать пользователя - ограничение доступа\n"
        "📢 Массовая рассылка - отправка сообщений всем пользователям"
    )
    
    await message.answer(admin_text, reply_markup=get_admin_menu(), parse_mode="HTML")


@router.message(F.text == "📧 Support")
@router.message(Command("support"))
async def cmd_support(message: Message):
    """Обработчик команды поддержки"""
    support_text = (
        "📧 <b>Поддержка</b>\n\n"
        "Предложения и замечания по работе площадок отправляйте, воспользовавшись командой:\n\n"
        "Для связи с поддержкой используйте команду /support и опишите вашу проблему.\n\n"
        "Мы постараемся ответить вам в кратчайшие сроки! 💬"
    )
    await message.answer(support_text, parse_mode="HTML")


@router.message(F.text == "💬 FAQ")
@router.message(Command("faq"))
async def cmd_faq(message: Message):
    """Обработчик FAQ"""
    faq_text = (
        "💬 <b>FAQ - Часто задаваемые вопросы</b>\n\n"
        "<b>Q: Как начать поиск объявлений?</b>\n"
        "A: Нажмите кнопку '🔍 Начать поиск' и настройте параметры фильтрации.\n\n"
        "<b>Q: Как изменить настройки поиска?</b>\n"
        "A: Используйте кнопку '🔧 Изменить параметры поиска' в главном меню.\n\n"
        "<b>Q: Как работает подписка?</b>\n"
        "A: Выберите тариф в разделе '💰 ПРАЙС'. Парсинг работает только при активной подписке.\n\n"
        "<b>Q: Что делать если объявления не приходят?</b>\n"
        "A: Проверьте настройки фильтров и убедитесь, что подписка активна.\n\n"
        "Остались вопросы? Обратитесь в поддержку: /support"
    )
    await message.answer(faq_text, parse_mode="HTML")


@router.message(F.text == "📺 Наш канал")
async def cmd_channel(message: Message):
    """Обработчик кнопки канала"""
    channel_text = (
        "📺 <b>Наш канал</b>\n\n"
        "Подписывайтесь на наш канал, чтобы быть в курсе всех обновлений и новостей!\n\n"
        "🔗 Ссылка на канал будет добавлена позже"
    )
    await message.answer(channel_text, parse_mode="HTML")


@router.message(F.text == "👨‍💻 РЕФЕРАЛЬНАЯ ПРОГРАММА")
@router.message(Command("ref_program"))
async def cmd_referral(message: Message):
    """Обработчик реферальной программы"""
    referral_text = (
        "👨‍💻 <b>РЕФЕРАЛЬНАЯ ПРОГРАММА</b>\n\n"
        "Приглашайте друзей и получайте бонусы!\n\n"
        "📊 Ваша реферальная ссылка:\n"
        f"<code>https://t.me/your_bot?start={message.from_user.id}</code>\n\n"
        "🎁 За каждого приглашенного друга вы получите бонусные часы использования бота!\n\n"
        "Функционал будет добавлен в следующих версиях."
    )
    await message.answer(referral_text, parse_mode="HTML")


@router.message(F.text == "🎁 БОНУСНАЯ СИСТЕМА")
async def cmd_bonus(message: Message, user_repo: UserRepository):
    """Обработчик бонусной системы"""
    user = await user_repo.get_user(message.from_user.id)
    
    bonus_text = (
        "🎁 <b>БОНУСНАЯ СИСТЕМА</b>\n\n"
        "Получайте бонусные часы за:\n"
        "• Приглашение друзей\n"
        "• Активное использование бота\n"
        "• Участие в акциях\n\n"
    )
    
    if user and user.subscription_end:
        from datetime import datetime
        remaining = user.subscription_end - datetime.utcnow()
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() / 3600)
            minutes = int((remaining.total_seconds() % 3600) / 60)
            bonus_text += f"⏱ Ваша текущая подписка: {hours}ч {minutes}мин"
        else:
            bonus_text += "⏱ У вас нет активной подписки"
    else:
        bonus_text += "⏱ У вас нет активной подписки"
    
    await message.answer(bonus_text, parse_mode="HTML")

