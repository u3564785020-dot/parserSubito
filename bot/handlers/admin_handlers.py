"""
Обработчики административных функций
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.filters import IsAdminFilter
from bot.keyboards import get_admin_menu, get_main_menu, get_cancel_keyboard
from core.database import UserRepository
import logging

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(IsAdminFilter())


class AdminStates(StatesGroup):
    """Состояния для административных функций"""
    waiting_user_id_for_bonus = State()
    waiting_bonus_hours = State()
    waiting_user_id_for_block = State()
    waiting_broadcast_message = State()


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def cmd_statistics(message: Message, user_repo: UserRepository):
    """Просмотр статистики бота"""
    stats = await user_repo.get_statistics()
    
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: {stats.get('total_users', 0)}\n"
        f"✅ Активных подписок: {stats.get('active_subscriptions', 0)}\n"
        f"🔍 Активных парсеров: {stats.get('active_parsers', 0)}\n"
        f"🚫 Заблокированных: {stats.get('blocked_users', 0)}\n"
    )
    
    await message.answer(stats_text, parse_mode="HTML")


@router.message(F.text == "👥 Управление пользователями")
async def cmd_user_management(message: Message):
    """Меню управления пользователями"""
    management_text = (
        "👥 <b>Управление пользователями</b>\n\n"
        "Доступные команды:\n\n"
        "🎁 Добавить бонусные часы - добавить время подписки пользователю\n"
        "🚫 Заблокировать пользователя - ограничить доступ к боту\n"
        "✅ Разблокировать пользователя - восстановить доступ\n\n"
        "Используйте соответствующие кнопки в меню."
    )
    await message.answer(management_text, parse_mode="HTML")


@router.message(F.text == "🎁 Добавить бонусные часы")
@router.message(Command("add_bonus"))
async def cmd_add_bonus_start(message: Message, state: FSMContext):
    """Начало процесса добавления бонусных часов"""
    await message.answer(
        "🎁 <b>Добавление бонусных часов</b>\n\n"
        "Введите @username или telegram_id пользователя:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_user_id_for_bonus)


@router.message(AdminStates.waiting_user_id_for_bonus)
async def process_user_id_for_bonus(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка ID пользователя для бонуса"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_admin_menu())
        return
    
    # Поиск пользователя
    user = None
    if message.text.startswith('@'):
        # Поиск по username
        user = await user_repo.get_user_by_username(message.text)
    else:
        # Поиск по ID
        try:
            telegram_id = int(message.text)
            user = await user_repo.get_user(telegram_id)
        except ValueError:
            await message.answer("❌ Неверный формат. Введите @username или числовой ID:")
            return
    
    if not user:
        await message.answer(
            "❌ Пользователь не найден.\n\n"
            "Попробуйте снова или отправьте '❌ Отмена':"
        )
        return
    
    # Сохраняем ID пользователя в состояние
    await state.update_data(target_user_id=user.telegram_id)
    
    await message.answer(
        f"✅ Пользователь найден: {user.first_name or 'Без имени'} (ID: {user.telegram_id})\n\n"
        "Введите количество часов для добавления:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_bonus_hours)


@router.message(AdminStates.waiting_bonus_hours)
async def process_bonus_hours(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка количества бонусных часов"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_admin_menu())
        return
    
    try:
        hours = int(message.text)
        if hours <= 0:
            await message.answer("❌ Количество часов должно быть больше 0. Попробуйте снова:")
            return
        
        # Получаем ID пользователя из состояния
        data = await state.get_data()
        target_user_id = data.get('target_user_id')
        
        # Добавляем часы
        success = await user_repo.add_subscription_hours(target_user_id, hours)
        
        if success:
            await message.answer(
                f"✅ Успешно добавлено {hours} час(ов) пользователю {target_user_id}",
                reply_markup=get_admin_menu()
            )
            logger.info(f"✅ Администратор добавил {hours}ч пользователю {target_user_id}")
        else:
            await message.answer(
                "❌ Ошибка при добавлении часов",
                reply_markup=get_admin_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите целое число:")


@router.message(F.text == "🚫 Заблокировать пользователя")
@router.message(Command("block_user"))
async def cmd_block_user_start(message: Message, state: FSMContext):
    """Начало процесса блокировки пользователя"""
    await message.answer(
        "🚫 <b>Блокировка пользователя</b>\n\n"
        "Введите @username или telegram_id пользователя для блокировки:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_user_id_for_block)


@router.message(AdminStates.waiting_user_id_for_block)
async def process_user_id_for_block(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка ID пользователя для блокировки"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_admin_menu())
        return
    
    # Поиск пользователя
    user = None
    if message.text.startswith('@'):
        user = await user_repo.get_user_by_username(message.text)
    else:
        try:
            telegram_id = int(message.text)
            user = await user_repo.get_user(telegram_id)
        except ValueError:
            await message.answer("❌ Неверный формат. Введите @username или числовой ID:")
            return
    
    if not user:
        await message.answer("❌ Пользователь не найден. Попробуйте снова:")
        return
    
    # Блокируем пользователя
    success = await user_repo.block_user(user.telegram_id)
    
    if success:
        await message.answer(
            f"✅ Пользователь {user.first_name or 'Без имени'} (ID: {user.telegram_id}) заблокирован",
            reply_markup=get_admin_menu()
        )
        logger.info(f"🚫 Администратор заблокировал пользователя {user.telegram_id}")
    else:
        await message.answer(
            "❌ Ошибка при блокировке пользователя",
            reply_markup=get_admin_menu()
        )
    
    await state.clear()


@router.message(F.text == "📢 Массовая рассылка")
@router.message(Command("broadcast"))
async def cmd_broadcast_start(message: Message, state: FSMContext):
    """Начало процесса массовой рассылки"""
    await message.answer(
        "📢 <b>Массовая рассылка</b>\n\n"
        "Введите сообщение для отправки всем пользователям:\n\n"
        "⚠️ Сообщение будет отправлено ВСЕМ пользователям бота!",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_broadcast_message)


@router.message(AdminStates.waiting_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext, user_repo: UserRepository):
    """Обработка сообщения для рассылки"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_admin_menu())
        return
    
    broadcast_text = message.text
    
    # Получаем всех пользователей
    all_users = await user_repo.get_all_users()
    
    if not all_users:
        await message.answer("❌ Нет пользователей для рассылки", reply_markup=get_admin_menu())
        await state.clear()
        return
    
    # Отправляем сообщение
    await message.answer(f"📤 Начинаю рассылку для {len(all_users)} пользователей...")
    
    success_count = 0
    failed_count = 0
    
    for user in all_users:
        try:
            await message.bot.send_message(
                chat_id=user.telegram_id,
                text=f"📢 <b>Сообщение от администратора:</b>\n\n{broadcast_text}",
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning(f"⚠️ Не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
    
    result_text = (
        f"✅ Рассылка завершена!\n\n"
        f"📤 Отправлено: {success_count}\n"
        f"❌ Не удалось отправить: {failed_count}"
    )
    
    await message.answer(result_text, reply_markup=get_admin_menu())
    await state.clear()
    
    logger.info(f"📢 Массовая рассылка завершена: {success_count} успешно, {failed_count} ошибок")


@router.message(Command("unblock_user"))
async def cmd_unblock_user(message: Message, user_repo: UserRepository):
    """Разблокировка пользователя (через команду)"""
    # Формат: /unblock_user 123456789
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer(
            "❌ Использование: /unblock_user <telegram_id или @username>"
        )
        return
    
    user_identifier = args[1]
    
    # Поиск пользователя
    user = None
    if user_identifier.startswith('@'):
        user = await user_repo.get_user_by_username(user_identifier)
    else:
        try:
            telegram_id = int(user_identifier)
            user = await user_repo.get_user(telegram_id)
        except ValueError:
            await message.answer("❌ Неверный формат ID")
            return
    
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    # Разблокируем
    success = await user_repo.unblock_user(user.telegram_id)
    
    if success:
        await message.answer(f"✅ Пользователь {user.telegram_id} разблокирован")
        logger.info(f"✅ Администратор разблокировал пользователя {user.telegram_id}")
    else:
        await message.answer("❌ Ошибка при разблокировке")


@router.message(Command("test_parse"))
async def cmd_test_parse(message: Message, user_repo: UserRepository):
    """Тестовый запуск парсинга для администратора"""
    from bot.utils import ParsingScheduler
    from aiogram import Bot
    
    # Получаем бота из контекста
    bot = message.bot
    
    # Создаем временный планировщик для тестирования
    scheduler = ParsingScheduler(bot, user_repo)
    
    await message.answer("🧪 Запускаю тестовый парсинг...")
    
    try:
        # Запускаем один цикл парсинга
        await scheduler._parse_for_all_users()
        await message.answer("✅ Тестовый парсинг завершен. Проверьте логи.")
    except Exception as e:
        await message.answer(f"❌ Ошибка тестового парсинга: {e}")
        logger.error(f"❌ Ошибка тестового парсинга: {e}")


@router.message(Command("parse_status"))
async def cmd_parse_status(message: Message, user_repo: UserRepository):
    """Проверка статуса парсинга"""
    # Получаем всех пользователей с активным парсингом
    active_users = await user_repo.get_active_parsers()
    
    if not active_users:
        await message.answer("ℹ️ Нет пользователей с активным парсингом")
        return
    
    status_text = f"📊 <b>Статус парсинга</b>\n\n"
    status_text += f"👥 Активных парсеров: {len(active_users)}\n\n"
    
    for user in active_users:
        subscription_status = "✅ Активна" if user.has_active_subscription() else "❌ Истекла"
        status_text += (
            f"👤 <b>Пользователь {user.telegram_id}</b>\n"
            f"📅 Подписка: {subscription_status}\n"
            f"⏰ До: {user.subscription_end}\n"
            f"🔍 Парсинг: {'✅ Активен' if user.parsing_active else '❌ Неактивен'}\n\n"
        )
    
    await message.answer(status_text, parse_mode="HTML")
