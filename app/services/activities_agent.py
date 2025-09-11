# app/services/activities_agent.py
"""
Activities Agent - specialized agent for entertainment planning
React agent that receives requests from RouterAgent
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

# Import Pydantic models
from app.models.activities_models import ActivitiesResponse, ActivitiesAgentResult
from app.tools.activities_tools import create_activities_plan

# Add project path for correct imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class ActivitiesAgent:
    """Specialized agent for entertainment planning in Madrid"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.3
        )
        
        # Удалена мок база данных - используем только API
        
        # Create parser for structured output
        self.output_parser = PydanticOutputParser(pydantic_object=ActivitiesResponse)
        
        # Add API services
        self.api_services = self._initialize_api_services()
        
        # Create tools with API capabilities
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
            early_stopping_method="force"
        )
        
        print("✅ ActivitiesAgent инициализирован с API функциональностью")
    
    # Удален метод _initialize_activities_database - используем только API
    
    def _initialize_api_services(self) -> Dict[str, Any]:
        """Initialize API services"""
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
        
        # Добавляем API инструменты (ПРИОРИТЕТ 1)
        if self.api_services["google_places"]:
            tools.append(Tool(
                name="search_places_api",
                description="""[ПРИОРИТЕТ 1] Поиск мест через Google Places API.
                ОБЯЗАТЕЛЬНО используй ПЕРВЫМ для поиска мест в Мадриде.
                Входные параметры: query (поисковый запрос), place_type (тип места)
                Формат: search_places_api("museos para niños", "museum")
                Возвращает: список мест с рейтингами, ценами, типами""",
                func=self._search_places_api
            ))
            
            tools.append(Tool(
                name="get_place_details_api",
                description="""[ПРИОРИТЕТ 1] Получение детальной информации о месте.
                Используй ПОСЛЕ search_places_api для получения полной информации.
                Входные параметры: place_id (ID места из search_places_api)
                Формат: get_place_details_api("ChIJN1t_tDeuEmsRUsoyG83frY4")
                Возвращает: детали, часы работы, отзывы, контакты""",
                func=self._get_place_details_api
            ))
        
        if self.api_services["weather"]:
            tools.append(Tool(
                name="check_weather_api",
                description="""[ПРИОРИТЕТ 1] Проверка погоды в Мадриде.
                ОБЯЗАТЕЛЬНО используй для рекомендации активностей на улице.
                Входные параметры: date (дата в формате YYYY-MM-DD)
                Формат: check_weather_api("2024-01-15")
                Возвращает: температуру, условия, рекомендации""",
                func=self._check_weather_api
            ))
        
        if self.api_services["events"]:
            tools.append(Tool(
                name="search_events_api",
                description="""[ПРИОРИТЕТ 1] Поиск событий и мероприятий.
                Используй для поиска временных событий и мероприятий.
                Входные параметры: query (поисковый запрос), date (дата)
                Формат: search_events_api("talleres niños", "2024-01-15")
                Возвращает: события с датами, временем, ценами""",
                func=self._search_events_api
            ))
        
        # Добавляем fallback инструмент (ПРИОРИТЕТ 2 - только если API недоступны)
        tools.append(StructuredTool.from_function(
            func=create_activities_plan,
            name="create_activities_plan",
            description="""[ПРИОРИТЕТ 2] Создает план активностей (fallback).
            Используй ТОЛЬКО если API недоступны или не дали результатов.
            Входные параметры: query, kids_ages, adults_count, interests, budget_level, special_needs, origin_country, travel_dates
            Формат: create_activities_plan(query="actividades", kids_ages=[8, 12], adults_count=2, interests=["arte"], budget_level="medium", special_needs=[], origin_country="Spain", travel_dates="2024-01-15")
            Возвращает: структурированный план активностей""",
            return_schema=ActivitiesResponse
        ))
        
        return tools
    
    def _force_api_usage(self, context: Dict[str, Any]) -> None:
        """Принудительно проверяет и использует API для получения актуальных данных"""
        try:
            print("🔍 ActivitiesAgent: Принудительная проверка API...")
            
            # Проверяем доступность API
            api_available = {
                "google_places": self.api_services["google_places"] is not None,
                "weather": self.api_services["weather"] is not None,
                "events": self.api_services["events"] is not None
            }
            
            print(f"📊 API статус: {api_available}")
            
            # Если есть API, добавляем СТРОГИЕ инструкции в контекст
            if any(api_available.values()):
                # Создаем персонализированные инструкции с учетом возраста детей
                kids_ages = context.get('kids_ages', [])
                travel_dates = context.get('travel_dates', '2024-01-15')
                input_query = context.get('input', 'actividades para niños')
                
                if kids_ages:
                    age_info = f" para niños de {min(kids_ages)}-{max(kids_ages)} años"
                    personalized_query = f"{input_query}{age_info}"
                else:
                    personalized_query = input_query
                
                context["api_instructions"] = f"""
                🚨 КРИТИЧЕСКИ ВАЖНО: API ДОСТУПНЫ! ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ ИХ!
                
                ДОСТУПНЫЕ API: {[k for k, v in api_available.items() if v]}
                👶 ВОЗРАСТ ДЕТЕЙ: {kids_ages}
                📅 ДАТЫ ПОЕЗДКИ: {travel_dates}
                
                ПОРЯДОК ДЕЙСТВИЙ (ОБЯЗАТЕЛЬНО):
                1. **СНАЧАЛА** вызови search_places_api с запросом "{personalized_query}"
                2. **ЗАТЕМ** вызови check_weather_api для даты "{travel_dates}"
                3. **ПОТОМ** вызови search_events_api для поиска событий с учетом возраста
                4. **ТОЛЬКО ПОСЛЕ** всех API вызовов используй create_activities_plan
                
                ЗАПРЕЩЕНО:
                ❌ Использовать create_activities_plan БЕЗ вызова API
                ❌ Пропускать API вызовы
                ❌ Использовать fallback данные
                ❌ Игнорировать возраст детей в запросах
                
                НАЧНИ С: search_places_api("{personalized_query}", "amusement_park|museum|park|zoo")
                """
                
                # Добавляем флаг принуждения
                context["force_api_first"] = True
                print("🚨 ActivitiesAgent: API принуждение активировано!")
            else:
                context["api_instructions"] = """
                ⚠️ API недоступны, используй create_activities_plan как fallback
                """
                context["force_api_first"] = False
                
        except Exception as e:
            print(f"⚠️ Ошибка принудительного использования API: {e}")
    
    def _force_api_calls(self, context: Dict[str, Any]) -> None:
        """Принудительно вызывает API для получения данных"""
        try:
            print("🚨 ActivitiesAgent: Принудительный вызов API...")
            
            # Извлекаем данные из контекста для персонализации
            kids_ages = context.get('kids_ages', [])
            travel_dates = context.get('travel_dates', '2024-01-15')
            input_query = context.get('input', 'actividades para niños')
            
            # Создаем простой запрос для Google Places API
            if kids_ages:
                # Упрощаем запрос для лучшего понимания API
                personalized_query = f"actividades niños Madrid {min(kids_ages)} {max(kids_ages)} años"
            else:
                personalized_query = "actividades niños Madrid"
            
            print(f"👶 Персонализированный запрос: {personalized_query}")
            
            # Принудительно вызываем Google Places API
            if self.api_services["google_places"]:
                print("🔍 Принудительный вызов search_places_api...")
                places_result = self._search_places_api(personalized_query, "amusement_park|museum|park|zoo")
                print(f"📊 Результат search_places_api: {places_result[:200]}...")
                
                # Добавляем результат в контекст
                context["forced_places_data"] = places_result
            
            # Принудительно вызываем Weather API
            if self.api_services["weather"]:
                print("🌤️ Принудительный вызов check_weather_api...")
                # Используем реальные даты поездки
                weather_date = travel_dates.split(' - ')[0] if ' - ' in travel_dates else travel_dates
                weather_result = self._check_weather_api(weather_date)
                print(f"📊 Результат check_weather_api: {weather_result[:200]}...")
                
                # Добавляем результат в контекст
                context["forced_weather_data"] = weather_result
            
            # Принудительно вызываем Events API
            if self.api_services["events"]:
                print("🎪 Принудительный вызов search_events_api...")
                # Создаем запрос с учетом возраста детей
                if kids_ages:
                    events_query = f"talleres niños Madrid {min(kids_ages)} {max(kids_ages)} años"
                else:
                    events_query = "talleres niños Madrid"
                events_result = self._search_events_api(events_query, weather_date)
                print(f"📊 Результат search_events_api: {events_result[:200]}...")
                
                # Добавляем результат в контекст
                context["forced_events_data"] = events_result
            
            print("✅ ActivitiesAgent: API принудительно вызваны с учетом возраста детей!")
            
        except Exception as e:
            print(f"⚠️ Ошибка принудительного вызова API: {e}")
    
    def _create_enhanced_prompt(self) -> PromptTemplate:
        """Создает расширенный промпт с API возможностями по схеме ReAct"""
        template = """Eres un experto agente de actividades familiares en Madrid que sigue el patrón ReAct (Reasoning + Acting).

INFORMACIÓN DE LA FAMILIA:
- Edades de los niños: {kids_ages}
- Número de adultos: {adults_count}
- Intereses: {interests}
- Presupuesto: {budget_level}
- Fechas de viaje: {travel_dates}

INSTRUCCIONES API:
{api_instructions}

DATOS API OBTENIDOS (si están disponibles):
- Lugares: {forced_places_data}
- Clima: {forced_weather_data}
- Eventos: {forced_events_data}

HERRAMIENTAS DISPONIBLES:
{tools}

NOMBRES DE HERRAMIENTAS:
{tool_names}

PRIORIDAD DE HERRAMIENTAS (ORDEN OBLIGATORIO):
1. **PRIMERA PRIORIDAD**: API externas (search_places_api, get_place_details_api, check_weather_api, search_events_api)
2. **SEGUNDA PRIORIDAD**: create_activities_plan (solo si API no disponibles)

PATRÓN DE RAZONAMIENTO ReAct:
**Thought**: [Analiza qué necesitas hacer y por qué]
**Action**: [Nombre de la herramienta a usar]
**Action Input**: [Parámetros para la herramienta]
**Observation**: [Resultado de la herramienta]
**Thought**: [Analiza el resultado y decide el siguiente paso]
**Action**: [Siguiente herramienta si es necesario]
**Action Input**: [Parámetros]
**Observation**: [Resultado]
**Final Answer**: [Respuesta final estructurada]

REGLAS ESTRICTAS:
1. **SIEMPRE** intenta usar API externas PRIMERO
2. **NUNCA** uses create_activities_plan si hay API disponibles
3. **COMBINA** información de múltiples API cuando sea posible
4. **VERIFICA** clima antes de recomendar actividades al aire libre
5. **BUSCA** eventos específicos para las fechas de viaje
6. **OBTÉN** detalles completos de lugares recomendados

🚨 VERIFICACIÓN OBLIGATORIA:
- Si ves "force_api_first": true, DEBES usar API PRIMERO
- Si ves "API ДОСТУПНЫ", DEBES usar API PRIMERO
- NO puedes usar create_activities_plan sin antes llamar a las API

EJEMPLO DE FLUJO CORRECTO:
**Thought**: Necesito encontrar museos para niños de 8 años en Madrid
**Action**: search_places_api
**Action Input**: {{"query": "museos para niños Madrid", "place_type": "museum"}}
**Observation**: [Resultado de la API]
**Thought**: Ahora necesito verificar el clima para recomendar actividades
**Action**: check_weather_api
**Action Input**: {{"date": "2024-01-15"}}
**Observation**: [Datos del clima]
**Thought**: Voy a buscar eventos especiales para esa fecha
**Action**: search_events_api
**Action Input**: {{"query": "talleres niños", "date": "2024-01-15"}}
**Observation**: [Eventos encontrados]
**Final Answer**: [Plan completo basado en datos reales]

Consulta del usuario: {input}

{agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=[
                "input", "kids_ages", "adults_count", "interests", 
                "budget_level", "travel_dates", "api_instructions", "forced_places_data", 
                "forced_weather_data", "forced_events_data", "tools", "tool_names", "agent_scratchpad"
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
            # Загружаем данные поездки
            if isinstance(profile, dict):
                # Если profile - это словарь от RouterAgent, извлекаем даты напрямую
                budget_level = profile.get('budget_level', 'medium')
                start_date = profile.get('start_date', '')
                end_date = profile.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
                print(f"📅 ActivitiesAgent: Получены даты от RouterAgent: {travel_dates}")
            else:
                # Если profile - это объект FamilyProfileSupabase, загружаем данные поездки
                travel_data = profile.load_travel_dates(family_id)
                budget_level = travel_data.get('budget_level', 'medium')
                start_date = travel_data.get('start_date', '')
                end_date = travel_data.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
                print(f"📅 ActivitiesAgent: Загружены даты из travel_requests: {travel_dates}")
            
            context = {
                "input": query,
                "kids_ages": kids_ages,
                "adults_count": adults_count,
                "interests": interests,
                "origin_country": origin_country,
                "special_needs": special_needs,
                "budget_level": budget_level,
                "travel_dates": travel_dates,
                "api_instructions": "",  # Будет заполнено в _force_api_usage
                "forced_places_data": "",  # Будет заполнено в _force_api_calls
                "forced_weather_data": "",  # Будет заполнено в _force_api_calls
                "forced_events_data": ""  # Будет заполнено в _force_api_calls
            }
            
            try:
                # Проверяем доступность API и принудительно используем их
                self._force_api_usage(context)
                
                # Принудительно вызываем API если они доступны
                if context.get("force_api_first", False):
                    print("🚨 ActivitiesAgent: Принудительный вызов API...")
                    self._force_api_calls(context)
                
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
                
                # Если нет структурированных данных, создаем минимальные данные
                if not structured_data:
                    print(f"⚠️ ActivitiesAgent: Нет структурированных данных, создаем минимальные данные")
                    activities_text = "No se pudieron obtener actividades. Verifique la conexión a las API."
                    # Создаем минимальные структурированные данные
                    from app.models.activities_models import BudgetEstimate
                    structured_data = ActivitiesResponse(
                        activities=[],
                        total_activities=0,
                        recommended_duration="1 día",
                        budget_estimate=BudgetEstimate(
                            range="€0-50", 
                            per_person="€10-25", 
                            notes="API no disponible"
                        ),
                        age_groups=self._get_age_groups(context.get('kids_ages', [])),
                        interests_covered=[],
                        weather_considerations=["Verificar clima antes de salir"],
                        practical_tips=["Verificar conexión a las API"]
                    )
                
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
                # Ошибка - создаем минимальные данные
                activities_text = f"Error al procesar la solicitud: {str(agent_error)}. Verifique la conexión a las API."
                from app.models.activities_models import BudgetEstimate
                structured_data = ActivitiesResponse(
                    activities=[],
                    total_activities=0,
                    recommended_duration="1 día",
                    budget_estimate=BudgetEstimate(
                        range="€0-50", 
                        per_person="€10-25", 
                        notes="Error en procesamiento"
                    ),
                    age_groups=self._get_age_groups(context.get('kids_ages', [])),
                    interests_covered=[],
                    weather_considerations=["Verificar clima antes de salir"],
                    practical_tips=["Verificar conexión a las API"]
                )
                
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
            from app.models.activities_models import BudgetEstimate
            structured_data = ActivitiesResponse(
                activities=[],
                total_activities=0,
                recommended_duration="1 día",
                budget_estimate=BudgetEstimate(
                    range="€0-50", 
                    per_person="€10-25", 
                    notes="Error crítico"
                ),
                age_groups=self._get_age_groups(context.get('kids_ages', [])),
                interests_covered=[],
                weather_considerations=["Verificar clima antes de salir"],
                practical_tips=["Verificar conexión a las API"]
            )
            return {
                "agent_name": "activities",
                "status": "error",
                "query": query,
                "family_context": context,
                "activities_text": f"Lo siento, hubo un error al crear tu plan de actividades: {str(e)}",
                "structured_data": structured_data,
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
            
            # Если не удалось извлечь активности, возвращаем пустой список
            if not activities:
                activities = []
            
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
    
    # Удален метод _generate_default_activities - используем только API данные
    
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
    
    # Удален метод _create_fallback_structured_data - используем только API данные
    
    def _create_tools(self) -> List[Tool]:
        """Создает инструменты для агента с приоритетами"""
        return [
            Tool(
                name="analyze_age_compatibility",
                description="""[ПРИОРИТЕТ 2] Анализ совместимости активностей с возрастными группами.
                Используй для дополнительного анализа после получения данных от API.
                Входные параметры: kids_ages (JSON массив возрастов)
                Формат: analyze_age_compatibility('[8, 12]')
                Возвращает: анализ по возрастным группам и рекомендации""",
                func=self._analyze_age_compatibility
            ),
            Tool(
                name="optimize_schedule",
                description="""[ПРИОРИТЕТ 2] Оптимизация расписания с учетом энергетических пиков.
                Используй для финальной оптимизации расписания.
                Входные параметры: schedule_data (JSON с данными расписания)
                Формат: optimize_schedule('{"activities": [...]}')
                Возвращает: оптимизированное расписание по времени дня""",
                func=self._optimize_schedule
            )
        ]
    
    def _create_prompt(self) -> PromptTemplate:
        """Создает промпт для реакт-агента по схеме ReAct"""
        return PromptTemplate(
            template="""Eres un experto agente de actividades familiares en Madrid que sigue el patrón ReAct (Reasoning + Acting).

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

