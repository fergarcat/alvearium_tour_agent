# app/models/__init__.py
"""
Модели данных для системы планирования поездок
"""

from .family_models import (
    FamilyProfile,
    PersonalizedQuery,
    AgentResponse,
    TripRecommendation
)

__all__ = [
    "FamilyProfile",
    "PersonalizedQuery", 
    "AgentResponse",
    "TripRecommendation"
]
