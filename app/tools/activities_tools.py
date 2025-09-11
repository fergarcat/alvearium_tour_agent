# app/tools/activities_tools.py
"""
Инструменты для ActivitiesAgent с Function Calling
"""

from typing import Dict, Any, List
from app.models.activities_models import (
    ActivitiesResponse, Activity, ActivityType, PriceRange, 
    AgeSuitability, BudgetEstimate, AccessibilityLevel
)

def create_activities_plan(
    query: str,
    kids_ages: List[int],
    adults_count: int,
    interests: List[str],
    budget_level: str,
    special_needs: List[str] = None,
    origin_country: str = "Spain",
    travel_dates: str = ""
) -> Dict[str, Any]:
    """
    Создает структурированный план активностей для семьи
    
    Args:
        query: Запрос пользователя
        kids_ages: Возрасты детей
        adults_count: Количество взрослых
        interests: Интересы семьи
        budget_level: Уровень бюджета (low, medium, high)
        special_needs: Особые потребности
        origin_country: Страна происхождения
        travel_dates: Даты поездки
    
    Returns:
        Словарь с структурированными данными плана активностей
    """
    if special_needs is None:
        special_needs = []
    
    # Определяем возрастные группы
    age_groups = _get_age_groups(kids_ages)
    
    # Создаем активности на основе контекста
    activities = _generate_activities_for_family(
        kids_ages, interests, budget_level, special_needs
    )
    
    # Создаем оценку бюджета
    budget_estimate = _create_budget_estimate(activities, budget_level)
    
    # Определяем покрытые интересы
    interests_covered = _get_covered_interests(activities, interests)
    
    # Создаем рекомендации
    weather_considerations = _get_weather_considerations()
    practical_tips = _get_practical_tips()
    
    # Формируем структурированный ответ
    response = ActivitiesResponse(
        activities=activities,
        total_activities=len(activities),
        recommended_duration=_calculate_duration(len(activities)),
        budget_estimate=budget_estimate,
        age_groups=age_groups,
        interests_covered=interests_covered,
        weather_considerations=weather_considerations,
        practical_tips=practical_tips
    )
    
    return response.dict()

def _get_age_groups(kids_ages: List[int]) -> List[str]:
    """Определяет возрастные группы детей"""
    if not kids_ages:
        return ["adults_only"]
    
    groups = []
    for age in kids_ages:
        if age <= 3:
            groups.append("toddlers")
        elif age <= 8:
            groups.append("children")
        elif age <= 12:
            groups.append("pre_teens")
        else:
            groups.append("teens")
    
    return list(set(groups))