PRIORIDAD DE HERRAMIENTAS:
1. **PRIMERA PRIORIDAD**: API externas (search_places_api, get_place_details_api, check_weather_api, search_events_api)
2. **SEGUNDA PRIORIDAD**: Herramientas internas (search_activities, analyze_age_compatibility, optimize_schedule)
3. **ÚLTIMA OPCIÓN**: create_activities_plan (solo si no hay otras opciones)

PATRÓN DE RAZONAMIENTO ReAct:
**Thought**: [Analiza la consulta y determina qué información necesitas]
**Action**: [Nombre de la herramienta a usar]
**Action Input**: [Parámetros específicos para la herramienta]
**Observation**: [Resultado de la herramienta]
**Thought**: [Evalúa el resultado y decide el siguiente paso]
**Action**: [Siguiente herramienta si es necesario]
**Action Input**: [Parámetros]
**Observation**: [Resultado]
**Final Answer**: [Respuesta final estructurada]

REGLAS ESTRICTAS:
1. **SIEMPRE** usa API externas PRIMERO si están disponibles
2. **COMBINA** información de múltiples fuentes
3. **VERIFICA** clima para actividades al aire libre
4. **CONSIDERA** edad específica de los niños
5. **INCLUYE** horarios y ubicaciones precisas
6. **BALANCEA** actividades educativas y recreativas

