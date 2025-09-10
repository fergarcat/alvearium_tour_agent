# app/tools/personalization_tools.py
"""
Инструменты для React Agent персонализации
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from models.family_models import FamilyProfile

def extract_family_info_tool(query: str) -> str:
    """Извлекает информацию о семье из запроса пользователя"""
    import re
    import json
    
    try:
        extracted_info = {}
        query_lower = query.lower()
        
        # Извлекаем возраст детей - расширенные паттерны
        kids_patterns = [
            # Множественные дети с "y"
            r'(\d+)\s*y\s*(\d+)\s*y\s*(\d+)\s*y\s*(\d+)\s*años?',  # "4 y 5 y 6 y 7 años"
            r'(\d+)\s*y\s*(\d+)\s*y\s*(\d+)\s*años?',              # "4 y 5 y 6 años"
            r'(\d+)\s*y\s*(\d+)\s*años?',                          # "5 y 8 años"
            r'(\d+)\s*y\s*(\d+)',                                  # "5 y 8"
            
            # Список через запятую
            r'(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*años?',          # "4, 5, 6, 7 años"
            r'(\d+),\s*(\d+),\s*(\d+)\s*años?',                   # "4, 5, 6 años"
            r'(\d+),\s*(\d+)\s*años?',                            # "4, 5 años"
            
            # Список через пробел
            r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+años?',             # "4 5 6 7 años"
            r'(\d+)\s+(\d+)\s+(\d+)\s+años?',                     # "4 5 6 años"
            r'(\d+)\s+(\d+)\s+años?',                             # "4 5 años"
            
            # С "de" и "años"
            r'niños?\s*de\s*(\d+)\s*y\s*(\d+)\s*años?',           # "niños de 5 y 8 años"
            r'niños?\s*de\s*(\d+)\s*años?',                       # "niños de 5 años"
            r'niño\s*de\s*(\d+)\s*años?',                         # "niño de 5 años"
            
            # Одиночные дети
            r'(\d+)\s*años?',                                      # "5 años"
            r'niño\s*de\s*(\d+)',                                 # "niño de 5"
            
            # Отрицательные случаи
            r'no\s+tenemos\s+niños?',                             # "no tenemos niños"
            r'sin\s+niños?',                                      # "sin niños"
            r'no\s+hay\s+niños?',                                 # "no hay niños"
        ]
        
        kids_ages = []
        for pattern in kids_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        kids_ages.extend([int(x) for x in match])
                    else:
                        kids_ages.append(int(match))
                break
        
        if kids_ages:
            extracted_info["kids_ages"] = kids_ages
        
        # Извлекаем количество взрослых
        adults_patterns = [
            r'(\d+)\s*adultos?',
            r'(\d+)\s*personas?',
            r'somos\s*(\d+)',
            r'(\d+)\s*adultos?'
        ]
        
        for pattern in adults_patterns:
            match = re.search(pattern, query_lower)
            if match:
                extracted_info["adults_count"] = int(match.group(1))
                break
        
        # Извлекаем бюджет - улучшенные паттерны
        if any(word in query_lower for word in ["bajo", "económico", "barato", "low", "poco dinero", "no tenemos mucho dinero"]):
            extracted_info["budget_level"] = "low"
        elif any(word in query_lower for word in ["alto", "caro", "lujo", "high", "mucho dinero"]):
            extracted_info["budget_level"] = "high"
        elif any(word in query_lower for word in ["medio", "medium", "normal"]):
            extracted_info["budget_level"] = "medium"
        
        # Также проверяем числовые значения бюджета
        budget_numbers = re.findall(r'(\d+)\s*(?:euros?|€|pesos?|\$)', query_lower)
        if budget_numbers:
            budget_amount = int(budget_numbers[0])
            if budget_amount < 500:
                extracted_info["budget_level"] = "low"
            elif budget_amount > 2000:
                extracted_info["budget_level"] = "high"
            else:
                extracted_info["budget_level"] = "medium"
        
        # Извлекаем даты - улучшенные паттерны
        date_patterns = [
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # DD/MM/YYYY
            r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',  # "15 de junio de 2024"
            r'del\s+(\d{1,2})\s+al\s+(\d{1,2})\s+de\s+(\w+)',  # "del 10 al 20 de octubre"
            r'de\s+(\d{1,2})\s+a\s+(\d{1,2})\s+de\s+(\w+)',  # "de 10 a 20 de octubre"
            r'(\d{1,2})\s+de\s+(\w+)',  # "15 de noviembre"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                # Простая обработка дат - в реальном проекте нужна более сложная логика
                extracted_info["travel_dates"] = "fechas_detectadas"
                break
        
        # Извлекаем интересы
        interests = []
        interest_keywords = {
            "museos": ["museo", "museos", "arte", "cultura"],
            "parques": ["parque", "parques", "naturaleza", "verde"],
            "comida": ["comida", "restaurante", "gastronomía", "tapas"],
            "compras": ["compras", "shopping", "tiendas", "mercado"],
            "deportes": ["deporte", "deportes", "fútbol", "tenis"],
            "shows": ["show", "espectáculo", "teatro", "música"]
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                interests.append(interest)
        
        if interests:
            extracted_info["interests"] = interests
        
        # Извлекаем страну происхождения
        countries = ["españa", "méxico", "argentina", "colombia", "venezuela", "chile", "perú", "ecuador"]
        for country in countries:
            if country in query_lower:
                extracted_info["origin_country"] = country.title()
                break
        
        # Извлекаем особые потребности
        special_needs = []
        if any(word in query_lower for word in ["autismo", "autista"]):
            special_needs.append("autismo")
        if any(word in query_lower for word in ["silla", "ruedas", "discapacidad"]):
            special_needs.append("movilidad_reducida")
        if any(word in query_lower for word in ["alergia", "alérgico"]):
            special_needs.append("alergias_alimentarias")
        
        if special_needs:
            extracted_info["special_needs"] = special_needs
        
        # Умная обработка случаев, когда парсинг не сработал
        if not extracted_info:
            # Пытаемся извлечь хотя бы что-то из текста
            numbers = re.findall(r'\d+', query_lower)
            if numbers:
                # Если есть числа, пытаемся понять контекст
                if any(word in query_lower for word in ["niño", "niños", "hijo", "hijos", "hija", "hijas"]):
                    # Контекст детей - берем все числа как возрасты
                    extracted_info["kids_ages"] = [int(n) for n in numbers]
                elif any(word in query_lower for word in ["adulto", "adultos", "persona", "personas", "somos"]):
                    # Контекст взрослых - берем первое число
                    extracted_info["adults_count"] = int(numbers[0])
                elif any(word in query_lower for word in ["año", "años", "edad", "edades"]):
                    # Контекст возраста - берем все числа
                    extracted_info["kids_ages"] = [int(n) for n in numbers]
                elif any(word in query_lower for word in ["presupuesto", "dinero", "euros", "euro", "pesos", "dólares"]):
                    # Контекст бюджета - не извлекаем числа как количество взрослых
                    pass
                elif any(word in query_lower for word in ["octubre", "noviembre", "diciembre", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre"]):
                    # Контекст дат - не извлекаем числа как количество взрослых
                    pass
                else:
                    # Неопределенный контекст - НЕ извлекаем числа как количество взрослых
                    pass
        
        # Возвращаем результат
        if extracted_info:
            return json.dumps(extracted_info, ensure_ascii=False)
        else:
            return json.dumps({"message": "No se pudo extraer información específica del mensaje"}, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({"error": f"Error al extraer información: {str(e)}"}, ensure_ascii=False)

def get_family_profile_tool(family_id: str) -> str:
    """Получает профиль семьи из базы данных"""
    try:
        from models.family_models_supabase import FamilyProfileSupabase
        
        # Очищаем family_id от лишних символов и извлекаем только ID
        family_id = family_id.strip().strip('"')
        
        # Если передана строка вида "family_id = 'value'", извлекаем только value
        if "family_id" in family_id and "=" in family_id:
            # Извлекаем значение после знака равенства
            if "=" in family_id:
                family_id = family_id.split("=")[1].strip().strip('"').strip("'")
        
        print(f"🔍 Очищенный family_id: '{family_id}'")
        
        # Создаем временный профиль для загрузки
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[],
            adults_count=0,
            interests=[],
            origin_country=""
        )
        
        if profile.load_from_supabase(family_id):
            profile_data = {
                "family_id": profile.family_id,
                "kids_ages": profile.kids_ages,
                "adults_count": profile.adults_count,
                "budget_level": profile.budget_level,
                "start_date": profile.start_date,
                "end_date": profile.end_date,
                "interests": profile.interests,
                "origin_country": profile.origin_country,
                "special_needs": profile.special_needs or [],
                "accommodation_preferences": profile.accommodation_type or "",
                "family_size": profile.get_family_size()
            }
            return json.dumps(profile_data, ensure_ascii=False)
        else:
            return json.dumps({"error": "Family profile not found"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Error loading family profile: {str(e)}"}, ensure_ascii=False)

def update_family_profile_tool(profile_data: str) -> str:
    """Обновляет профиль семьи с новой информацией"""
    try:
        data = json.loads(profile_data)
        return f"Perfil actualizado: {data}"
    except:
        return f"Error al actualizar perfil"

def analyze_family_needs_tool(profile_data: str) -> str:
    """Анализирует потребности семьи на основе профиля"""
    try:
        profile = json.loads(profile_data)
        kids_ages = profile.get("kids_ages", [])
        max_age = max(kids_ages) if kids_ages else 0
        
        analysis = {
            "age_group": "niños pequeños" if max_age < 6 else "niños mayores",
            "budget_level": profile.get("budget_level", "medium"),
            "activity_type": "educativo" if "museums" in profile.get("interests", []) else "recreativo",
            "stay_duration": profile.get("stay_duration", 1),
            "family_size": profile.get("adults_count", 2) + len(kids_ages)
        }
        return f"Análisis de necesidades: {analysis}"
    except:
        return "Error al analizar necesidades familiares"

def suggest_personalization_tool(profile_data: str, query: str = "") -> str:
    """Предлагает персонализацию на основе профиля и запроса"""
    try:
        profile = json.loads(profile_data)
        kids_ages = profile.get("kids_ages", [])
        interests = profile.get("interests", [])
        budget = profile.get("budget_level", "medium")
        
        # Определяем фокус персонализации
        if "hotel" in query.lower() or "alojamiento" in query.lower():
            focus = "hoteles familiares"
            target_agent = "hotels"
        elif "restaurant" in query.lower() or "comida" in query.lower():
            focus = "restaurantes familiares"
            target_agent = "restaurants"
        elif "actividad" in query.lower() or "museo" in query.lower() or "parque" in query.lower():
            focus = "actividades familiares"
            target_agent = "activities"
        elif "transporte" in query.lower() or "metro" in query.lower():
            focus = "transporte familiar"
            target_agent = "transportation"
        else:
            focus = "experiencia completa"
            target_agent = "all"
        
        suggestions = {
            "target_agent": target_agent,
            "personalization_focus": focus,
            "age_appropriate": "actividades para niños de " + str(min(kids_ages)) + " a " + str(max(kids_ages)) + " años" if kids_ages else "actividades familiares",
            "budget_appropriate": f"opciones de presupuesto {budget}",
            "interests_based": f"enfocado en {', '.join(interests[:3])}",
            "magic_touch": "consejos mágicos del Ratoncito Pérez"
        }
        return f"Sugerencias de personalización: {suggestions}"
    except:
        return "Error al generar sugerencias"

def calculate_stay_duration_tool(start_date: str, end_date: str) -> str:
    """Вычисляет продолжительность пребывания"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days
        return f"Duración del viaje: {duration} días"
    except:
        return "Error al calcular duración"

