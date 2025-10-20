"""
Планировщик задач для парсинга
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from datetime import datetime
import logging

from core.database import UserRepository
from parser import SubitoParser
from config import PARSE_INTERVAL

logger = logging.getLogger(__name__)


class ParsingScheduler:
    """Планировщик для автоматического парсинга"""
    
    def __init__(self, bot: Bot, user_repo: UserRepository):
        self.bot = bot
        self.user_repo = user_repo
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Запуск планировщика"""
        if not self.is_running:
            # Добавляем задачу парсинга с интервалом из конфига
            self.scheduler.add_job(
                self._parse_for_all_users,
                trigger=IntervalTrigger(seconds=PARSE_INTERVAL),
                id='parse_all_users',
                name='Parse listings for all active users',
                replace_existing=True
            )
            
            # Добавляем задачу проверки подписок
            self.scheduler.add_job(
                self._check_subscriptions,
                trigger=IntervalTrigger(minutes=5),
                id='check_subscriptions',
                name='Check and deactivate expired subscriptions',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Планировщик запущен")
    
    def stop(self):
        """Остановка планировщика"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("🛑 Планировщик остановлен")
    
    async def _parse_for_all_users(self):
        """Парсинг для всех активных пользователей"""
        try:
            logger.info("🔄 Начало цикла парсинга...")
            
            # Получаем список пользователей с активным парсингом
            active_users = await self.user_repo.get_active_parsers()
            
            logger.info(f"📊 Найдено пользователей с активным парсингом: {len(active_users)}")
            
            if not active_users:
                logger.info("ℹ️ Нет активных пользователей для парсинга")
                return
            
            logger.info(f"🔍 Запуск парсинга для {len(active_users)} пользователей")
            
            async with SubitoParser() as parser:
                logger.info("✅ Парсер Subito инициализирован")
                
                for user in active_users:
                    try:
                        logger.info(f"👤 Обработка пользователя {user.telegram_id} (подписка до: {user.subscription_end})")
                        await self._parse_for_user(user, parser)
                    except Exception as e:
                        logger.error(f"❌ Ошибка парсинга для пользователя {user.telegram_id}: {e}")
            
            logger.info("✅ Цикл парсинга завершен")
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в планировщике парсинга: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
    
    async def _parse_for_user(self, user, parser: SubitoParser):
        """Парсинг для конкретного пользователя"""
        try:
            logger.info(f"🔍 Начинаем парсинг для пользователя {user.telegram_id}")
            
            # Получаем настройки поиска
            settings = user.search_settings
            max_listings = settings.get('max_listings', 4)
            
            logger.info(f"⚙️ Настройки пользователя {user.telegram_id}: {settings}")
            logger.info(f"📊 Максимум объявлений: {max_listings}")
            
            # Выполняем поиск
            logger.info(f"🌐 Выполняем поиск на Subito.it...")
            listings = await parser.search_listings(settings, max_results=max_listings)
            
            logger.info(f"📦 Найдено объявлений: {len(listings) if listings else 0}")
            
            if not listings:
                logger.info(f"ℹ️ Объявления не найдены для пользователя {user.telegram_id}")
                return
            
            # Отправляем только новые объявления
            sent_count = 0
            for listing in listings:
                if not user.is_listing_seen(listing.listing_id):
                    logger.info(f"📤 Отправляем новое объявление {listing.listing_id} пользователю {user.telegram_id}")
                    await self._send_listing_to_user(user.telegram_id, listing)
                    await self.user_repo.add_seen_listing(user.telegram_id, listing.listing_id)
                    sent_count += 1
                else:
                    logger.debug(f"⏭️ Объявление {listing.listing_id} уже было отправлено пользователю {user.telegram_id}")
            
            if sent_count > 0:
                logger.info(f"✅ Отправлено {sent_count} новых объявлений пользователю {user.telegram_id}")
            else:
                logger.info(f"ℹ️ Новых объявлений для пользователя {user.telegram_id} не найдено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга для пользователя {user.telegram_id}: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
    
    async def _send_listing_to_user(self, telegram_id: int, listing):
        """Отправка объявления пользователю"""
        try:
            # Формируем текст сообщения
            message_text = listing.format_telegram_message()
            
            # Отправляем с фото если есть
            if listing.image_url:
                try:
                    await self.bot.send_photo(
                        chat_id=telegram_id,
                        photo=listing.image_url,
                        caption=message_text,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    # Если не удалось отправить фото, отправляем только текст
                    logger.warning(f"⚠️ Не удалось отправить фото: {e}")
                    await self.bot.send_message(
                        chat_id=telegram_id,
                        text=message_text,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    )
            else:
                # Отправляем только текст
                await self.bot.send_message(
                    chat_id=telegram_id,
                    text=message_text,
                    parse_mode="HTML",
                    disable_web_page_preview=False
                )
            
            logger.debug(f"📤 Объявление {listing.listing_id} отправлено пользователю {telegram_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки объявления пользователю {telegram_id}: {e}")
    
    async def _check_subscriptions(self):
        """Проверка и деактивация истекших подписок"""
        try:
            # Получаем всех пользователей с активным парсингом
            active_users = await self.user_repo.get_active_parsers()
            
            deactivated_count = 0
            for user in active_users:
                if not user.has_active_subscription():
                    # Деактивируем парсинг
                    await self.user_repo.set_parsing_status(user.telegram_id, False)
                    
                    # Отправляем уведомление
                    try:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=(
                                "⏱ <b>Подписка истекла</b>\n\n"
                                "Ваша подписка закончилась, парсинг автоматически остановлен.\n\n"
                                "Для продолжения работы активируйте новую подписку: /prices"
                            ),
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось отправить уведомление пользователю {user.telegram_id}: {e}")
                    
                    deactivated_count += 1
                    logger.info(f"⏱ Подписка истекла для пользователя {user.telegram_id}")
            
            if deactivated_count > 0:
                logger.info(f"⏱ Деактивировано подписок: {deactivated_count}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки подписок: {e}")