EJEMPLO DE FLUJO:
**Thought**: Necesito encontrar actividades para niños de 8 y 12 años en Madrid
**Action**: search_places_api
**Action Input**: {{"query": "actividades familiares Madrid", "place_type": "tourist_attraction"}}
**Observation**: [Lugares encontrados]
**Thought**: Ahora voy a verificar el clima para recomendar actividades apropiadas
**Action**: check_weather_api
**Action Input**: {{"date": "2024-01-15"}}
**Observation**: [Datos del clima]
**Thought**: Voy a analizar la compatibilidad con las edades de los niños
**Action**: analyze_age_compatibility
**Action Input**: {{"kids_ages": [8, 12]}}
**Observation**: [Análisis de edades]
**Final Answer**: [Plan personalizado basado en datos reales]

Pregunta del usuario: {input}

{agent_scratchpad}""",
            input_variables=["input", "kids_ages", "adults_count", "interests", "origin_country", "special_needs", "budget_level", "travel_dates", "tools", "tool_names", "agent_scratchpad"]
        )
    
    # Удален метод _search_activities - используем только API поиск
    
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
    
    # Удален метод _matches_criteria - используем только API фильтрацию
    
    # Удален метод _generate_simple_activities_plan - используем только API данные
    
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
                params["types"] = place_type
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/textsearch/json",
                params=params,
                timeout=10
            )
            
            print(f"🔍 Google Places API URL: {response.url}")
            print(f"📊 Google Places API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("results", [])
                print(f"📊 Google Places API Response: {data}")
                print(f"📊 Found places: {len(places)}")
                
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
        """Проверка погоды через OpenWeatherMap API"""
        try:
            if not self.api_services["weather"]:
                return json.dumps({"status": "error", "error": "Weather API не настроен"})
            
            # Реальный вызов OpenWeatherMap API
            api_key = self.api_services["weather"]["api_key"]
            base_url = self.api_services["weather"]["base_url"]
            
            # Madrid coordinates
            lat = "40.4168"
            lon = "-3.7038"
            
            params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",
                "lang": "es"
            }
            
            response = requests.get(f"{base_url}/weather", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                "date": date,
                    "temperature": f"{data['main']['temp']:.1f}°C",
                    "condition": data['weather'][0]['description'].title(),
                    "humidity": f"{data['main']['humidity']}%",
                    "wind": f"{data['wind']['speed']} m/s",
                    "recommendation": self._get_weather_recommendation(data['main']['temp'], data['weather'][0]['main'])
            }
            
            return json.dumps({
                "status": "success",
                    "weather": weather_data
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Weather API error: {response.status_code}"
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_weather_recommendation(self, temp: float, condition: str) -> str:
        """Генерирует рекомендацию на основе погоды"""
        if temp < 10:
            return "Llevar ropa de abrigo, ideal para actividades en interiores"
        elif temp > 25:
            return "Día caluroso, ideal para actividades al aire libre con protección solar"
        elif condition in ["Rain", "Drizzle"]:
            return "Lluvia prevista, recomendadas actividades en interiores"
        else:
            return "Ideal para actividades al aire libre"
    
    def _search_events_api(self, query: str, date: str = None) -> str:
        """Поиск событий через Eventbrite API"""
        try:
            if not self.api_services["events"]:
                return json.dumps({"status": "error", "error": "Events API не настроен"})
            
            # Реальный вызов Eventbrite API
            api_key = self.api_services["events"]["api_key"]
            base_url = self.api_services["events"]["base_url"]
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Поиск событий в Мадриде
            params = {
                "q": query,
                "location.address": "Madrid, Spain",
                "location.within": "10km",
                "sort_by": "date",
                "status": "live"
            }
            
            if date:
                params["start_date.range_start"] = date
                params["start_date.range_end"] = date
            
            response = requests.get(f"{base_url}/events/search", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = []
                
                for event in data.get("events", [])[:5]:  # Ограничиваем до 5 событий
                    event_data = {
                        "name": event.get("name", {}).get("text", ""),
                        "date": event.get("start", {}).get("local", "").split("T")[0] if event.get("start", {}).get("local") else date or "",
                        "time": event.get("start", {}).get("local", "").split("T")[1][:5] if event.get("start", {}).get("local") else "",
                        "location": event.get("venue", {}).get("name", "Madrid"),
                        "price": self._get_event_price(event),
                        "age_range": self._get_event_age_range(event, query)
                    }
                    events.append(event_data)
            
            return json.dumps({
                "status": "success",
                    "events": events,
                "query": query,
                "date": date
            })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Events API error: {response.status_code}"
                })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_event_price(self, event: dict) -> str:
        """Извлекает цену события"""
        try:
            ticket_classes = event.get("ticket_availability", {}).get("ticket_classes", [])
            if ticket_classes:
                price = ticket_classes[0].get("cost", {}).get("display", "Gratis")
                return price
            return "Gratis"
        except:
            return "Gratis"
    
    def _get_event_age_range(self, event: dict, query: str) -> str:
        """Определяет возрастной диапазон события"""
        name = event.get("name", {}).get("text", "").lower()
        if "niños" in name or "niños" in query.lower():
            return "5-12 años"
        elif "familiar" in name or "familiar" in query.lower():
            return "Todas las edades"
        else:
            return "Todas las edades"

def create_activities_agent() -> ActivitiesAgent:
    """Создает экземпляр ActivitiesAgent для RouterAgent"""
    return ActivitiesAgent()