def validate_family_profile_tool(profile_data: str) -> str:
    """Валидирует профиль семьи"""
    try:
        profile = json.loads(profile_data)
        
        # Проверяем обязательные поля
        required_fields = ["kids_ages", "adults_count", "budget_level", "start_date", "end_date", "interests", "origin_country"]
        missing_fields = [field for field in required_fields if not profile.get(field)]
        
        if missing_fields:
            return f"Perfil incompleto. Faltan campos: {', '.join(missing_fields)}"
        
        # Проверяем валидность данных
        kids_ages = profile.get("kids_ages", [])
        if not all(0 < age < 18 for age in kids_ages):
            return "Edades de niños inválidas (deben estar entre 1 y 17 años)"
        
        adults_count = profile.get("adults_count", 0)
        if adults_count < 1 or adults_count > 10:
            return "Número de adultos inválido (debe estar entre 1 y 10)"
        
        budget_level = profile.get("budget_level", "")
        if budget_level not in ["low", "medium", "high"]:
            return "Nivel de presupuesto inválido (debe ser low, medium o high)"
        
        return "Perfil válido"
    except:
        return "Error al validar perfil"

def get_family_insights_tool(profile_data: str) -> str:
    """Генерирует инсайты о семье"""
    try:
        profile = json.loads(profile_data)
        kids_ages = profile.get("kids_ages", [])
        interests = profile.get("interests", [])
        budget = profile.get("budget_level", "medium")
        stay_duration = profile.get("stay_duration", 1)
        
        insights = []
        
        # Инсайты по возрасту
        if kids_ages:
            min_age = min(kids_ages)
            max_age = max(kids_ages)
            if max_age < 6:
                insights.append("Familia con niños pequeños - ideal para actividades educativas y parques")
            elif max_age < 12:
                insights.append("Familia con niños medianos - perfecto para museos interactivos y actividades mixtas")
            else:
                insights.append("Familia con niños mayores - pueden disfrutar de actividades más complejas")
        
        # Инсайты по интересам
        if "museums" in interests:
            insights.append("Interés en cultura - recomendar museos familiares y actividades educativas")
        if "parks" in interests:
            insights.append("Amantes de la naturaleza - incluir parques y espacios verdes")
        if "food" in interests:
            insights.append("Gastronomía importante - recomendar restaurantes con menús para niños")
        
        # Инсайты по бюджету
        if budget == "low":
            insights.append("Presupuesto ajustado - priorizar opciones gratuitas y descuentos")
        elif budget == "high":
            insights.append("Presupuesto amplio - pueden acceder a experiencias premium")
        
        # Инсайты по duración
        if stay_duration <= 2:
            insights.append("Viaje corto - concentrar en atracciones principales")
        elif stay_duration >= 5:
            insights.append("Viaje largo - incluir actividades variadas y días de descanso")
        
        return f"Insights familiares: {'; '.join(insights)}"
    except:
        return "Error al generar insights familiares"

