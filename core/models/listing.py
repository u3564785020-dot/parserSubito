"""
Модель объявления с Subito.it
"""
from datetime import datetime
from typing import Optional, List, Dict, Any


class Listing:
    """Модель объявления с Subito.it"""
    
    def __init__(
        self,
        listing_id: str,
        title: str,
        price: float,
        url: str,
        image_url: Optional[str] = None,
        seller_name: Optional[str] = None,
        seller_url: Optional[str] = None,
        seller_online_status: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        published_date: Optional[str] = None,
        seller_listings_count: int = 0,
        seller_comments_count: int = 0,
        seller_registration_date: Optional[str] = None,
        views_count: int = 0,
        seller_rating: int = 0,
        category: Optional[str] = None,
        additional_images: Optional[List[str]] = None
    ):
        self.listing_id = listing_id
        self.title = title
        self.price = price
        self.url = url
        self.image_url = image_url
        self.seller_name = seller_name
        self.seller_url = seller_url
        self.seller_online_status = seller_online_status
        self.location = location
        self.description = description
        self.published_date = published_date
        self.seller_listings_count = seller_listings_count
        self.seller_comments_count = seller_comments_count
        self.seller_registration_date = seller_registration_date
        self.views_count = views_count
        self.seller_rating = seller_rating
        self.category = category
        self.additional_images = additional_images or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "listing_id": self.listing_id,
            "title": self.title,
            "price": self.price,
            "url": self.url,
            "image_url": self.image_url,
            "seller_name": self.seller_name,
            "seller_url": self.seller_url,
            "seller_online_status": self.seller_online_status,
            "location": self.location,
            "description": self.description,
            "published_date": self.published_date,
            "seller_listings_count": self.seller_listings_count,
            "seller_comments_count": self.seller_comments_count,
            "seller_registration_date": self.seller_registration_date,
            "views_count": self.views_count,
            "seller_rating": self.seller_rating,
            "category": self.category,
            "additional_images": self.additional_images
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Listing':
        """Создание объекта из словаря"""
        return cls(
            listing_id=data["listing_id"],
            title=data["title"],
            price=data["price"],
            url=data["url"],
            image_url=data.get("image_url"),
            seller_name=data.get("seller_name"),
            seller_url=data.get("seller_url"),
            seller_online_status=data.get("seller_online_status"),
            location=data.get("location"),
            description=data.get("description"),
            published_date=data.get("published_date"),
            seller_listings_count=data.get("seller_listings_count", 0),
            seller_comments_count=data.get("seller_comments_count", 0),
            seller_registration_date=data.get("seller_registration_date"),
            views_count=data.get("views_count", 0),
            seller_rating=data.get("seller_rating", 0),
            category=data.get("category"),
            additional_images=data.get("additional_images", [])
        )
    
    def format_telegram_message(self) -> str:
        """Форматирование объявления для отправки в Telegram"""
        message_parts = []
        
        # Название
        message_parts.append(f"🏷️ <b>Название:</b> {self.title}")
        
        # Цена
        message_parts.append(f"💰 <b>Цена:</b> {self.price} €")
        
        # Продавец
        if self.seller_name:
            message_parts.append(f"👤 <b>Продавец:</b> {self.seller_name}")
        
        # Локация
        if self.location:
            message_parts.append(f"🌐 <b>Локация:</b> {self.location}")
        
        # Статус онлайн
        if self.seller_online_status:
            message_parts.append(f"🔴 <b>В сети:</b> {self.seller_online_status}")
        
        # Описание
        if self.description:
            desc = self.description[:300] + "..." if len(self.description) > 300 else self.description
            message_parts.append(f"\n📝 <b>Описание:</b>\n{desc}")
        
        # Дата публикации
        if self.published_date:
            message_parts.append(f"\n📅 <b>Дата публикации:</b> {self.published_date}")
        
        # Статистика продавца
        message_parts.append(f"\n📊 <b>Кол-во объявлений:</b> {self.seller_listings_count}")
        message_parts.append(f"⭐ <b>Кол-во комментариев:</b> {self.seller_comments_count}")
        
        if self.seller_registration_date:
            message_parts.append(f"📅 <b>Дата регистрации продавца:</b> {self.seller_registration_date}")
        
        message_parts.append(f"👁️ <b>Просмотров в Атом:</b> {self.views_count}")
        message_parts.append(f"⭐ <b>Рейтинг продавца:</b> {self.seller_rating}")
        
        # Ссылки
        message_parts.append("\n🔗 <b>Ссылки:</b>")
        if self.image_url:
            message_parts.append(f"📷 <a href='{self.image_url}'>Ссылка на фото</a>")
        message_parts.append(f"📋 <a href='{self.url}'>Ссылка на объявление</a>")
        if self.seller_url:
            message_parts.append(f"👤 <a href='{self.seller_url}'>Ссылка на продавца</a>")
        
        return "\n".join(message_parts)

