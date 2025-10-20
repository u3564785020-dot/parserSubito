"""
Парсер объявлений с Subito.it
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
import re
from urllib.parse import urljoin
from core.models import Listing

logger = logging.getLogger(__name__)


class SubitoParser:
    """Парсер для сайта Subito.it"""
    
    BASE_URL = "https://www.subito.it"
    SEARCH_URL = f"{BASE_URL}/annunci-italia/vendita/usato/"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def __aenter__(self):
        """Создание сессии при входе в контекст"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self.session:
            await self.session.close()
    
    def _build_search_url(self, settings: Dict[str, Any]) -> str:
        """Построение URL для поиска с учетом фильтров"""
        params = []
        
        # Цена
        if settings.get("min_price"):
            params.append(f"ps={settings['min_price']}")
        if settings.get("max_price"):
            params.append(f"pe={settings['max_price']}")
        
        # Ключевые слова
        keywords = settings.get("keywords", [])
        if keywords:
            query = "+".join(keywords)
            url = f"{self.SEARCH_URL}?q={query}"
        else:
            url = self.SEARCH_URL
        
        # Добавляем параметры
        if params:
            separator = "&" if "?" in url else "?"
            url += separator + "&".join(params)
        
        return url
    
    async def search_listings(
        self,
        settings: Dict[str, Any],
        max_results: int = 10
    ) -> List[Listing]:
        """
        Поиск объявлений по заданным параметрам
        
        Args:
            settings: Настройки поиска пользователя
            max_results: Максимальное количество результатов
        
        Returns:
            Список объявлений
        """
        if not self.session:
            raise RuntimeError("Сессия не инициализирована. Используйте async with.")
        
        search_url = self._build_search_url(settings)
        logger.info(f"🔍 Поиск объявлений: {search_url}")
        
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.error(f"❌ Ошибка запроса: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Парсинг списка объявлений
                listings = await self._parse_listings_page(soup, settings, max_results)
                
                logger.info(f"✅ Найдено объявлений: {len(listings)}")
                return listings
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска объявлений: {e}")
            return []
    
    async def _parse_listings_page(
        self,
        soup: BeautifulSoup,
        settings: Dict[str, Any],
        max_results: int
    ) -> List[Listing]:
        """Парсинг страницы со списком объявлений"""
        listings = []
        
        # Поиск карточек объявлений
        # Subito.it использует различные классы, ищем по data-id или другим атрибутам
        items = soup.find_all('div', class_=re.compile(r'item.*card|listing.*item', re.I))
        
        if not items:
            # Альтернативный поиск
            items = soup.find_all('a', href=re.compile(r'/.*\.htm$'))
        
        logger.info(f"📦 Найдено элементов на странице: {len(items)}")
        
        for item in items[:max_results]:
            try:
                listing = await self._parse_listing_card(item)
                if listing and self._matches_filters(listing, settings):
                    # Получаем детальную информацию
                    detailed_listing = await self._fetch_listing_details(listing.url)
                    if detailed_listing:
                        # Проверяем фильтры продавца
                        if self._matches_seller_filters(detailed_listing, settings):
                            listings.append(detailed_listing)
                            if len(listings) >= max_results:
                                break
            except Exception as e:
                logger.error(f"❌ Ошибка парсинга карточки: {e}")
                continue
        
        return listings
    
    async def _parse_listing_card(self, item) -> Optional[Listing]:
        """Парсинг карточки объявления из списка"""
        try:
            # Извлечение URL
            link = item.find('a', href=re.compile(r'/.*\.htm$'))
            if not link:
                link = item if item.name == 'a' else None
            
            if not link or not link.get('href'):
                return None
            
            url = urljoin(self.BASE_URL, link['href'])
            
            # Извлечение ID из URL
            listing_id = url.split('/')[-1].replace('.htm', '').split('-')[-1]
            
            # Извлечение названия
            title_elem = item.find(['h2', 'h3', 'p'], class_=re.compile(r'title|name', re.I))
            title = title_elem.get_text(strip=True) if title_elem else "Без названия"
            
            # Извлечение цены
            price_elem = item.find(['span', 'p', 'div'], class_=re.compile(r'price|euro', re.I))
            price = 0.0
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self._extract_price(price_text)
            
            # Извлечение изображения
            img_elem = item.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.BASE_URL, image_url)
            
            return Listing(
                listing_id=listing_id,
                title=title,
                price=price,
                url=url,
                image_url=image_url
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга карточки: {e}")
            return None
    
    async def _fetch_listing_details(self, url: str) -> Optional[Listing]:
        """Получение детальной информации об объявлении"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Извлечение ID
                listing_id = url.split('/')[-1].replace('.htm', '').split('-')[-1]
                
                # Название
                title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'title|heading', re.I))
                title = title_elem.get_text(strip=True) if title_elem else "Без названия"
                
                # Цена
                price_elem = soup.find(['span', 'div'], class_=re.compile(r'price', re.I))
                price = 0.0
                if price_elem:
                    price = self._extract_price(price_elem.get_text(strip=True))
                
                # Изображение
                img_elem = soup.find('img', class_=re.compile(r'main.*image|gallery.*image', re.I))
                if not img_elem:
                    img_elem = soup.find('img', alt=True)
                image_url = None
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                    if image_url and not image_url.startswith('http'):
                        image_url = urljoin(self.BASE_URL, image_url)
                
                # Описание
                desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|content', re.I))
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Локация
                location_elem = soup.find(['span', 'div'], class_=re.compile(r'location|city|town', re.I))
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                # Информация о продавце
                seller_name = ""
                seller_url = ""
                seller_online_status = ""
                seller_listings_count = 0
                seller_registration_date = ""
                
                seller_elem = soup.find(['div', 'section'], class_=re.compile(r'seller|user|author', re.I))
                if seller_elem:
                    # Имя продавца
                    name_elem = seller_elem.find(['span', 'a', 'p'], class_=re.compile(r'name|username', re.I))
                    if name_elem:
                        seller_name = name_elem.get_text(strip=True)
                        if name_elem.name == 'a' and name_elem.get('href'):
                            seller_url = urljoin(self.BASE_URL, name_elem['href'])
                    
                    # Статус онлайн
                    status_elem = seller_elem.find(['span', 'div'], class_=re.compile(r'online|status|active', re.I))
                    if status_elem:
                        seller_online_status = status_elem.get_text(strip=True)
                    
                    # Количество объявлений
                    listings_elem = seller_elem.find(text=re.compile(r'annunci|pubblicati', re.I))
                    if listings_elem:
                        numbers = re.findall(r'\d+', listings_elem)
                        if numbers:
                            seller_listings_count = int(numbers[0])
                    
                    # Дата регистрации
                    reg_elem = seller_elem.find(text=re.compile(r'dal|da|registrato|pubblica da', re.I))
                    if reg_elem:
                        seller_registration_date = reg_elem.strip()
                
                # Дата публикации
                date_elem = soup.find(['span', 'time'], class_=re.compile(r'date|published|time', re.I))
                published_date = date_elem.get_text(strip=True) if date_elem else ""
                
                # Категория
                category_elem = soup.find(['span', 'a'], class_=re.compile(r'category|breadcrumb', re.I))
                category = category_elem.get_text(strip=True) if category_elem else ""
                
                return Listing(
                    listing_id=listing_id,
                    title=title,
                    price=price,
                    url=url,
                    image_url=image_url,
                    seller_name=seller_name,
                    seller_url=seller_url,
                    seller_online_status=seller_online_status,
                    location=location,
                    description=description,
                    published_date=published_date,
                    seller_listings_count=seller_listings_count,
                    seller_registration_date=seller_registration_date,
                    category=category
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения деталей объявления: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> float:
        """Извлечение числового значения цены"""
        try:
            # Удаляем все кроме цифр и точки/запятой
            price_text = re.sub(r'[^\d,.]', '', price_text)
            # Заменяем запятую на точку
            price_text = price_text.replace(',', '.')
            return float(price_text) if price_text else 0.0
        except:
            return 0.0
    
    def _matches_filters(self, listing: Listing, settings: Dict[str, Any]) -> bool:
        """Проверка соответствия объявления базовым фильтрам"""
        # Проверка цены
        min_price = settings.get("min_price", 0)
        max_price = settings.get("max_price", float('inf'))
        
        if not (min_price <= listing.price <= max_price):
            return False
        
        # Проверка ключевых слов
        keywords = settings.get("keywords", [])
        if keywords:
            title_lower = listing.title.lower()
            if not any(keyword.lower() in title_lower for keyword in keywords):
                return False
        
        return True
    
    def _matches_seller_filters(self, listing: Listing, settings: Dict[str, Any]) -> bool:
        """Проверка соответствия фильтрам продавца"""
        # Максимальное количество объявлений у продавца
        max_seller_listings = settings.get("max_seller_listings", float('inf'))
        if listing.seller_listings_count > max_seller_listings:
            return False
        
        # Год регистрации продавца
        seller_year = settings.get("seller_registration_year")
        if seller_year and listing.seller_registration_date:
            year_match = re.search(r'\d{4}', listing.seller_registration_date)
            if year_match:
                reg_year = int(year_match.group())
                if reg_year < seller_year:
                    return False
        
        return True