def _generate_activities_for_family(
    kids_ages: List[int], 
    interests: List[str], 
    budget_level: str,
    special_needs: List[str]
) -> List[Activity]:
    """Генерирует активности для семьи на основе их профиля"""
    activities = []
    
    # Базовые активности для Мадрида
    base_activities = [
        {
            "name": "Museo del Prado",
            "type": ActivityType.MUSEUM,
            "description": "Museo de arte clásico con actividades familiares y talleres para niños",
            "schedule": "10:00-20:00 (Lunes cerrado)",
            "location": "Paseo del Prado, s/n, 28014 Madrid",
            "price_range": PriceRange.MEDIUM,
            "age_suitability": AgeSuitability(
                suitable=min(kids_ages) >= 5 if kids_ages else True,
                age_range="5+ años",
                notes="Ideal para niños mayores, actividades familiares disponibles"
            ),
            "interests_match": 0.9 if "arte" in interests else 0.3,
            "accessibility": AccessibilityLevel.WHEELCHAIR_ACCESSIBLE
        },
        {
            "name": "Parque del Retiro",
            "type": ActivityType.PARK,
            "description": "Parque histórico con palacio de cristal, estanque y zonas de juego",
            "schedule": "6:00-22:00",
            "location": "Plaza de la Independencia, 7, 28001 Madrid",
            "price_range": PriceRange.FREE,
            "age_suitability": AgeSuitability(
                suitable=True,
                age_range="Todas las edades",
                notes="Perfecto para todas las edades, muchas actividades al aire libre"
            ),
            "interests_match": 0.8 if "naturaleza" in interests else 0.6,
            "accessibility": AccessibilityLevel.STANDARD
        },
        {
            "name": "Museo Nacional de Ciencias Naturales",
            "type": ActivityType.MUSEUM,
            "description": "Museo interactivo con exposiciones sobre naturaleza y ciencia",
            "schedule": "10:00-17:00 (Martes cerrado)",
            "location": "Calle de José Gutiérrez Abascal, 2, 28006 Madrid",
            "price_range": PriceRange.LOW,
            "age_suitability": AgeSuitability(
                suitable=True,
                age_range="Todas las edades",
                notes="Muy interactivo, ideal para niños curiosos"
            ),
            "interests_match": 0.9 if "ciencia" in interests else 0.7,
            "accessibility": AccessibilityLevel.WHEELCHAIR_ACCESSIBLE
        },
        {
            "name": "Planetario de Madrid",
            "type": ActivityType.ENTERTAINMENT,
            "description": "Planetario con proyecciones sobre el espacio y el universo",
            "schedule": "10:00-19:30 (Lunes cerrado)",
            "location": "Parque Tierno Galván, 28045 Madrid",
            "price_range": PriceRange.LOW,
            "age_suitability": AgeSuitability(
                suitable=min(kids_ages) >= 6 if kids_ages else True,
                age_range="6+ años",
                notes="Proyecciones fascinantes para niños mayores"
            ),
            "interests_match": 0.8 if "ciencia" in interests else 0.5,
            "accessibility": AccessibilityLevel.STANDARD
        }
    ]
    
    # Фильтруем и адаптируем активности
    for activity_data in base_activities:
        # Проверяем соответствие возрасту
        if kids_ages and not activity_data["age_suitability"].suitable:
            continue
        
        # Адаптируем под особые потребности
        if special_needs and "ruido" in special_needs and activity_data["type"] == ActivityType.ENTERTAINMENT:
            continue
        
        # Адаптируем под бюджет
        if budget_level == "low" and activity_data["price_range"] == PriceRange.HIGH:
            continue
        
        activities.append(Activity(**activity_data))
    
    # Добавляем дополнительные активности на основе интересов
    if "naturaleza" in interests:
        activities.append(Activity(
            name="Casa de Campo",
            type=ActivityType.PARK,
            description="Gran parque con zoo, teleférico y actividades al aire libre",
            schedule="6:00-22:00",
            location="Casa de Campo, 28011 Madrid",
            price_range=PriceRange.FREE,
            age_suitability=AgeSuitability(suitable=True, age_range="Todas las edades"),
            interests_match=0.9,
            accessibility=AccessibilityLevel.STANDARD
        ))
    
    if "arte" in interests:
        activities.append(Activity(
            name="Museo Reina Sofía",
            type=ActivityType.MUSEUM,
            description="Museo de arte contemporáneo con talleres familiares",
            schedule="10:00-21:00 (Martes cerrado)",
            location="Calle de Santa Isabel, 52, 28012 Madrid",
            price_range=PriceRange.MEDIUM,
            age_suitability=AgeSuitability(
                suitable=min(kids_ages) >= 8 if kids_ages else True,
                age_range="8+ años",
                notes="Arte contemporáneo, talleres especiales para familias"
            ),
            interests_match=0.9,
            accessibility=AccessibilityLevel.WHEELCHAIR_ACCESSIBLE
        ))
    
    return activities

def _create_budget_estimate(activities: List[Activity], budget_level: str) -> BudgetEstimate:
    """Создает оценку бюджета"""
    free_count = len([a for a in activities if a.price_range == PriceRange.FREE])
    total_count = len(activities)
    
    if budget_level == "low":
        return BudgetEstimate(
            range="€0-50",
            per_person="€10-25",
            notes="Enfocado en actividades gratuitas y de bajo costo"
        )
    elif budget_level == "high":
        return BudgetEstimate(
            range="€100-300",
            per_person="€50-150",
            notes="Incluye actividades premium y experiencias especiales"
        )
    else:
        return BudgetEstimate(
            range="€50-150",
            per_person="€25-75",
            notes="Balance entre calidad y precio, incluye actividades variadas"
        )

def _get_covered_interests(activities: List[Activity], interests: List[str]) -> List[str]:
    """Определяет покрытые интересы"""
    if not interests:
        return []
    
    covered = []
    for interest in interests:
        for activity in activities:
            if activity.interests_match > 0.5:
                covered.append(interest)
                break
    
    return covered

def _calculate_duration(activity_count: int) -> str:
    """Рассчитывает рекомендуемую продолжительность"""
    if activity_count <= 2:
        return "1-2 días"
    elif activity_count <= 4:
        return "2-3 días"
    else:
        return "3-5 días"

def _get_weather_considerations() -> List[str]:
    """Возвращает погодные соображения"""
    return [
        "Llevar ropa de abrigo en invierno (diciembre-enero)",
        "Paraguas recomendado en primavera (marzo-mayo)",
        "Protector solar y gorra en verano (junio-agosto)",
        "Verificar horarios en días lluviosos",
        "Actividades al aire libre dependen del clima"
    ]

def _get_practical_tips() -> List[str]:
    """Возвращает практические советы"""
    return [
        "Reservar con antelación para actividades populares",
        "Llevar documentación para descuentos familiares",
        "Verificar horarios de apertura antes de visitar",
        "Considerar transporte público (Metro muy eficiente)",
        "Llevar agua y snacks para los niños",
        "Descargar apps de museos para audioguías"
    ]
