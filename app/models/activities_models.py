# app/models/activities_models.py
"""
Pydantic модели для ActivitiesAgent с структурированным выводом
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class ActivityType(str, Enum):
    """Типы активностей"""
    MUSEUM = "museum"
    PARK = "park"
    WORKSHOP = "workshop"
    ENTERTAINMENT = "entertainment"
    NATURE = "nature"
    GENERAL = "general"

class PriceRange(str, Enum):
    """Ценовые диапазоны"""
    FREE = "free"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AccessibilityLevel(str, Enum):
    """Уровни доступности"""
    STANDARD = "standard"
    WHEELCHAIR_ACCESSIBLE = "wheelchair_accessible"
    SPECIAL_NEEDS = "special_needs"

class AgeSuitability(BaseModel):
    """Информация о подходящем возрасте"""
    suitable: bool = Field(description="Подходит ли активность для возраста детей")
    age_range: str = Field(description="Подходящий возрастной диапазон")
    notes: Optional[str] = Field(default=None, description="Дополнительные заметки о возрасте")

class Activity(BaseModel):
    """Модель активности"""
    name: str = Field(description="Название активности")
    type: ActivityType = Field(description="Тип активности")
    description: str = Field(description="Описание активности")
    schedule: Optional[str] = Field(default=None, description="Расписание работы")
    location: Optional[str] = Field(default=None, description="Местоположение")
    price_range: PriceRange = Field(description="Ценовой диапазон")
    age_suitability: AgeSuitability = Field(description="Информация о подходящем возрасте")
    interests_match: float = Field(ge=0, le=1, description="Соответствие интересам семьи (0-1)")
    accessibility: AccessibilityLevel = Field(default=AccessibilityLevel.STANDARD, description="Уровень доступности")
    
    @validator('interests_match')
    def validate_interests_match(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('interests_match должен быть между 0 и 1')
        return v

class BudgetEstimate(BaseModel):
    """Оценка бюджета"""
    range: str = Field(description="Диапазон цен (например: €50-150)")
    per_person: str = Field(description="Стоимость на человека")
    notes: Optional[str] = Field(default=None, description="Примечания о бюджете")

class ActivitiesResponse(BaseModel):
    """Структурированный ответ ActivitiesAgent"""
    activities: List[Activity] = Field(description="Список рекомендованных активностей")
    total_activities: int = Field(description="Общее количество активностей")
    recommended_duration: str = Field(description="Рекомендуемая продолжительность поездки")
    budget_estimate: BudgetEstimate = Field(description="Оценка бюджета")
    age_groups: List[str] = Field(description="Покрытые возрастные группы")
    interests_covered: List[str] = Field(description="Покрытые интересы семьи")
    weather_considerations: List[str] = Field(description="Погодные соображения")
    practical_tips: List[str] = Field(description="Практические советы")
    
    @validator('total_activities')
    def validate_total_activities(cls, v, values):
        if 'activities' in values and v != len(values['activities']):
            raise ValueError('total_activities должно соответствовать количеству активностей')
        return v

class ActivitiesAgentResult(BaseModel):
    """Полный результат работы ActivitiesAgent"""
    agent_name: str = Field(default="activities", description="Название агента")
    status: str = Field(description="Статус обработки: success, fallback, error")
    query: str = Field(description="Исходный запрос пользователя")
    family_context: Dict[str, Any] = Field(description="Контекст семьи")
    activities_text: str = Field(description="Текстовое описание активностей")
    structured_data: ActivitiesResponse = Field(description="Структурированные данные")
    metadata: Dict[str, Any] = Field(description="Метаданные обработки")
    
    class Config:
        json_encoders = {
            # Кастомные энкодеры для сложных типов
        }