# ===== НОВЫЕ ИНСТРУМЕНТЫ ДЛЯ УМНОГО АНАЛИЗА =====

def analyze_trip_requirements_tool(family_data: str, trip_query: str = "") -> str:
    """Анализирует требования к поездке на основе профиля семьи и запроса"""
    try:
        # Если передана строка с параметрами, извлекаем их
        if "=" in family_data and "trip_query" in family_data:
            # Извлекаем trip_query из строки
            if "trip_query" in family_data:
                trip_query_start = family_data.find("trip_query = ") + len("trip_query = ")
                trip_query_end = family_data.find('"', trip_query_start + 1)
                if trip_query_end == -1:
                    trip_query_end = len(family_data)
                trip_query = family_data[trip_query_start:trip_query_end].strip('"')
            
            # Извлекаем family_data из строки
            family_data_start = family_data.find("family_data = ") + len("family_data = ")
            family_data_end = family_data.find(",", family_data_start)
            if family_data_end == -1:
                family_data_end = len(family_data)
            family_data = family_data[family_data_start:family_data_end].strip('"')
        
        # Если family_data не является валидным JSON, создаем базовую структуру
        try:
            family = json.loads(family_data)
        except json.JSONDecodeError:
            # Создаем базовую структуру семьи
            family = {
                "family_id": family_data if family_data else "unknown",
                "kids_ages": [],
                "adults_count": 2,
                "budget_level": "medium",
                "interests": [],
                "special_needs": []
            }
        query_lower = trip_query.lower()
        
        requirements = {
            "trip_type": "general",
            "critical_fields": [],
            "recommendations": []
        }
        
        # Определяем тип поездки
        if "hotel" in query_lower or "alojamiento" in query_lower:
            requirements["trip_type"] = "hotel"
            requirements["critical_fields"] = ["accommodation_preferences", "budget_level"]
        elif "comer" in query_lower or "restaurante" in query_lower:
            requirements["trip_type"] = "restaurant"
            requirements["critical_fields"] = ["dietary_restrictions", "kids_ages"]
        elif "actividad" in query_lower or "actividades" in query_lower:
            requirements["trip_type"] = "activities"
            requirements["critical_fields"] = ["kids_ages", "interests", "special_needs"]
        elif "transporte" in query_lower or "llegar" in query_lower:
            requirements["trip_type"] = "transport"
            requirements["critical_fields"] = ["mobility_restrictions", "family_size"]
        
        # Анализируем профиль семьи
        if family.get("kids_ages"):
            ages = family["kids_ages"]
            if any(age < 3 for age in ages):
                requirements["recommendations"].append("Considerar actividades para bebés")
            if any(3 <= age <= 12 for age in ages):
                requirements["recommendations"].append("Actividades familiares apropiadas")
        
        if family.get("special_needs"):
            requirements["recommendations"].append("Verificar accesibilidad")
        
        return json.dumps(requirements, ensure_ascii=False)
    except Exception as e:
        return f"Error al analizar requisitos: {str(e)}"

