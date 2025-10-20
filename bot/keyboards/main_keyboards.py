"""
Клавиатуры для Telegram-бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="🔍 Начать поиск"),
        KeyboardButton(text="👤 Профиль")
    )
    builder.row(
        KeyboardButton(text="❌ Остановить отслеживание"),
        KeyboardButton(text="🔁 Повторить последний запрос")
    )
    builder.row(
        KeyboardButton(text="🔧 Изменить параметры поиска")
    )
    builder.row(
        KeyboardButton(text="💰 ПРАЙС"),
        KeyboardButton(text="🎁 БОНУСНАЯ СИСТЕМА")
    )
    builder.row(
        KeyboardButton(text="👨‍💻 РЕФЕРАЛЬНАЯ ПРОГРАММА")
    )
    builder.row(
        KeyboardButton(text="📧 Support"),
        KeyboardButton(text="💬 FAQ")
    )
    builder.row(
        KeyboardButton(text="📺 Наш канал")
    )
    
    return builder.as_markup(resize_keyboard=True)


def get_admin_menu() -> ReplyKeyboardMarkup:
    """Меню администратора"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="👥 Управление пользователями")
    )
    builder.row(
        KeyboardButton(text="🎁 Добавить бонусные часы"),
        KeyboardButton(text="🚫 Заблокировать пользователя")
    )
    builder.row(
        KeyboardButton(text="📢 Массовая рассылка")
    )
    builder.row(
        KeyboardButton(text="🔙 Вернуться в главное меню")
    )
    
    return builder.as_markup(resize_keyboard=True)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек поиска"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💰 Минимальная цена", callback_data="set_min_price")
    )
    builder.row(
        InlineKeyboardButton(text="💸 Максимальная цена", callback_data="set_max_price")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Количество объявлений", callback_data="set_max_listings")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Максимальный рейтинг", callback_data="set_max_rating")
    )
    builder.row(
        InlineKeyboardButton(text="❤️ Макс. лайков", callback_data="set_max_likes")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Макс. объявлений у продавца", callback_data="set_max_seller_listings")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Дата регистрации", callback_data="set_seller_year")
    )
    builder.row(
        InlineKeyboardButton(text="👁️ Макс. просмотров", callback_data="set_max_views")
    )
    builder.row(
        InlineKeyboardButton(text="🔑 Ключевые слова", callback_data="set_keywords")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить и вернуться", callback_data="save_settings")
    )
    
    return builder.as_markup()


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора подписки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏱ 1 час", callback_data="sub_1h")
    )
    builder.row(
        InlineKeyboardButton(text="📅 24 часа", callback_data="sub_24h")
    )
    builder.row(
        InlineKeyboardButton(text="📆 48 часов", callback_data="sub_48h")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
    )
    
    return builder.as_markup()


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)

