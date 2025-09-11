# app/services/activities_agent.py
"""
Activities Agent - специализированный агент для планирования развлечений
Реакт-агент, получающий запросы от RouterAgent
"""

import os
import json
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.tools import Tool, StructuredTool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Импортируем Pydantic модели
from app.models.activities_models import ActivitiesResponse, ActivitiesAgentResult
from app.tools.activities_tools import create_activities_plan

# Добавляем путь к проекту для корректных импортов
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class ActivitiesAgent:
    """Специализированный агент для планирования развлечений в Мадриде"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.3
        )
        
        self.activities_database = self._initialize_activities_database()
        
        # Создаем парсер для структурированного вывода
        self.output_parser = PydanticOutputParser(pydantic_object=ActivitiesResponse)
        
        # Добавляем API сервисы
        self.api_services = self._initialize_api_services()
        
        # Создаем инструменты с API возможностями
        self.tools = self._create_enhanced_tools()
        self.prompt = self._create_enhanced_prompt()
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            max_iterations=2,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            early_stopping_method="generate"
        )
        
        print("✅ ActivitiesAgent инициализирован с API функциональностью")
    
    def _initialize_activities_database(self) -> Dict[str, List[Dict]]:
        """Инициализирует базу данных активностей"""
        return {
            "museums": [
                {
                    "name": "Museo del Prado",
                    "age_range": [6, 99],
                    "interests": ["arte", "cultura", "historia"],
                    "duration": 120,
                    "indoor": True,
                    "educational_value": "high",
                    "crowd_level": "high",
                    "best_time": "morning",
                    "price_range": "medium"
                }
            ],
            "parks": [
                {
                    "name": "Parque del Retiro",
                    "age_range": [0, 99],
                    "interests": ["naturaleza", "deporte", "relajacion"],
                    "duration": 180,
                    "indoor": False,
                    "educational_value": "medium",
                    "crowd_level": "medium",
                    "best_time": "morning",
                    "price_range": "free"
                }
            ]
        }
    
    def _initialize_api_services(self) -> Dict[str, Any]:
        """Инициализирует API сервисы"""
        return {
            "google_places": self._init_google_places(),
            "weather": self._init_weather_api(),
            "events": self._init_events_api()
        }
    
    def _init_google_places(self) -> Optional[Dict]:
        """Инициализирует Google Places API"""
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://maps.googleapis.com/maps/api/place"}
        return None
    
    def _init_weather_api(self) -> Optional[Dict]:
        """Инициализирует Weather API"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://api.openweathermap.org/data/2.5"}
        return None
    
    def _init_events_api(self) -> Optional[Dict]:
        """Инициализирует Events API"""
        api_key = os.getenv("EVENTBRITE_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://www.eventbriteapi.com/v3"}
        return None
    
    def _create_enhanced_tools(self) -> List[Tool]:
        """Создает расширенные инструменты с API вызовами"""
        tools = []
        
        # Добавляем API инструменты
        if self.api_services["google_places"]:
            tools.append(Tool(
                name="search_places_api",
                description="""Поиск мест через Google Places API.
                Используй когда нужно найти конкретные места в Мадриде.
                Входные параметры: query (поисковый запрос), place_type (тип места)
                Пример: search_places_api("museos para niños", "museum")""",
                func=self._search_places_api
            ))
            
            tools.append(Tool(
                name="get_place_details_api",
                description="""Получение детальной информации о месте.
                Используй когда нужно узнать больше о конкретном месте.
                Входные параметры: place_id (ID места)
                Пример: get_place_details_api("ChIJN1t_tDeuEmsRUsoyG83frY4")""",
                func=self._get_place_details_api
            ))
        
        if self.api_services["weather"]:
            tools.append(Tool(
                name="check_weather_api",
                description="""Проверка погоды в Мадриде.
                Используй когда нужно учесть погодные условия.
                Входные параметры: date (дата)
                Пример: check_weather_api("2024-01-15")""",
                func=self._check_weather_api
            ))
        
        if self.api_services["events"]:
            tools.append(Tool(
                name="search_events_api",
                description="""Поиск событий и мероприятий.
                Используй когда нужно найти временные события.
                Входные параметры: query (поисковый запрос), date (дата)
                Пример: search_events_api("talleres niños", "2024-01-15")""",
                func=self._search_events_api
            ))
        
        # Добавляем fallback инструмент
        tools.append(StructuredTool.from_function(
            func=create_activities_plan,
            name="create_activities_plan",
            description="Создает план активностей (fallback)",
            return_schema=ActivitiesResponse
        ))
        
        return tools
    
    def _create_enhanced_prompt(self) -> PromptTemplate:
        """Создает расширенный промпт с API возможностями"""
        template = """Ты эксперт по планированию actividades para familias en Madrid.

Tienes acceso a varias herramientas para obtener información actualizada:

HERRAMIENTAS DISPONIBLES:
{tools}

NOMBRES DE HERRAMIENTAS:
{tool_names}

INFORMACIÓN DE LA FAMILIA:
- Edades de los niños: {kids_ages}
- Número de adultos: {adults_count}
- Intereses: {interests}
- Presupuesto: {budget_level}
- Fechas de viaje: {travel_dates}

INSTRUCCIONES:
1. **ANALIZA** la consulta del usuario
2. **DECIDE** qué herramientas necesitas usar
3. **LLAMA** a las herramientas apropiadas para obtener información
4. **PROCESA** la información obtenida
5. **COMBINA** los resultados en un plan coherente
6. **CONSIDERA** el clima, horarios, precios y edad de los niños

EJEMPLO DE RAZONAMIENTO:
- "Necesito encontrar museos para niños de 8 años"
- "Voy a usar search_places_api para buscar museos"
- "Ahora voy a obtener detalles de los museos encontrados"
- "Voy a verificar el clima para recomendar actividades al aire libre"
- "Voy a buscar eventos especiales para esa fecha"

Consulta del usuario: {input}

{agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=[
                "input", "kids_ages", "adults_count", "interests", 
                "budget_level", "travel_dates", "tools", "tool_names", "agent_scratchpad"
            ]
        )
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Главный метод обработки запросов от RouterAgent с Pydantic + Function Calling"""
        try:
            print(f"🎯 ActivitiesAgent: Обработка запроса с Pydantic + Function Calling")
            
            profile = request_data.get('profile', {})
            query = request_data.get('query', 'planificar actividades')
            
            # Извлекаем данные профиля
            kids_ages = profile.get('kids_ages', []) if isinstance(profile, dict) else getattr(profile, 'kids_ages', [])
            adults_count = profile.get('adults_count', 2) if isinstance(profile, dict) else getattr(profile, 'adults_count', 2)
            interests = profile.get('interests', []) if isinstance(profile, dict) else getattr(profile, 'interests', [])
            origin_country = profile.get('origin_country', 'Spain') if isinstance(profile, dict) else getattr(profile, 'origin_country', 'Spain')
            special_needs = profile.get('special_needs', []) if isinstance(profile, dict) else getattr(profile, 'special_needs', [])
            budget_level = profile.get('budget_level', 'medium') if isinstance(profile, dict) else getattr(profile, 'budget_level', 'medium')
            travel_dates = profile.get('travel_dates', '') if isinstance(profile, dict) else f"{getattr(profile, 'start_date', '')} - {getattr(profile, 'end_date', '')}"
            
            context = {
                "input": query,
                "kids_ages": kids_ages,
                "adults_count": adults_count,
                "interests": interests,
                "origin_country": origin_country,
                "special_needs": special_needs,
                "budget_level": budget_level,
                "travel_dates": travel_dates
            }
            
            try:
                # Выполняем агент с Function Calling
                result = self.agent_executor.invoke(context)
                
                # Извлекаем структурированные данные из результата
                structured_data = None
                activities_text = ""
                
                if isinstance(result, dict):
                    output = result.get('output', '')
                    intermediate_steps = result.get('intermediate_steps', [])
                    
                    # Ищем вызов функции create_activities_plan в промежуточных шагах
                    for step in intermediate_steps:
                        if isinstance(step, tuple) and len(step) >= 2:
                            action, observation = step
                            if isinstance(action, dict) and action.get('tool') == 'create_activities_plan':
                                try:
                                    # Парсим результат функции (observation уже является словарем)
                                    if isinstance(observation, dict):
                                        structured_data = ActivitiesResponse(**observation)
                                    else:
                                        structured_data = ActivitiesResponse.parse_raw(observation)
                                    activities_text = self._format_activities_text(structured_data)
                                    print(f"✅ ActivitiesAgent: Структурированные данные получены через Function Calling")
                                    break
                                except Exception as e:
                                    print(f"⚠️ ActivitiesAgent: Ошибка парсинга структурированных данных: {e}")
                                    continue
                    
                    # Если не нашли структурированные данные, используем текстовый вывод
                    if not structured_data and output:
                        activities_text = output
                        print(f"✅ ActivitiesAgent: Используем текстовый вывод")
                
                # Fallback: создаем структурированные данные программно
                if not structured_data:
                    print(f"✅ ActivitiesAgent: Создаем структурированные данные программно")
                    structured_data = self._create_fallback_structured_data(context)
                    activities_text = self._format_activities_text(structured_data)
                
                # Создаем результат с Pydantic валидацией
                agent_result = ActivitiesAgentResult(
                    agent_name="activities",
                    status="success",
                    query=query,
                    family_context=context,
                    activities_text=activities_text,
                    structured_data=structured_data,
                    metadata={
                        "processing_time": "real_time",
                        "confidence": 0.9,
                        "source": "pydantic_function_calling",
                        "validation": "passed"
                    }
                )
                
                return agent_result.dict()

            except Exception as agent_error:
                print(f"⚠️ ActivitiesAgent: Ошибка агента: {agent_error}")
                # Fallback к простому ответу
                activities_text = self._generate_simple_activities_plan(context)
                structured_data = self._parse_activities_response(activities_text, context)
                
                return {
                    "agent_name": "activities",
                    "status": "fallback",
                    "query": query,
                    "family_context": context,
                    "activities_text": activities_text,
                    "structured_data": structured_data,
                    "metadata": {
                        "processing_time": "real_time",
                        "confidence": 0.6,
                        "source": "fallback",
                        "error": str(agent_error)
                    }
                }
            
        except Exception as e:
            print(f"❌ ActivitiesAgent: Ошибка обработки: {e}")
            return {
                "agent_name": "activities",
                "status": "error",
                "query": query,
                "family_context": context,
                "activities_text": f"Lo siento, hubo un error al crear tu plan de actividades: {str(e)}",
                "structured_data": {"activities": [], "error": str(e)},
                "metadata": {
                    "processing_time": "real_time",
                    "confidence": 0.0,
                    "source": "error",
                    "error": str(e)
                }
            }
    
    def _parse_activities_response(self, activities_text: str, context: Dict) -> Dict[str, Any]:
        """Парсит текстовый ответ в структурированные данные"""
        try:
            # Извлекаем основные данные из контекста
            kids_ages = context.get('kids_ages', [])
            budget_level = context.get('budget_level', 'medium')
            interests = context.get('interests', [])
            
            # Парсим активности из текста
            activities = []
            lines = activities_text.split('\n')
            
            current_activity = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Ищем заголовки активностей (содержат цифры или эмодзи)
                if any(indicator in line for indicator in ['**', '###', '1.', '2.', '3.', '4.', '5.', '🎯', '🏛️', '🌳', '🎨']):
                    if current_activity:
                        activities.append(current_activity)
                    
                    # Извлекаем название активности
                    activity_name = line.replace('**', '').replace('###', '').strip()
                    # Убираем номера
                    import re
                    activity_name = re.sub(r'^\d+\.\s*', '', activity_name)
                    
                    current_activity = {
                        "name": activity_name,
                        "type": self._classify_activity_type(activity_name),
                        "description": "",
                        "schedule": "",
                        "location": "",
                        "price_range": self._estimate_price_range(activity_name, budget_level),
                        "age_suitability": self._assess_age_suitability(activity_name, kids_ages),
                        "interests_match": self._assess_interests_match(activity_name, interests),
                        "accessibility": "standard"
                    }
                elif current_activity and line:
                    # Добавляем информацию к текущей активности
                    if 'horario' in line.lower() or 'schedule' in line.lower():
                        current_activity["schedule"] = line
                    elif 'ubicación' in line.lower() or 'location' in line.lower():
                        current_activity["location"] = line
                    elif not current_activity["description"]:
                        current_activity["description"] = line
                    else:
                        current_activity["description"] += " " + line
            
            # Добавляем последнюю активность
            if current_activity:
                activities.append(current_activity)
            
            # Если не удалось извлечь активности, создаем базовые
            if not activities:
                activities = self._generate_default_activities(kids_ages, budget_level, interests)
            
            return {
                "activities": activities,
                "total_activities": len(activities),
                "recommended_duration": self._calculate_recommended_duration(activities),
                "budget_estimate": self._calculate_budget_estimate(activities, budget_level),
                "age_groups": self._get_age_groups(kids_ages),
                "interests_covered": self._get_covered_interests(activities, interests),
                "weather_considerations": self._get_weather_considerations(),
                "practical_tips": self._get_practical_tips()
            }
            
        except Exception as e:
            print(f"⚠️ Ошибка парсинга активностей: {e}")
            return {
                "activities": [],
                "total_activities": 0,
                "error": str(e)
            }
    
    def _classify_activity_type(self, activity_name: str) -> str:
        """Классифицирует тип активности"""
        activity_lower = activity_name.lower()
        if any(word in activity_lower for word in ['museo', 'museum', 'galería']):
            return "museum"
        elif any(word in activity_lower for word in ['parque', 'park', 'jardín']):
            return "park"
        elif any(word in activity_lower for word in ['taller', 'workshop', 'clase']):
            return "workshop"
        elif any(word in activity_lower for word in ['teatro', 'theater', 'espectáculo']):
            return "entertainment"
        elif any(word in activity_lower for word in ['zoo', 'acuario', 'animal']):
            return "nature"
        else:
            return "general"
    
    def _estimate_price_range(self, activity_name: str, budget_level: str) -> str:
        """Оценивает ценовой диапазон активности"""
        activity_lower = activity_name.lower()
        if any(word in activity_lower for word in ['gratis', 'free', 'entrada libre']):
            return "free"
        elif any(word in activity_lower for word in ['museo', 'parque']):
            return "low" if budget_level == "low" else "medium"
        else:
            return "medium" if budget_level == "medium" else "high"
    
    def _assess_age_suitability(self, activity_name: str, kids_ages: List[int]) -> Dict[str, Any]:
        """Оценивает подходящий возраст для активности"""
        if not kids_ages:
            return {"suitable": True, "age_range": "all", "notes": ""}
        
        activity_lower = activity_name.lower()
        min_age = min(kids_ages)
        max_age = max(kids_ages)
        
        if any(word in activity_lower for word in ['museo', 'museum']):
            if min_age < 5:
                return {"suitable": False, "age_range": "5+", "notes": "Demasiado pequeño para museos"}
            elif max_age > 12:
                return {"suitable": True, "age_range": "5-12", "notes": "Ideal para niños"}
            else:
                return {"suitable": True, "age_range": "5-12", "notes": "Perfecto para esta edad"}
        else:
            return {"suitable": True, "age_range": "all", "notes": "Adecuado para todas las edades"}
    
    def _assess_interests_match(self, activity_name: str, interests: List[str]) -> float:
        """Оценивает соответствие интересам семьи (0-1)"""
        if not interests:
            return 0.5
        
        activity_lower = activity_name.lower()
        matches = 0
        
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in activity_lower or any(word in activity_lower for word in interest_lower.split()):
                matches += 1
        
        return matches / len(interests)
    
    def _generate_default_activities(self, kids_ages: List[int], budget_level: str, interests: List[str]) -> List[Dict]:
        """Генерирует базовые активности по умолчанию"""
        activities = [
            {
                "name": "Museo del Prado",
                "type": "museum",
                "description": "Museo de arte clásico con actividades familiares",
                "schedule": "10:00-20:00",
                "location": "Madrid Centro",
                "price_range": "medium",
                "age_suitability": {"suitable": True, "age_range": "5+", "notes": "Ideal para niños mayores"},
                "interests_match": 0.8,
                "accessibility": "standard"
            },
            {
                "name": "Parque del Retiro",
                "type": "park",
                "description": "Parque histórico con palacio de cristal y estanque",
                "schedule": "6:00-22:00",
                "location": "Madrid Centro",
                "price_range": "free",
                "age_suitability": {"suitable": True, "age_range": "all", "notes": "Perfecto para todas las edades"},
                "interests_match": 0.9,
                "accessibility": "standard"
            }
        ]
        return activities
    
    def _calculate_recommended_duration(self, activities: List[Dict]) -> str:
        """Рассчитывает рекомендуемую продолжительность"""
        total_activities = len(activities)
        if total_activities <= 2:
            return "1-2 días"
        elif total_activities <= 4:
            return "2-3 días"
        else:
            return "3-5 días"
    
    def _calculate_budget_estimate(self, activities: List[Dict], budget_level: str) -> Dict[str, str]:
        """Рассчитывает оценку бюджета"""
        free_activities = len([a for a in activities if a.get("price_range") == "free"])
        total_activities = len(activities)
        
        if budget_level == "low":
            return {"range": "€0-50", "per_person": "€10-25", "notes": "Enfocado en actividades gratuitas"}
        elif budget_level == "high":
            return {"range": "€100-300", "per_person": "€50-150", "notes": "Incluye actividades premium"}
        else:
            return {"range": "€50-150", "per_person": "€25-75", "notes": "Balance entre calidad y precio"}
    
    def _get_age_groups(self, kids_ages: List[int]) -> List[str]:
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
    
    def _get_covered_interests(self, activities: List[Dict], interests: List[str]) -> List[str]:
        """Определяет покрытые интересы"""
        if not interests:
            return []
        
        covered = []
        for interest in interests:
            for activity in activities:
                if self._assess_interests_match(activity["name"], [interest]) > 0.5:
                    covered.append(interest)
                    break
        
        return covered
    
    def _get_weather_considerations(self) -> List[str]:
        """Возвращает рекомендации по погоде"""
        return [
            "Llevar ropa de abrigo en invierno",
            "Paraguas recomendado en primavera",
            "Protector solar en verano",
            "Verificar horarios en días lluviosos"
        ]
    
    def _get_practical_tips(self) -> List[str]:
        """Возвращает практические советы"""
        return [
            "Reservar con antelación para actividades populares",
            "Llevar documentación para descuentos familiares",
            "Verificar horarios de apertura",
            "Considerar transporte público"
        ]
    
    def _format_activities_text(self, structured_data: ActivitiesResponse) -> str:
        """Форматирует структурированные данные в читаемый текст"""
        text = f"# 🎯 Plan de Actividades Personalizado\n\n"
        text += f"**Total de actividades:** {structured_data.total_activities}\n"
        text += f"**Duración recomendada:** {structured_data.recommended_duration}\n\n"
        
        for i, activity in enumerate(structured_data.activities, 1):
            text += f"## {i}. {activity.name}\n"
            text += f"**Tipo:** {activity.type.value.title()}\n"
            text += f"**Descripción:** {activity.description}\n"
            if activity.schedule:
                text += f"**Horario:** {activity.schedule}\n"
            if activity.location:
                text += f"**Ubicación:** {activity.location}\n"
            text += f"**Precio:** {activity.price_range.value}\n"
            text += f"**Adecuado para:** {activity.age_suitability.age_range}\n"
            if activity.age_suitability.notes:
                text += f"**Notas:** {activity.age_suitability.notes}\n"
            text += f"**Coincidencia con intereses:** {activity.interests_match:.0%}\n\n"
        
        return text
    
    def _create_fallback_structured_data(self, context: Dict[str, Any]) -> ActivitiesResponse:
        """Создает структурированные данные программно как fallback"""
        try:
            # Используем нашу функцию для создания структурированных данных
            structured_dict = create_activities_plan(
                query=context.get('input', ''),
                kids_ages=context.get('kids_ages', []),
                adults_count=context.get('adults_count', 2),
                interests=context.get('interests', []),
                budget_level=context.get('budget_level', 'medium'),
                special_needs=context.get('special_needs', []),
                origin_country=context.get('origin_country', 'Spain'),
                travel_dates=context.get('travel_dates', '')
            )
            
            return ActivitiesResponse(**structured_dict)
        except Exception as e:
            print(f"⚠️ Ошибка создания fallback данных: {e}")
            # Возвращаем минимальные данные
            from app.models.activities_models import BudgetEstimate
            
            return ActivitiesResponse(
                activities=[],
                total_activities=0,
                recommended_duration="1 día",
                budget_estimate=BudgetEstimate(
                    range="€0-50", 
                    per_person="€10-25", 
                    notes="Presupuesto básico"
                ),
                age_groups=["adults_only"],
                interests_covered=[],
                weather_considerations=["Verificar clima antes de salir"],
                practical_tips=["Planificar con antelación"]
            )
    
    def _create_tools(self) -> List[Tool]:
        """Создает инструменты для агента"""
        return [
            Tool(
                name="search_activities",
                description="Поиск активностей по критериям: возраст, интересы, погода, время",
                func=self._search_activities
            ),
            Tool(
                name="analyze_age_compatibility",
                description="Анализ совместимости активностей с возрастными группами детей",
                func=self._analyze_age_compatibility
            ),
            Tool(
                name="optimize_schedule",
                description="Оптимизация расписания с учетом энергетических пиков детей",
                func=self._optimize_schedule
            )
        ]
    
    def _create_prompt(self) -> PromptTemplate:
        """Создает промпт для реакт-агента"""
        return PromptTemplate(
            template="""Eres un experto agente de actividades familiares en Madrid.

INFORMACIÓN DE LA FAMILIA:
- Edades de los niños: {kids_ages}
- Número de adultos: {adults_count}
- Intereses: {interests}
- País de origen: {origin_country}
- Necesidades especiales: {special_needs}
- Presupuesto: {budget_level}
- Fechas de viaje: {travel_dates}

HERRAMIENTAS DISPONIBLES:
{tools}

NOMBRES DE HERRAMIENTAS:
{tool_names}

OBJETIVOS:
1. Buscar actividades apropiadas para cada edad
2. Crear un horario optimizado
3. Considerar el clima y la temporada
4. Incluir valor educativo
5. Balancear actividades activas y tranquilas

Responde en español y sé específico con horarios y ubicaciones.

Pregunta del usuario: {input}

{agent_scratchpad}""",
            input_variables=["input", "kids_ages", "adults_count", "interests", "origin_country", "special_needs", "budget_level", "travel_dates", "tools", "tool_names", "agent_scratchpad"]
        )
    
    def _search_activities(self, criteria: str) -> str:
        """Поиск активностей по критериям"""
        try:
            criteria_dict = json.loads(criteria) if criteria.startswith('{') else {"age": 8, "interests": ["arte"]}
            matching_activities = []
            
            for category, activities in self.activities_database.items():
                for activity in activities:
                    if self._matches_criteria(activity, criteria_dict):
                        matching_activities.append(activity)
            
            return json.dumps({
                "found_activities": len(matching_activities),
                "activities": matching_activities[:10]
            }, ensure_ascii=False)
            
        except Exception as e:
            return f"Error en búsqueda: {str(e)}"
    
    def _analyze_age_compatibility(self, kids_ages: str) -> str:
        """Анализ совместимости с возрастными группами"""
        try:
            ages = json.loads(kids_ages) if kids_ages.startswith('[') else [8, 12]
            
            analysis = {
                "age_groups": {
                    "toddlers": [age for age in ages if age < 4],
                    "preschoolers": [age for age in ages if 4 <= age < 6],
                    "school_age": [age for age in ages if 6 <= age < 12],
                    "teens": [age for age in ages if age >= 12]
                },
                "recommendations": {
                    "universal_activities": ["Parque del Retiro", "Museo Nacional de Ciencias Naturales"],
                    "age_specific": {
                        "toddlers": ["Parques infantiles", "Zoológico"],
                        "teens": ["Parque Warner", "Museo del Prado"]
                    }
                }
            }
            
            return json.dumps(analysis, ensure_ascii=False)
            
        except Exception as e:
            return f"Error en análisis de edad: {str(e)}"
    
    def _optimize_schedule(self, schedule_data: str) -> str:
        """Оптимизация расписания"""
        try:
            optimized_schedule = {
                "morning": {
                    "time": "09:00-12:00",
                    "activities": ["Museos", "Parques"],
                    "reason": "Alta energía, mejor concentración"
                },
                "afternoon": {
                    "time": "14:00-17:00",
                    "activities": ["Actividades activas", "Entretenimiento"],
                    "reason": "Energía moderada, tiempo para diversión"
                },
                "evening": {
                    "time": "18:00-20:00",
                    "activities": ["Paseos tranquilos", "Cenas familiares"],
                    "reason": "Energía baja, momento de relajación"
                }
            }
            
            return json.dumps(optimized_schedule, ensure_ascii=False)
            
        except Exception as e:
            return f"Error en optimización: {str(e)}"
    
    def _matches_criteria(self, activity: Dict, criteria: Dict) -> bool:
        """Проверяет соответствие активности критериям"""
        if "age" in criteria:
            age = criteria["age"]
            if not (activity["age_range"][0] <= age <= activity["age_range"][1]):
                return False
        
        if "interests" in criteria:
            interests = criteria["interests"]
            if not any(interest in activity["interests"] for interest in interests):
                return False
        
        return True
    
    def _generate_simple_activities_plan(self, context: Dict) -> str:
        """Генерирует простой план активностей как fallback"""
        kids_ages = context.get('kids_ages', [])
        interests = context.get('interests', [])
        
        plan = f"""🎯 **Plan de Actividades para Familia**

**Edades de los niños:** {kids_ages}
**Intereses:** {', '.join(interests)}

### Actividades Recomendadas:

1. **Museo del Prado** - Ideal para todas las edades
   - Horario: 10:00-12:00
   - Actividades familiares disponibles

2. **Parque del Retiro** - Perfecto para niños
   - Horario: 14:00-16:00
   - Palacio de Cristal y Estanque Grande

3. **Museo Nacional de Ciencias Naturales**
   - Horario: 10:00-12:30
   - Exposiciones interactivas

4. **Planetario de Madrid**
   - Horario: 16:00-18:00
   - Proyecciones sobre el espacio

### Consideraciones:
- Llevar ropa de abrigo en diciembre
- Reservar actividades con antelación
- Combinar actividades educativas y recreativas

¿Te gustaría más detalles sobre alguna actividad específica?"""
        
        return plan
    
    # API методы
    def _search_places_api(self, query: str, place_type: str = None) -> str:
        """Поиск мест через Google Places API"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API не настроен"})
            
            # Реальный API вызов
            params = {
                "query": query,
                "location": "40.4168,-3.7038",  # Madrid coordinates
                "radius": 5000,
                "key": self.api_services["google_places"]["api_key"]
            }
            
            if place_type:
                params["type"] = place_type
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/textsearch/json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("results", [])
                
                # Форматируем результаты
                formatted_places = []
                for place in places[:5]:  # Ограничиваем до 5 результатов
                    formatted_places.append({
                        "name": place.get("name"),
                        "place_id": place.get("place_id"),
                        "rating": place.get("rating", 0),
                        "price_level": place.get("price_level", 2),
                        "types": place.get("types", []),
                        "vicinity": place.get("vicinity"),
                        "geometry": place.get("geometry", {})
                    })
                
                return json.dumps({
                    "status": "success",
                    "places": formatted_places,
                    "query": query,
                    "place_type": place_type
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"API error: {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_place_details_api(self, place_id: str) -> str:
        """Получение детальной информации о месте"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API не настроен"})
            
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,rating,price_level,opening_hours,photos,reviews,website,formatted_phone_number,types",
                "key": self.api_services["google_places"]["api_key"]
            }
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/details/json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                return json.dumps({
                    "status": "success",
                    "details": {
                        "name": result.get("name"),
                        "address": result.get("formatted_address"),
                        "rating": result.get("rating", 0),
                        "price_level": result.get("price_level", 2),
                        "opening_hours": result.get("opening_hours", {}),
                        "phone": result.get("formatted_phone_number"),
                        "website": result.get("website"),
                        "reviews": result.get("reviews", [])[:3],  # Последние 3 отзыва
                        "types": result.get("types", [])
                    }
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"API error: {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _check_weather_api(self, date: str) -> str:
        """Проверка погоды"""
        try:
            if not self.api_services["weather"]:
                return json.dumps({"status": "error", "error": "Weather API не настроен"})
            
            # Для демонстрации используем моковые данные
            # В реальности здесь был бы вызов OpenWeatherMap API
            mock_weather = {
                "date": date,
                "temperature": "15°C",
                "condition": "Parcialmente nublado",
                "humidity": "65%",
                "wind": "10 km/h",
                "recommendation": "Ideal para actividades al aire libre"
            }
            
            return json.dumps({
                "status": "success",
                "weather": mock_weather
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _search_events_api(self, query: str, date: str = None) -> str:
        """Поиск событий и мероприятий"""
        try:
            if not self.api_services["events"]:
                return json.dumps({"status": "error", "error": "Events API не настроен"})
            
            # Для демонстрации используем моковые данные
            # В реальности здесь был бы вызов Eventbrite API
            mock_events = [
                {
                    "name": "Taller de Arte para Niños",
                    "date": date or "2024-01-15",
                    "time": "10:00-12:00",
                    "location": "Museo del Prado",
                    "price": "€15",
                    "age_range": "5-12 años"
                },
                {
                    "name": "Visita Guiada Familiar",
                    "date": date or "2024-01-15",
                    "time": "16:00-18:00",
                    "location": "Parque del Retiro",
                    "price": "Gratis",
                    "age_range": "Todas las edades"
                }
            ]
            
            return json.dumps({
                "status": "success",
                "events": mock_events,
                "query": query,
                "date": date
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })

def create_activities_agent() -> ActivitiesAgent:
    """Создает экземпляр ActivitiesAgent для RouterAgent"""
    return ActivitiesAgent()