def check_missing_information_tool_wrapper(input_str: str) -> str:
    """Обертка для check_missing_information_tool"""
    try:
        # Парсим входную строку
        if "family_profile" in input_str and "trip_type" in input_str:
            # Извлекаем family_profile
            family_profile_start = input_str.find("family_profile = ") + len("family_profile = ")
            family_profile_end = input_str.find(",", family_profile_start)
            if family_profile_end == -1:
                family_profile_end = input_str.find("}", family_profile_start)
            if family_profile_end == -1:
                family_profile_end = len(input_str)
            family_profile = input_str[family_profile_start:family_profile_end].strip()
            
            # Извлекаем trip_type
            trip_type_start = input_str.find("trip_type = ") + len("trip_type = ")
            trip_type_end = input_str.find(",", trip_type_start)
            if trip_type_end == -1:
                trip_type_end = input_str.find("}", trip_type_start)
            if trip_type_end == -1:
                trip_type_end = len(input_str)
            trip_type = input_str[trip_type_start:trip_type_end].strip().strip('"').strip("'")
            
            return check_missing_information_tool(family_profile, trip_type)
        else:
            # Если формат неожиданный, используем всю строку как family_profile
            return check_missing_information_tool(input_str, "general")
    except Exception as e:
        return f"Error parsing input: {str(e)}"

