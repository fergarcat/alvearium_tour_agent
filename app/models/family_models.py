# app/models/family_models.py
"""
Модели данных для системы планирования поездок семей
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class FamilyProfile:
    """Профиль семьи для персонализации"""
    # Обязательные поля
    kids_ages: List[int]
    adults_count: int
    budget_level: str  # "low", "medium", "high"
    start_date: str  # "YYYY-MM-DD"
    end_date: str  # "YYYY-MM-DD"
    interests: List[str]  # ["museums", "parks", "food", "shows"]
    origin_country: str
    trip_preferences: str  # Описание пожеланий по поездке
    
    # Дополнительные поля (заполняются позже)
    special_needs: List[str] = None  # ["wheelchair", "stroller", "dietary"]
    language_preference: str = "es"
    accommodation_type: str = None  # "hotel", "apartment", "hostel"
    transportation_preference: str = None  # "public", "car", "walking"
    
    def __post_init__(self):
        if self.special_needs is None:
            self.special_needs = []
        if self.accommodation_type is None:
            self.accommodation_type = "hotel"
        if self.transportation_preference is None:
            self.transportation_preference = "public"
    
    def get_stay_duration(self) -> int:
        """Вычисляет продолжительность пребывания в днях"""
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return (end - start).days
        except:
            return 1
    
    def get_family_size(self) -> int:
        """Возвращает общий размер семьи"""
        return self.adults_count + len(self.kids_ages)
    
    def get_age_group(self) -> str:
        """Определяет возрастную группу детей"""
        if not self.kids_ages:
            return "sin_niños"
        
        max_age = max(self.kids_ages)
        if max_age < 6:
            return "niños_pequeños"
        elif max_age < 12:
            return "niños_medianos"
        else:
            return "niños_mayores"
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует профиль в словарь"""
        return {
            "kids_ages": self.kids_ages,
            "adults_count": self.adults_count,
            "budget_level": self.budget_level,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "interests": self.interests,
            "origin_country": self.origin_country,
            "special_needs": self.special_needs,
            "language_preference": self.language_preference,
            "accommodation_type": self.accommodation_type,
            "transportation_preference": self.transportation_preference,
            "stay_duration": self.get_stay_duration(),
            "family_size": self.get_family_size(),
            "age_group": self.get_age_group()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FamilyProfile':
        """Создает профиль из словаря"""
        return cls(
            kids_ages=data.get("kids_ages", []),
            adults_count=data.get("adults_count", 2),
            budget_level=data.get("budget_level", "medium"),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            interests=data.get("interests", []),
            origin_country=data.get("origin_country", ""),
            special_needs=data.get("special_needs", []),
            language_preference=data.get("language_preference", "es"),
            accommodation_type=data.get("accommodation_type", "hotel"),
            transportation_preference=data.get("transportation_preference", "public")
        )

@dataclass
class PersonalizedQuery:
    """Персонализированный запрос с контекстом семьи"""
    original_query: str
    family_profile: FamilyProfile
    personalized_context: str
    target_agent: str  # "hotels", "restaurants", "activities", "transportation", "all"
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует запрос в словарь"""
        return {
            "original_query": self.original_query,
            "family_profile": self.family_profile.to_dict(),
            "personalized_context": self.personalized_context,
            "target_agent": self.target_agent
        }

@dataclass
class AgentResponse:
    """Стандартный ответ агента"""
    content: str
    agent_type: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует ответ в словарь"""
        return {
            "content": self.content,
            "agent_type": self.agent_type,
            "confidence": self.confidence,
            "metadata": self.metadata
        }

@dataclass
class TripRecommendation:
    """Рекомендация для поездки"""
    title: str
    description: str
    category: str  # "hotel", "restaurant", "activity", "transportation"
    location: str
    price_range: str  # "low", "medium", "high"
    rating: float = 0.0
    family_friendly: bool = True
    age_appropriate: List[int] = None  # Возрасты детей
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.age_appropriate is None:
            self.age_appropriate = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует рекомендацию в словарь"""
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "location": self.location,
            "price_range": self.price_range,
            "rating": self.rating,
            "family_friendly": self.family_friendly,
            "age_appropriate": self.age_appropriate,
            "metadata": self.metadata
        }
