"""
Обработчики настроек поиска
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import get_settings_keyboard, get_main_menu, get_cancel_keyboard
from core.database import UserRepository
import logging

logger = logging.getLogger(__name__)

router = Router()


class SettingsStates(StatesGroup):
    """Состояния для настройки параметров"""
    waiting_min_price = State()
    waiting_max_price = State()
    waiting_max_listings = State()
    waiting_max_rating = State()
    waiting_max_likes = State()
    waiting_max_seller_listings = State()
    waiting_seller_year = State()
    waiting_max_views = State()
    waiting_keywords = State()


@router.message(F.text == "🔧 Изменить параметры поиска")
@router.message(Command("change_params"))
async def cmd_change_params(message: Message, user_repo: UserRepository):
    """Изменение параметров поиска"""
    user = await user_repo.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден. Используйте /start")
        return
    
    settings = user.search_settings
    
    settings_text = (
        "⚙️ <b>Настройки Subito (🇮🇹)</b>\n\n"
        f"💰 Минимальная цена: {settings.get('min_price', 5)} EUR\n"
        f"💸 Максимальная цена: {settings.get('max_price', 3000)} EUR\n"
        f"📊 Количество объявлений: {settings.get('max_listings', 4)}\n"
        f"⭐ Максимальный рейтинг: {settings.get('max_rating', 0)}\n"
        f"❤️ Макс. лайков: {settings.get('max_likes', 0)}\n"
        f"📝 Макс. объявлений у продавца: {settings.get('max_seller_listings', 1)}\n"
        f"📅 Дата регистрации: {settings.get('seller_registration_year', 2025)}\n"
        f"👁️ Макс. просмотров: {settings.get('max_views', 0)}\n\n"
        "Выберите параметр для изменения:"
    )
    
    await message.answer(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "set_min_price")
async def set_min_price(callback: CallbackQuery, state: FSMContext):
    """Установка минимальной цены"""
    await callback.message.answer(
        "💰 Введите минимальную цену в EUR:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_min_price)
    await callback.answer()


@router.message(SettingsStates.waiting_min_price)
async def process_min_price(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка минимальной цены"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        min_price = float(message.text)
        if min_price < 0:
            await message.answer("❌ Цена не может быть отрицательной. Попробуйте снова:")
            return
        
        user = await user_repo.get_user(message.from_user.id)
        user.search_settings['min_price'] = min_price
        await user_repo.update_user(user)
        
        await state.clear()
        await message.answer(
            f"✅ Минимальная цена установлена: {min_price} EUR",
            reply_markup=get_main_menu()
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число:")


@router.callback_query(F.data == "set_max_price")
async def set_max_price(callback: CallbackQuery, state: FSMContext):
    """Установка максимальной цены"""
    await callback.message.answer(
        "💸 Введите максимальную цену в EUR:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_max_price)
    await callback.answer()


@router.message(SettingsStates.waiting_max_price)
async def process_max_price(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка максимальной цены"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        max_price = float(message.text)
        if max_price < 0:
            await message.answer("❌ Цена не может быть отрицательной. Попробуйте снова:")
            return
        
        user = await user_repo.get_user(message.from_user.id)
        user.search_settings['max_price'] = max_price
        await user_repo.update_user(user)
        
        await state.clear()
        await message.answer(
            f"✅ Максимальная цена установлена: {max_price} EUR",
            reply_markup=get_main_menu()
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число:")


@router.callback_query(F.data == "set_max_listings")
async def set_max_listings(callback: CallbackQuery, state: FSMContext):
    """Установка количества объявлений"""
    await callback.message.answer(
        "📊 Введите максимальное количество объявлений для поиска:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_max_listings)
    await callback.answer()


@router.message(SettingsStates.waiting_max_listings)
async def process_max_listings(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка количества объявлений"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        max_listings = int(message.text)
        if max_listings < 1:
            await message.answer("❌ Количество должно быть больше 0. Попробуйте снова:")
            return
        
        user = await user_repo.get_user(message.from_user.id)
        user.search_settings['max_listings'] = max_listings
        await user_repo.update_user(user)
        
        await state.clear()
        await message.answer(
            f"✅ Количество объявлений установлено: {max_listings}",
            reply_markup=get_main_menu()
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введите целое число:")


@router.callback_query(F.data == "set_max_seller_listings")
async def set_max_seller_listings(callback: CallbackQuery, state: FSMContext):
    """Установка макс. объявлений у продавца"""
    await callback.message.answer(
        "📝 Введите максимальное количество объявлений у продавца:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_max_seller_listings)
    await callback.answer()


@router.message(SettingsStates.waiting_max_seller_listings)
async def process_max_seller_listings(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка макс. объявлений у продавца"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        max_seller_listings = int(message.text)
        if max_seller_listings < 0:
            await message.answer("❌ Количество не может быть отрицательным. Попробуйте снова:")
            return
        
        user = await user_repo.get_user(message.from_user.id)
        user.search_settings['max_seller_listings'] = max_seller_listings
        await user_repo.update_user(user)
        
        await state.clear()
        await message.answer(
            f"✅ Макс. объявлений у продавца установлено: {max_seller_listings}",
            reply_markup=get_main_menu()
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введите целое число:")


@router.callback_query(F.data == "set_seller_year")
async def set_seller_year(callback: CallbackQuery, state: FSMContext):
    """Установка года регистрации продавца"""
    await callback.message.answer(
        "📅 Введите минимальный год регистрации продавца (например, 2020):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_seller_year)
    await callback.answer()


@router.message(SettingsStates.waiting_seller_year)
async def process_seller_year(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка года регистрации"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        year = int(message.text)
        if year < 2000 or year > 2030:
            await message.answer("❌ Введите корректный год (2000-2030):")
            return
        
        user = await user_repo.get_user(message.from_user.id)
        user.search_settings['seller_registration_year'] = year
        await user_repo.update_user(user)
        
        await state.clear()
        await message.answer(
            f"✅ Год регистрации продавца установлен: {year}",
            reply_markup=get_main_menu()
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введите год:")


@router.callback_query(F.data == "set_keywords")
async def set_keywords(callback: CallbackQuery, state: FSMContext):
    """Установка ключевых слов"""
    await callback.message.answer(
        "🔑 Введите ключевые слова через запятую (например: велосипед, автомобиль):\n\n"
        "Или отправьте '-' чтобы очистить ключевые слова",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SettingsStates.waiting_keywords)
    await callback.answer()


@router.message(SettingsStates.waiting_keywords)
async def process_keywords(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка ключевых слов"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    user = await user_repo.get_user(message.from_user.id)
    
    if message.text.strip() == "-":
        user.search_settings['keywords'] = []
        await user_repo.update_user(user)
        await state.clear()
        await message.answer("✅ Ключевые слова очищены", reply_markup=get_main_menu())
        return
    
    keywords = [kw.strip() for kw in message.text.split(',') if kw.strip()]
    user.search_settings['keywords'] = keywords
    await user_repo.update_user(user)
    
    await state.clear()
    await message.answer(
        f"✅ Ключевые слова установлены: {', '.join(keywords)}",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == "save_settings")
async def save_settings(callback: CallbackQuery):
    """Сохранение настроек"""
    await callback.message.answer("✅ Настройки сохранены!", reply_markup=get_main_menu())
    await callback.answer()