def check_missing_information_tool(family_profile: str, trip_type: str = "") -> str:
    """Проверяет недостающую информацию для конкретного типа поездки"""
    try:
        # Если передана строка с параметрами, извлекаем их
        if "=" in family_profile and "trip_type" in family_profile:
            # Извлекаем trip_type из строки
            if "trip_type" in family_profile:
                trip_type_start = family_profile.find("trip_type = ") + len("trip_type = ")
                trip_type_end = family_profile.find(",", trip_type_start)
                if trip_type_end == -1:
                    trip_type_end = family_profile.find("}", trip_type_start)
                if trip_type_end == -1:
                    trip_type_end = len(family_profile)
                trip_type = family_profile[trip_type_start:trip_type_end].strip().strip('"').strip("'")
            
            # Извлекаем family_profile из строки
            family_profile_start = family_profile.find("family_profile = ") + len("family_profile = ")
            family_profile_end = family_profile.find(",", family_profile_start)
            if family_profile_end == -1:
                family_profile_end = family_profile.find("}", family_profile_start)
            if family_profile_end == -1:
                family_profile_end = len(family_profile)
            family_profile = family_profile[family_profile_start:family_profile_end].strip()
        
        # Если family_profile не является валидным JSON, создаем базовую структуру
        try:
            profile = json.loads(family_profile)
        except json.JSONDecodeError:
            # Создаем базовую структуру семьи
            profile = {
                "family_id": "unknown",
                "kids_ages": [],
                "adults_count": 2,
                "budget_level": "medium",
                "interests": [],
                "special_needs": []
            }
        
        # Критически важные поля для каждого типа поездки
        critical_fields = {
            "hotel": ["accommodation_preferences", "budget_level", "family_size"],
            "restaurant": ["dietary_restrictions", "kids_ages", "special_needs"],
            "activities": ["kids_ages", "interests", "special_needs", "mobility_restrictions"],
            "transport": ["mobility_restrictions", "family_size", "special_needs"],
            "general": ["interests", "budget_level", "kids_ages"]
        }
        
        required_fields = critical_fields.get(trip_type, critical_fields["general"])
        missing_fields = []
        optional_fields = []
        
        for field in required_fields:
            if not profile.get(field) or (isinstance(profile.get(field), list) and len(profile.get(field)) == 0):
                missing_fields.append(field)
            else:
                optional_fields.append(field)
        
        # Проверяем дополнительные поля в зависимости от профиля
        if profile.get("kids_ages") and any(age < 3 for age in profile["kids_ages"]):
            if "baby_facilities" not in profile:
                missing_fields.append("baby_facilities")
        
        if profile.get("special_needs"):
            if "accessibility_requirements" not in profile:
                missing_fields.append("accessibility_requirements")
        
        result = {
            "missing_critical": missing_fields,
            "present_fields": optional_fields,
            "trip_type": trip_type,
            "is_complete": len(missing_fields) == 0
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error al verificar información faltante: {str(e)}"

def determine_information_importance_tool(missing_field: str, trip_context: str = "") -> str:
    """Определяет важность недостающего поля для контекста поездки"""
    try:
        # Матрица важности полей для разных контекстов
        importance_matrix = {
            "accommodation_preferences": {
                "hotel": "critical",
                "restaurant": "low",
                "activities": "medium",
                "transport": "low"
            },
            "dietary_restrictions": {
                "hotel": "medium",
                "restaurant": "critical",
                "activities": "low",
                "transport": "low"
            },
            "kids_ages": {
                "hotel": "high",
                "restaurant": "high",
                "activities": "critical",
                "transport": "medium"
            },
            "special_needs": {
                "hotel": "high",
                "restaurant": "high",
                "activities": "critical",
                "transport": "critical"
            },
            "mobility_restrictions": {
                "hotel": "medium",
                "restaurant": "medium",
                "activities": "critical",
                "transport": "critical"
            },
            "interests": {
                "hotel": "low",
                "restaurant": "medium",
                "activities": "critical",
                "transport": "low"
            }
        }
        
        importance = importance_matrix.get(missing_field, {}).get(trip_context, "medium")
        
        result = {
            "field": missing_field,
            "trip_context": trip_context,
            "importance": importance,
            "should_ask": importance in ["critical", "high"]
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error al determinar importancia: {str(e)}"

def collect_missing_information_tool(missing_fields: str, trip_context: str = "") -> str:
    """Собирает недостающую информацию у пользователя"""
    try:
        # Обрабатываем пустые строки
        if not missing_fields or missing_fields.strip() == "":
            fields = []
        else:
            fields = json.loads(missing_fields)
        
        if not trip_context or trip_context.strip() == "":
            context = {}
        else:
            context = json.loads(trip_context)
        
        questions = []
        
        for field in fields:
            if field == "accommodation_preferences":
                questions.append("¿Qué tipo de alojamiento prefieres? (hotel, apartamento, hostal)")
            elif field == "dietary_restrictions":
                questions.append("¿Tienes alguna restricción dietética? (vegetariano, alergias, etc.)")
            elif field == "kids_ages":
                questions.append("¿Cuáles son las edades de tus hijos? (ej: 5, 8, 12)")
            elif field == "special_needs":
                questions.append("¿Algún miembro de la familia tiene necesidades especiales?")
            elif field == "mobility_restrictions":
                questions.append("¿Hay alguna limitación de movilidad en la familia?")
            elif field == "interests":
                questions.append("¿Qué les interesa más? (museos, parques, comida, shows, compras)")
            elif field == "baby_facilities":
                questions.append("¿Necesitas instalaciones para bebés? (cuna, cambiador, etc.)")
            elif field == "accessibility_requirements":
                questions.append("¿Qué requisitos de accesibilidad necesitas?")
        
        result = {
            "questions": questions,
            "fields_to_collect": fields,
            "trip_context": context.get("trip_type", "general")
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error al recopilar información faltante: {str(e)}"

def route_to_specialized_agent_tool(trip_analysis: str, family_profile: str) -> str:
    """Определяет, к какому специализированному агенту направить запрос"""
    try:
        analysis = json.loads(trip_analysis)
        profile = json.loads(family_profile)
        
        trip_type = analysis.get("trip_type", "general")
        
        # Логика маршрутизации
        agent_mapping = {
            "hotel": "hotel_agent",
            "restaurant": "restaurant_agent", 
            "activities": "activities_agent",
            "transport": "transport_agent",
            "general": "general_agent"
        }
        
        target_agent = agent_mapping.get(trip_type, "general_agent")
        
        # Дополнительная логика на основе профиля семьи
        if profile.get("kids_ages") and any(age < 5 for age in profile["kids_ages"]):
            if trip_type == "activities":
                target_agent = "family_activities_agent"
        
        if profile.get("special_needs"):
            if trip_type in ["hotel", "restaurant", "activities"]:
                target_agent = f"accessible_{trip_type}_agent"
        
        result = {
            "target_agent": target_agent,
            "trip_type": trip_type,
            "routing_reason": f"Basado en tipo de viaje: {trip_type}",
            "family_context": {
                "has_young_children": any(age < 5 for age in profile.get("kids_ages", [])),
                "has_special_needs": bool(profile.get("special_needs")),
                "budget_level": profile.get("budget_level", "medium")
            }
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error al enrutar a agente especializado: {str(e)}"

def sequential_question_tool(user_response: str, family_id: str) -> str:
    """
    Новый инструмент для последовательного сбора информации о семье
    Заменяет сложный промпт простой логикой парсинга
    """
    try:
        import json
        from models.family_models_supabase import FamilyProfileSupabase
        
        # Парсим ответ пользователя
        extracted_info = extract_family_info_tool(user_response)
        info_data = json.loads(extracted_info)
        
        print(f"🔍 Sequential Question Tool: Извлеченная информация: {info_data}")
        
        # Определяем, какая информация была получена
        if "kids_ages" in info_data:
            # Получили информацию о детях, спрашиваем о взрослых
            ages_str = ", ".join(map(str, info_data["kids_ages"]))
            return json.dumps({
                "action": "ask_next_question",
                "question": f"¡Perfecto! 👶 He anotado que tienes niños de las siguientes edades: {ages_str}\n\nAhora necesito saber:\n\n👨‍👩‍👧‍👦 **¿Cuántos adultos viajarán?**\n\n(Por ejemplo: \"Somos 2 adultos\" o \"Viajamos 4 adultos\")",
                "collected_info": {"kids_ages": info_data["kids_ages"]},
                "next_step": "adults_count"
            }, ensure_ascii=False)
        
        elif "adults_count" in info_data:
            # Получили информацию о взрослых, спрашиваем о бюджете
            return json.dumps({
                "action": "ask_next_question", 
                "question": f"¡Excelente! 👨‍👩‍👧‍👦 He anotado que viajan {info_data['adults_count']} adultos.\n\nAhora necesito saber:\n\n💰 **¿Cuál es tu presupuesto aproximado para el viaje?**\n\n- Bajo (económico)\n- Medio (normal)\n- Alto (lujo)\n\n(Por ejemplo: \"Presupuesto medio\" o \"Queremos algo económico\")",
                "collected_info": {"adults_count": info_data["adults_count"]},
                "next_step": "budget_level"
            }, ensure_ascii=False)
        
        elif "budget_level" in info_data:
            # Получили информацию о бюджете, спрашиваем о датах
            return json.dumps({
                "action": "ask_next_question",
                "question": f"¡Genial! 💰 He anotado tu presupuesto: {info_data['budget_level']}\n\nAhora necesito saber:\n\n📅 **¿Cuándo planeas viajar?**\n\n(Por ejemplo: \"Del 15 al 20 de junio\" o \"En julio por una semana\")",
                "collected_info": {"budget_level": info_data["budget_level"]},
                "next_step": "travel_dates"
            }, ensure_ascii=False)
        
        elif "travel_dates" in info_data:
            # Получили информацию о датах, спрашиваем об интересах
            return json.dumps({
                "action": "ask_next_question",
                "question": "¡Perfecto! 📅 He anotado las fechas de tu viaje.\n\nAhora necesito saber:\n\n🎯 **¿Qué les gusta hacer a tu familia?**\n\n(Por ejemplo: \"Museos, parques y comida\" o \"Nos gusta el arte y la naturaleza\")",
                "collected_info": {"travel_dates": info_data["travel_dates"]},
                "next_step": "interests"
            }, ensure_ascii=False)
        
        elif "interests" in info_data:
            # Получили информацию об интересах, спрашиваем о стране
            interests_str = ", ".join(info_data["interests"])
            return json.dumps({
                "action": "ask_next_question",
                "question": f"¡Excelente! 🎯 He anotado tus intereses: {interests_str}\n\nAhora necesito saber:\n\n🌍 **¿De qué país vienen?**\n\n(Por ejemplo: \"España\" o \"México\")",
                "collected_info": {"interests": info_data["interests"]},
                "next_step": "origin_country"
            }, ensure_ascii=False)
        
        elif "origin_country" in info_data:
            # Получили информацию о стране, спрашиваем об особых потребностях
            return json.dumps({
                "action": "ask_next_question",
                "question": f"¡Perfecto! 🌍 He anotado que vienen de {info_data['origin_country']}.\n\nÚltima pregunta:\n\n✨ **¿Tienes alguna preferencia especial para el viaje?**\n\n(Por ejemplo: \"Mi hijo tiene autismo\" o \"Necesitamos silla de ruedas\" o \"No, todo normal\")",
                "collected_info": {"origin_country": info_data["origin_country"]},
                "next_step": "special_needs"
            }, ensure_ascii=False)
        
        elif "special_needs" in info_data:
            # Получили всю информацию, создаем профиль
            return json.dumps({
                "action": "create_profile",
                "message": "¡Perfecto! He recopilado toda la información necesaria.",
                "collected_info": {"special_needs": info_data["special_needs"]},
                "next_step": "profile_creation"
            }, ensure_ascii=False)
        
        else:
            # Не удалось извлечь информацию, просим уточнить
            return json.dumps({
                "action": "ask_clarification",
                "question": "No pude entender tu respuesta. Por favor, responde de manera más específica.\n\n👶 **¿Cuántos niños tienes y qué edades tienen?**\n\n(Por ejemplo: \"Tengo 2 niños de 5 y 8 años\" o \"No tenemos niños\")",
                "collected_info": {},
                "next_step": "kids_ages"
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "action": "error",
            "message": f"Error al procesar tu respuesta: {str(e)}",
            "collected_info": {},
            "next_step": "error"
        }, ensure_ascii=False)


def llm_interpretation_tool(user_response: str, current_question: str, collected_info: str = "{}") -> str:
    """
    Инструмент для интерпретации ответов пользователя с помощью LLM
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
        
        # Инициализируем LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=500
        )
        
        # Создаем промпт для интерпретации
        interpretation_prompt = PromptTemplate(
            template="""Eres un asistente experto en interpretar respuestas de usuarios para recopilar información familiar.

CONTEXTO:
- Pregunta actual: {current_question}
- Información ya recopilada: {collected_info}
- Respuesta del usuario: {user_response}

TAREA:
Interpreta la respuesta del usuario y extrae la información relevante en formato JSON.

CAMPOS POSIBLES:
- kids_ages: array de edades de niños (ej: [5, 8, 12])
- adults_count: número de adultos (ej: 2)
- budget_level: "low", "medium", "high"
- travel_dates: fechas de viaje (ej: "2024-10-15 to 2024-10-20")
- interests: array de intereses (ej: ["museos", "parques"])
- origin_country: país de origen (ej: "España")
- special_needs: array de necesidades especiales (ej: ["autismo"] o [] si no hay)

REGLAS:
1. Si la respuesta es sobre niños, extrae kids_ages
2. Si la respuesta es sobre adultos, extrae adults_count
3. Si la respuesta es sobre presupuesto, extrae budget_level
4. Si la respuesta es sobre fechas, extrae travel_dates
5. Si la respuesta es sobre intereses, extrae interests
6. Si la respuesta es sobre país, extrae origin_country
7. Si la respuesta es sobre necesidades especiales, extrae special_needs:
   - Si menciona necesidades específicas, inclúyelas en el array
   - Si dice "no", "no hay", "no las tengo", "todo normal", devuelve special_needs: []
8. Si no puedes extraer información específica, devuelve solo el campo "message" con una explicación
9. Si la respuesta es confusa o incompleta, devuelve "message" pidiendo aclaración

FORMATO DE RESPUESTA:
Solo devuelve JSON válido, sin texto adicional.

Ejemplos:
- "Tengo 2 niños de 5 y 8 años" → {{"kids_ages": [5, 8]}}
- "Somos 4 adultos" → {{"adults_count": 4}}
- "Presupuesto medio" → {{"budget_level": "medium"}}
- "Del 15 al 20 de octubre" → {{"travel_dates": "2024-10-15 to 2024-10-20"}}
- "No hay necesidades especiales" → {{"special_needs": []}}
- "No, todo normal" → {{"special_needs": []}}
- "No" (sobre necesidades especiales) → {{"special_needs": []}}
- "No entiendo" → {{"message": "No pude entender tu respuesta. Por favor, responde de manera más específica."}}""",
            input_variables=["current_question", "collected_info", "user_response"]
        )
        
        # Вызываем LLM
        chain = interpretation_prompt | llm
        response = chain.invoke({
            "current_question": current_question,
            "collected_info": collected_info,
            "user_response": user_response
        })
        
        # Парсим JSON ответ
        result = json.loads(response.content)
        return json.dumps(result, ensure_ascii=False)
        
    except json.JSONDecodeError:
        # Если LLM вернул невалидный JSON, возвращаем ошибку
        return json.dumps({
            "message": "No pude entender tu respuesta. Por favor, responde de manera más específica."
        }, ensure_ascii=False)
        
    except Exception as e:
        # В случае любой другой ошибки
        return json.dumps({
            "message": f"Error al procesar tu respuesta: {str(e)}"
        }, ensure_ascii=False)
