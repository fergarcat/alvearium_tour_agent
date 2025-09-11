# app/services/personalization_agent.py
"""
Специализированный PersonalizationReactAgent для работы с Supabase
"""

import os
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# Импорты из модульной структуры
from app.models.family_models_supabase import FamilyProfileSupabase, PersonalizedQuery
from app.core.data_collector import FamilyDataCollector
from app.services.router_agent import RouterAgent
from app.tools.personalization_tools import (
    get_family_profile_tool,
    update_family_profile_tool,
    analyze_family_needs_tool,
    suggest_personalization_tool,
    calculate_stay_duration_tool,
    validate_family_profile_tool,
    get_family_insights_tool,
    # Новые инструменты для умного анализа
    analyze_trip_requirements_tool,
    check_missing_information_tool_wrapper,
    determine_information_importance_tool,
    collect_missing_information_tool,
    route_to_specialized_agent_tool,
    # Новый инструмент для последовательных вопросов
    sequential_question_tool,
    # Новый инструмент для LLM интерпретации
    llm_interpretation_tool
)

# -----------------------------
# Specialized Personalization React Agent
# -----------------------------
class PersonalizationReactAgent:
    """
    Специализированный PersonalizationReactAgent для работы с Supabase
    
    Ответственность:
    - Персонализация запросов через React Agent
    - Управление профилями семей в Supabase
    - Использование специализированных инструментов
    - Интеллектуальный анализ потребностей семьи
    """
    
    def __init__(self, use_openai=True):
        print("🚀 Инициализация PersonalizationReactAgent (Enhanced Agent)...")
        
        # Используем только OpenAI
        if use_openai and os.getenv("OPENAI_API_KEY"):
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-4o-mini",
                    temperature=0.1,
                    max_tokens=2048
                )
                print("✅ Используется OpenAI (GPT-4o-mini)")
            except Exception as e:
                print(f"❌ Ошибка OpenAI: {e}")
                raise Exception(f"OpenAI не настроен: {e}")
        else:
            print("⚠️ OPENAI_API_KEY не найден, используем тестовый режим")
            # Создаем заглушку для тестирования
            self.llm = None
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Управление состоянием для последовательного сбора информации
        self.collected_profile_data = {}
        self.current_question_step = "kids_ages"  # kids_ages, adults_count, budget_level, etc.
        
        # НОВОЕ: Инициализация компонентов для управления данными
        self.data_collector = FamilyDataCollector()
        self.router_agent = RouterAgent()
        
        print("✅  1  (Enhanced Agent) инициализирован")
        
        # Создаем инструменты для React Agent
        self.tools = [
            Tool(
                name="get_family_profile",
                description="Obtiene el perfil completo de la familia desde la base de datos usando el family_id",
                func=get_family_profile_tool
            ),
            Tool(
                name="update_family_profile",
                description="Actualiza el perfil de la familia con nueva información en formato JSON",
                func=update_family_profile_tool
            ),
            Tool(
                name="analyze_family_needs",
                description="Analiza las necesidades específicas de la familia basándose en su perfil",
                func=analyze_family_needs_tool
            ),
            Tool(
                name="suggest_personalization",
                description="Sugiere cómo personalizar la respuesta basándose en el perfil familiar y la consulta",
                func=suggest_personalization_tool
            ),
            Tool(
                name="calculate_stay_duration",
                description="Calcula la duración del viaje basándose en las fechas de inicio y fin",
                func=calculate_stay_duration_tool
            ),
            Tool(
                name="validate_family_profile",
                description="Valida que el perfil familiar tenga todos los campos requeridos",
                func=validate_family_profile_tool
            ),
            Tool(
                name="get_family_insights",
                description="Genera insights específicos sobre la familia basándose en su perfil",
                func=get_family_insights_tool
            ),
            # Новые инструменты для умного анализа
            Tool(
                name="analyze_trip_requirements",
                description="Analiza los requisitos del viaje basándose en el perfil familiar y la consulta del usuario",
                func=analyze_trip_requirements_tool
            ),
            Tool(
                name="check_missing_information",
                description="Verifica qué información falta en el perfil familiar para un tipo específico de viaje",
                func=check_missing_information_tool_wrapper
            ),
            Tool(
                name="determine_information_importance",
                description="Determina la importancia de un campo faltante para el contexto del viaje",
                func=determine_information_importance_tool
            ),
            Tool(
                name="collect_missing_information",
                description="Recopila información faltante del usuario de manera interactiva",
                func=collect_missing_information_tool
            ),
            Tool(
                name="route_to_specialized_agent",
                description="Determina a qué agente especializado dirigir la consulta basándose en el análisis del viaje",
                func=route_to_specialized_agent_tool
            ),
            Tool(
                name="create_family_profile",
                description="Crea un nuevo perfil familiar en la base de datos. Acepta diferentes formatos: JSON, key=value, o texto natural. Ejemplo: 'family_id=test, kids_ages=[3,1], adults_count=4, budget_level=medium'",
                func=self._create_family_profile_tool
            ),
            Tool(
                name="sequential_question",
                description="Procesa respuestas del usuario de manera secuencial para recopilar información familiar. Reemplaza el complejo prompt con lógica simple de parsing.",
                func=sequential_question_tool
            ),
            Tool(
                name="llm_interpretation",
                description="Usa LLM para interpretar respuestas del usuario en contexto de la pregunta actual. Más inteligente que regex parsing.",
                func=llm_interpretation_tool
            )
        ]
        
        # Создаем React Agent
        self.agent = self._create_react_agent()
        
    def _create_react_agent(self):
        """Создает React Agent с инструментами"""
        try:
            from langchain.agents import create_react_agent
            from .prompt_templates import PERSONALIZATION_AGENT_PROMPT
            
            # Создаем агента с внешним промптом
            # Получаем имена инструментов
            tool_names = [tool.name for tool in self.tools]
            
            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=PERSONALIZATION_AGENT_PROMPT
            )
        
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
        except Exception as e:
            print(f"⚠️ Ошибка создания React Agent: {e}")
            print("   Используем упрощенную версию...")
            return self._create_simple_agent()
    
    def _create_simple_agent(self):
        """Создает упрощенный агент без LangChain"""
        class SimpleAgent:
            def __init__(self, llm, tools, memory):
                self.llm = llm
                self.tools = tools
                self.memory = memory
            
            def invoke(self, input_data):
                query = input_data.get("input", "")
                
                # Простая логика ответов
                if "hotel" in query.lower() or "hoteles" in query.lower():
                    response = "🏨 Te recomiendo hoteles familiares en el centro de Madrid..."
                elif "comer" in query.lower() or "restaurante" in query.lower():
                    response = "🍽️ Te sugiero restaurantes con menú infantil..."
                elif "actividad" in query.lower() or "actividades" in query.lower():
                    response = "🎯 Te recomiendo actividades para toda la familia..."
                else:
                    response = "🐭 ¡Hola! Soy el Ratoncito Pérez. ¿En qué puedo ayudarte con tu viaje a Madrid?"
                
                return {"output": response}
        
        return SimpleAgent(self.llm, self.tools, self.memory)
    
    def _create_family_profile_tool(self, input_data: str) -> str:
        """
        Умный инструмент для создания профиля семьи
        Принимает разные форматы:
        - JSON: {"family_id": "test", "kids_ages": [3, 1], ...}
        - Простой: family_id=test, kids_ages=[3,1], adults_count=4
        - Смешанный: любой формат
        """
        try:
            # 1. Парсим входные данные
            data = self._parse_family_data(input_data)
            
            # 2. Валидируем обязательные поля
            if not data.get("family_id"):
                return "❌ Error: family_id es obligatorio. Por favor, proporciona un ID de familia."
            
            # 3. Проверяем, не существует ли уже профиль
            existing_profile = self.get_family_profile(data["family_id"])
            if existing_profile:
                return f"✅ El perfil para {data['family_id']} ya existe. Puedo ayudarte con la planificación de tu viaje."
            
            # 4. Создаем профиль с валидными датами
            # Обрабатываем неверные значения дат
            start_date = data.get("start_date", "")
            end_date = data.get("end_date", "")
            
            # Если даты неверные или "unknown", используем дефолтные
            if not start_date or start_date == "unknown" or not self._is_valid_date(start_date):
                start_date = "2024-06-15"
            if not end_date or end_date == "unknown" or not self._is_valid_date(end_date):
                end_date = "2024-06-20"
            
            # Обрабатываем budget_level
            budget_level = data.get("budget_level", "medium")
            if budget_level == "unknown":
                budget_level = "medium"
            
            profile = FamilyProfileSupabase(
                family_id=data["family_id"],
                kids_ages=data.get("kids_ages", []),
                adults_count=data.get("adults_count", 0),
                interests=data.get("interests", []) if isinstance(data.get("interests"), list) else [],
                origin_country=data.get("origin_country", ""),
                special_needs=data.get("special_needs", []) if isinstance(data.get("special_needs"), list) else [],
                language_preference=data.get("language_preference", "es"),
                accommodation_type=data.get("accommodation_type", ""),
                transportation_preference=data.get("transportation_preference", "")
            )
            
            # 5. Сохраняем в БД
            result = profile.save_to_supabase()
            if result:
                return f"✅ ¡Perfecto! He creado el perfil familiar para {data['family_id']}. Ahora puedo ayudarte a planificar tu viaje a Madrid con información personalizada."
            else:
                return f"❌ Error al crear el perfil familiar para {data['family_id']}. Por favor, verifica los datos e intenta de nuevo."
            
        except Exception as e:
            return f"❌ Error al crear perfil familiar: {str(e)}. Por favor, verifica que los datos estén en el formato correcto."
    
    def _is_valid_date(self, date_string: str) -> bool:
        """Проверяет валидность даты в формате YYYY-MM-DD"""
        try:
            from datetime import datetime
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _parse_family_data(self, input_data: str) -> dict:
        """
        Парсит входные данные в разных форматах
        """
        try:
            import json
            import re
            
            # Попытка 1: Парсинг как JSON
            try:
                data = json.loads(input_data)
                return self._normalize_family_data(data)
            except:
                pass
            
            # Попытка 2: Парсинг как key=value пары
            try:
                data = {}
                # Ищем пары key=value
                pairs = re.findall(r'(\w+)\s*=\s*([^,]+)', input_data)
                for key, value in pairs:
                    # Очищаем значение от кавычек и скобок
                    clean_value = value.strip().strip('"\'[]')
                    
                    # Парсим массивы
                    if clean_value.startswith('[') and clean_value.endswith(']'):
                        try:
                            data[key] = json.loads(clean_value)
                        except:
                            data[key] = [x.strip() for x in clean_value[1:-1].split(',')]
                    # Парсим числа
                    elif clean_value.isdigit():
                        data[key] = int(clean_value)
                    # Парсим булевы значения
                    elif clean_value.lower() in ['true', 'false']:
                        data[key] = clean_value.lower() == 'true'
                    # Пустые строки для массивов
                    elif clean_value == '' and key in ['interests', 'special_needs', 'kids_ages']:
                        data[key] = []
                    # Обрабатываем "unknown" значения
                    elif clean_value == 'unknown':
                        if key in ['interests', 'special_needs', 'kids_ages']:
                            data[key] = []
                        elif key in ['start_date', 'end_date']:
                            data[key] = ""  # Будет заменено на дефолтную дату
                        else:
                            data[key] = ""
                    # Строки
                    else:
                        data[key] = clean_value
                
                return self._normalize_family_data(data)
            except:
                pass
            
            # Попытка 3: Простой парсинг по ключевым словам
            data = {}
            data["family_id"] = "default"
            
            # Ищем возраст детей
            kids_match = re.search(r'niños?\s*de\s*(\d+)\s*y\s*(\d+)', input_data.lower())
            if kids_match:
                data["kids_ages"] = [int(kids_match.group(1)), int(kids_match.group(2))]
            
            # Ищем количество взрослых
            adults_match = re.search(r'(\d+)\s*adultos?', input_data.lower())
            if adults_match:
                data["adults_count"] = int(adults_match.group(1))
            
            # Ищем бюджет
            if 'bajo' in input_data.lower():
                data["budget_level"] = "low"
            elif 'alto' in input_data.lower():
                data["budget_level"] = "high"
            else:
                data["budget_level"] = "medium"
            
            return self._normalize_family_data(data)
            
        except Exception as e:
            print(f"⚠️ Ошибка парсинга данных: {e}")
            return {"family_id": "default"}
    
    def _normalize_family_data(self, data: dict) -> dict:
        """
        Нормализует данные семьи к стандартному формату
        """
        normalized = {
            "family_id": data.get("family_id", "default"),
            "kids_ages": data.get("kids_ages", data.get("children", [])),
            "adults_count": data.get("adults_count", data.get("adults", 0)),
            "budget_level": data.get("budget_level", data.get("budget", "medium")),
            "start_date": data.get("start_date", data.get("travel_dates", "")),
            "end_date": data.get("end_date", ""),
            "interests": data.get("interests", []),
            "origin_country": data.get("origin_country", data.get("origin", "")),
            "special_needs": data.get("special_needs", []),
            "language_preference": data.get("language_preference", "es"),
            "accommodation_type": data.get("accommodation_type", ""),
            "transportation_preference": data.get("transportation_preference", "")
        }
        
        # Нормализуем budget_level
        if normalized["budget_level"] in ["bajo", "low", "1"]:
            normalized["budget_level"] = "low"
        elif normalized["budget_level"] in ["alto", "high", "3"]:
            normalized["budget_level"] = "high"
        else:
            normalized["budget_level"] = "medium"
        
        return normalized
    
    def process_query(self, query: str, user_id: str = "default") -> str:
        """
        Главный метод агента с полным управлением данными
        
        Workflow:
        1. Проверяем наличие профиля семьи
        2. Если нет профиля - приветствуем и задаем вопросы
        3. Если есть профиль - анализируем запрос
        4. Обрабатываем через React Agent
        5. Сохраняем запрос в Supabase
        6. Возвращаем персонализированный ответ
        """
        
        try:
            print(f"🤖 PersonalizationReactAgent: Обработка запроса для семьи {user_id}")
            print(f"   Query: {query[:50]}...")
            
            # 1. Проверяем наличие профиля семьи
            profile = self.get_family_profile(user_id)
            
            # 2. Если нет профиля, используем последовательный подход
            if not profile:
                print("   ⚠️ Профиль не найден, используем последовательный сбор информации...")
                
                # Простые приветствия обрабатываем сразу
                if any(word in query.lower() for word in ["hola", "hi", "hello", "привет", "здравствуй"]):
                    return """🐭 **¡Hola! Soy el Ratoncito Pérez, tu asistente mágico para viajes familiares en Madrid. ✨**

Para ayudarte a planificar el viaje perfecto, necesito conocer algunos detalles sobre tu familia.

Empecemos con la primera pregunta:

👶 **¿Cuántos niños tienes y qué edades tienen?**

(Por ejemplo: "Tengo 2 niños de 5 y 8 años" o "No tenemos niños")"""
                
                # Для других запросов используем последовательную обработку
                return self._process_sequential_response(query, user_id)
    
            # 3. Если есть профиль, передаем в RouterAgent для анализа и обработки
            print("   🔄 Передача в RouterAgent для анализа и обработки...")
            routing_data = self.prepare_data_for_routing(query, user_id)
            
            # 4. Сохраняем запрос в Supabase
            self._save_travel_request(query, "RouterAgent processing", profile)
            
            # 5. Передаем управление RouterAgent - он сам проанализирует запрос и вернет ответ
            return self.router_agent.process_routing_data(routing_data)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка в PersonalizationReactAgent: {e}")
            
            # Обработка Rate Limit ошибки
            if "Rate limit reached" in error_msg or "429" in error_msg:
                return "⚠️ Lo siento, he alcanzado el límite de consultas por hoy. Por favor, intenta de nuevo mañana."
            
            # Обработка других ошибок API
            if "API" in error_msg or "key" in error_msg.lower():
                return "⚠️ Error de configuración de API. Por favor, verifica las credenciales."
            
            # Обработка ошибок подключения
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return "⚠️ Error de conexión. Por favor, verifica tu conexión a internet."
            
            # Fallback ответ
            return f"Lo siento, hubo un error al procesar tu consulta: {str(e)}"
    
    def get_family_profile(self, family_id: str) -> Optional[FamilyProfileSupabase]:
        """Получает профиль семьи из Supabase"""
        try:
            profile = FamilyProfileSupabase(
                family_id=family_id,
                kids_ages=[],
                adults_count=0,
                interests=[],
                origin_country=""
            )
            
            if profile.load_from_supabase(family_id):
                return profile
            return None
            
        except Exception as e:
            print(f"❌ Ошибка получения профиля семьи: {e}")
            return None
    
    def update_family_profile(self, family_id: str, profile_data: Dict):
        """Обновляет профиль семьи в Supabase"""
        try:
            profile = self.get_family_profile(family_id)
            if not profile:
                print(f"❌ Профиль семьи {family_id} не найден")
                return
        
            # Обновляем поля (только те, которые существуют в модели)
            if "kids_ages" in profile_data:
                profile.kids_ages = profile_data["kids_ages"]
            if "adults_count" in profile_data:
                profile.adults_count = profile_data["adults_count"]
            if "interests" in profile_data:
                profile.interests = profile_data["interests"]
            if "origin_country" in profile_data:
                profile.origin_country = profile_data["origin_country"]
            if "special_needs" in profile_data:
                profile.special_needs = profile_data["special_needs"]
            if "language_preference" in profile_data:
                profile.language_preference = profile_data["language_preference"]
            
            # Для budget_level, start_date, end_date создаем travel_request
            if any(key in profile_data for key in ["budget_level", "start_date", "end_date"]):
                budget_level = profile_data.get("budget_level", "medium")
                start_date = profile_data.get("start_date", "2024-12-01")
                end_date = profile_data.get("end_date", "2024-12-05")
                
                profile.save_travel_request(
                    request_type="accommodation",
                    request_data={"preferences": {}},
                    trip_preferences="",
                    budget_level=budget_level,
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Сохраняем в Supabase
            profile.update_in_supabase()
            
        except Exception as e:
            print(f"❌ Ошибка обновления профиля семьи: {e}")
    
    # ========================================
    # НОВЫЕ МЕТОДЫ: Управление данными
    # ========================================
    
    def initialize_family_profile(self, family_id: str = "default", interactive: bool = True) -> FamilyProfileSupabase:
        """Инициализирует профиль семьи через интерактивный сбор данных"""
        print("🎯 Inicializando perfil familiar...")
        
        if interactive:
            # Собираем данные через интерактивный сборщик
            temp_profile, trip_preferences = self.data_collector.collect_family_data(family_id)
        else:
            # Создаем тестовый профиль для автоматического тестирования
            print("📝 Создаем тестовый профиль семьи...")
            temp_profile = self.data_collector._create_test_profile(family_id)
            trip_preferences = "Test trip preferences"
        
        # Создаем профиль с интеграцией Supabase
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=temp_profile.kids_ages,
            adults_count=temp_profile.adults_count,
            interests=temp_profile.interests,
            origin_country=temp_profile.origin_country,
            special_needs=temp_profile.special_needs,
            language_preference=temp_profile.language_preference,
            accommodation_type=temp_profile.accommodation_type,
            transportation_preference=temp_profile.transportation_preference
        )
        
        # Сохраняем в Supabase
        profile.save_to_supabase()
        
        return profile
    
    def _create_basic_profile(self, family_id: str) -> FamilyProfileSupabase:
        """Создает базовый профиль семьи без интерактивного ввода"""
        print("📝 Создаем базовый профиль семьи...")
        
        # Создаем базовый профиль с дефолтными значениями
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[8, 12],  # Дефолтные возрасты
            adults_count=2,     # Дефолтное количество взрослых
            interests=["museums", "parks"],  # Дефолтные интересы
            origin_country="Spain",  # Дефолтная страна
            special_needs=[]  # Дефолтные потребности
        )
        
        # Сохраняем в Supabase
        try:
            profile.save_to_supabase()
            print("✅ Базовый профиль сохранен в Supabase")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения в Supabase: {e}")
        
        return profile
        
    def _ensure_family_profile(self, family_id: str) -> FamilyProfileSupabase:
        """Обеспечивает наличие профиля семьи"""
        profile = self.get_family_profile(family_id)
        if not profile:
            print("⚠️ No se encontró perfil familiar. El agente preguntará por la información necesaria...")
            # Не создаем профиль автоматически, позволяем агенту задать вопросы
            return None
        return profile
    
    def _analyze_query(self, query: str, family_id: str, profile) -> Dict:
        """Анализирует запрос для определения стратегии обработки"""
        query_lower = query.lower()
        
        analysis = {
            "query_type": "general",
            "needs_hotels": any(word in query_lower for word in ["hotel", "alojamiento", "dormir", "reservar"]),
            "needs_restaurants": any(word in query_lower for word in ["comer", "restaurante", "cena", "almuerzo", "desayuno"]),
            "needs_activities": any(word in query_lower for word in ["actividad", "hacer", "visitar", "turismo", "museo"]),
            "needs_transport": any(word in query_lower for word in ["llegar", "transporte", "metro", "autobús", "taxi"]),
            "is_planning": any(word in query_lower for word in ["planificar", "viaje", "madrid", "recomendar"]),
            "needs_multi_agent": False,
            "family_id": family_id,
            "profile_complete": bool(profile and (
                (isinstance(profile, dict) and profile.get('kids_ages') and profile.get('adults_count', 0) > 0) or
                (hasattr(profile, 'kids_ages') and profile.kids_ages and profile.adults_count > 0)
            ))
        }
        
        # Определяем общий тип запроса
        if analysis["is_planning"]:
            analysis["query_type"] = "planning"
        elif analysis["needs_hotels"]:
            analysis["query_type"] = "hotels"
        elif analysis["needs_restaurants"]:
            analysis["query_type"] = "restaurants"
        elif analysis["needs_activities"]:
            analysis["query_type"] = "activities"
        elif analysis["needs_transport"]:
            analysis["query_type"] = "transport"
        
        # Определяем, нужен ли мультиагентный подход
        needs_count = sum([
            analysis["needs_hotels"],
            analysis["needs_restaurants"], 
            analysis["needs_activities"],
            analysis["needs_transport"]
        ])
        
        analysis["needs_multi_agent"] = (
            needs_count > 1 or  # Множественные потребности
            analysis["is_planning"] or  # Планирование поездки
            not analysis["profile_complete"]  # Неполный профиль
        )
        
        return analysis
    
    def _save_travel_request(self, query: str, response: str, profile) -> None:
        """Сохраняет запрос в Supabase"""
        try:
            # Получаем пожелания из профиля или из запроса
            trip_preferences = getattr(profile, 'trip_preferences', '') or query
            
            # Убеждаемся, что target_agent соответствует допустимым значениям
            request_type_mapping = {
                "hotels": "accommodation",
                "restaurants": "restaurants",
                "activities": "activities",
                "transportation": "transport",
                "all": "accommodation"
            }
            
            # Простое определение типа запроса
            query_lower = query.lower()
            if any(word in query_lower for word in ["hotel", "alojamiento"]):
                request_type = "accommodation"
            elif any(word in query_lower for word in ["comer", "restaurante"]):
                request_type = "restaurants"
            elif any(word in query_lower for word in ["actividad", "hacer"]):
                request_type = "activities"
            elif any(word in query_lower for word in ["llegar", "transporte"]):
                request_type = "transport"
            else:
                request_type = "accommodation"
            
            # Получаем данные из собранной информации или используем дефолтные значения
            budget_level = getattr(profile, 'budget_level', 'medium') if hasattr(profile, 'budget_level') else 'medium'
            start_date = getattr(profile, 'start_date', '2024-12-01') if hasattr(profile, 'start_date') else '2024-12-01'
            end_date = getattr(profile, 'end_date', '2024-12-05') if hasattr(profile, 'end_date') else '2024-12-05'
            
            profile.save_travel_request(request_type, {
                "query": query,
                "personalized_response": response,
                "preferences": {
                    "budget_level": budget_level,
                    "interests": profile.interests,
                    "family_size": profile.get_family_size(),
                    "age_group": profile.get_age_group()
                }
            }, trip_preferences, budget_level, start_date, end_date)
            
        except Exception as e:
            print(f"⚠️ Не удалось сохранить запрос: {e}")
    
    def create_ai_profile(self, family_id: str, ai_analysis: Dict) -> Optional[str]:
        """Создает AI профиль семьи"""
        try:
            profile = self.get_family_profile(family_id)
            if not profile:
                print(f"❌ Профиль семьи {family_id} не найден")
                return None
            
            return profile.create_ai_profile(ai_analysis)
        except Exception as e:
            print(f"❌ Ошибка создания AI профиля: {e}")
            return None
    
    def prepare_data_for_routing(self, query: str, family_id: str) -> Dict:
        """
        Подготавливает данные для RouterAgent
        
        Workflow:
        1. Вызывает API endpoint для получения полного профиля с датами
        2. Анализирует запрос
        3. Подготавливает структурированные данные для маршрутизации
        """
        try:
            print(f"🔍 PersonalizationReactAgent: Подготовка данных для маршрутизации")
            
            # 1. Получаем полный профиль через API endpoint
            full_profile = self._get_full_family_profile_via_api(family_id)
            print(f"📊 PersonalizationReactAgent: Получен профиль: {type(full_profile)}")
            print(f"   • Kids ages: {full_profile.get('kids_ages', [])}")
            print(f"   • Start date: {full_profile.get('start_date', 'No especificada')}")
            print(f"   • End date: {full_profile.get('end_date', 'No especificada')}")
            
            # 2. Подготавливаем данные для RouterAgent (без анализа запроса)
            routing_data = {
                "query": query,
                "family_id": family_id,
                "profile": {
                    "kids_ages": full_profile.get('kids_ages', []),
                    "adults_count": full_profile.get('adults_count', 0),
                    "budget_level": full_profile.get('budget_level', 'medium'),
                    "interests": full_profile.get('interests', []),
                    "special_needs": full_profile.get('special_needs', []),
                    "language_preference": full_profile.get('language_preference', 'es'),
                    "start_date": full_profile.get('start_date', '2024-12-01'),
                    "end_date": full_profile.get('end_date', '2024-12-05')
                }
            }
            
            print(f"✅ Данные подготовлены для RouterAgent")
            print(f"📤 PersonalizationReactAgent ПЕРЕДАЕТ RouterAgent:")
            print(f"   • Query: {routing_data['query']}")
            print(f"   • Family ID: {routing_data['family_id']}")
            print(f"   • Profile data:")
            profile_data = routing_data['profile']
            print(f"     - Kids ages: {profile_data.get('kids_ages', [])}")
            print(f"     - Adults count: {profile_data.get('adults_count', 0)}")
            print(f"     - Interests: {profile_data.get('interests', [])}")
            print(f"     - Special needs: {profile_data.get('special_needs', [])}")
            print(f"     - Language: {profile_data.get('language_preference', 'es')}")
            print(f"     - Budget level: {profile_data.get('budget_level', 'No especificado')}")
            print(f"     - Start date: {profile_data.get('start_date', 'No especificada')}")
            print(f"     - End date: {profile_data.get('end_date', 'No especificada')}")
            print(f"   • Query analysis: {routing_data.get('query_analysis', {})}")
            print(f"   • Needs multi-agent: {routing_data.get('needs_multi_agent', False)}")
            print(f"   • Agents needed: {[k for k, v in routing_data.items() if k.startswith('needs_') and v]}")
            print(f"   • Query type: {routing_data.get('query_type', 'general')}")
            return routing_data
            
        except Exception as e:
            print(f"❌ Ошибка подготовки данных для маршрутизации: {e}")
            return {
                "query": query,
                "family_id": family_id,
                "profile": {},
                "query_analysis": {"query_type": "general"},
                "needs_hotels": False,
                "needs_restaurants": False,
                "needs_activities": False,
                "needs_transport": False,
                "is_planning": False,
                "query_type": "general"
            }
    
    def _get_full_family_profile_via_api(self, family_id: str) -> Dict:
        """Получает полный профиль семьи через API endpoint"""
        try:
            import requests
            import os
            
            # Получаем базовый URL API
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            api_url = f"{base_url}/api/v1/agents/families/{family_id}/profile"
            
            print(f"🌐 PersonalizationReactAgent: Загружаем полный профиль через API: {api_url}")
            
            # Вызываем API endpoint
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                profile_data = response.json()
                print(f"✅ PersonalizationReactAgent: Профиль загружен: {profile_data.get('start_date')} - {profile_data.get('end_date')}")
                return profile_data
            else:
                print(f"⚠️ PersonalizationReactAgent: API вернул статус {response.status_code}")
                return self._get_fallback_profile(family_id)
                
        except Exception as e:
            print(f"❌ PersonalizationReactAgent: Ошибка загрузки через API: {e}")
            return self._get_fallback_profile(family_id)
    
    def _get_fallback_profile(self, family_id: str) -> Dict:
        """Создает fallback профиль если API недоступен"""
        try:
            # Пытаемся загрузить через модель как fallback
            profile = self.get_family_profile(family_id)
            if profile:
                # Загружаем данные поездки через модель
                travel_data = profile.load_travel_dates(family_id)
                print(f"📅 PersonalizationReactAgent: Fallback загружены даты: {travel_data.get('start_date')} - {travel_data.get('end_date')}")
                return {
                    "family_id": profile.family_id,
                    "kids_ages": profile.kids_ages,
                    "adults_count": profile.adults_count,
                    "budget_level": travel_data.get('budget_level', 'medium'),
                    "start_date": travel_data.get('start_date', '2024-12-01'),
                    "end_date": travel_data.get('end_date', '2024-12-05'),
                    "interests": profile.interests,
                    "special_needs": profile.special_needs or [],
                    "language_preference": profile.language_preference,
                    "accommodation_type": profile.accommodation_type,
                    "transportation_preference": profile.transportation_preference
                }
            else:
                # Если профиль не найден, возвращаем дефолтные значения
                print(f"⚠️ PersonalizationReactAgent: Профиль не найден, используем дефолтные значения")
                return {
                    "family_id": family_id,
                    "kids_ages": [],
                    "adults_count": 0,
                    "budget_level": "medium",
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-05",
                    "interests": [],
                    "special_needs": [],
                    "language_preference": "es",
                    "accommodation_type": "",
                    "transportation_preference": ""
                }
        except Exception as e:
            print(f"❌ PersonalizationReactAgent: Ошибка fallback профиля: {e}")
            return {
                "family_id": family_id,
                "kids_ages": [],
                "adults_count": 0,
                "budget_level": "medium",
                "start_date": "2024-12-01",
                "end_date": "2024-12-05",
                "interests": [],
                "special_needs": [],
                "language_preference": "es",
                "accommodation_type": "",
                "transportation_preference": ""
            }

    def get_agent_capabilities(self) -> List[str]:
        """Возвращает список возможностей агента"""
        return [
            "Персонализация запросов",
            "Управление профилями семей",
            "Сохранение запросов в Supabase",
            "Анализ потребностей семьи",
            "Создание AI профилей",
            "Интерактивный сбор данных",
            "Подготовка данных для маршрутизации",
            "Загрузка полного профиля через API"
        ]
    
    def _process_with_sequential_agent(self, query: str, user_id: str) -> str:
        """Обрабатывает запрос с последовательным сбором информации"""
        try:
            # Определяем текущий шаг на основе содержимого запроса
            current_step = self._determine_current_step(query)
            collected_info = self._get_collected_info(user_id)
            
            # Создаем контекст для агента
            context = {
                "input": f"Usuario {user_id}: {query}",
                "family_id": user_id,
                "current_step": current_step,
                "collected_info": collected_info
            }
            
            # Используем обычного агента, но с дополнительным контекстом
            response = self.agent.invoke(context)
            return response["output"]
            
        except Exception as e:
            print(f"❌ Ошибка в последовательной обработке: {e}")
            return f"Lo siento, hubo un error al procesar tu consulta: {str(e)}"
    
    def _determine_current_step(self, query: str) -> str:
        """Определяет текущий шаг сбора информации"""
        query_lower = query.lower()
        
        # Проверяем, какая информация уже упоминается в запросе
        if any(word in query_lower for word in ["niño", "niños", "edad", "años", "año"]):
            return "kids_ages"
        elif any(word in query_lower for word in ["adulto", "adultos", "padre", "madre", "padres"]):
            return "adults_count"
        elif any(word in query_lower for word in ["presupuesto", "dinero", "económico", "caro", "barato"]):
            return "budget_level"
        elif any(word in query_lower for word in ["fecha", "cuando", "viajar", "julio", "agosto", "junio"]):
            return "travel_dates"
        elif any(word in query_lower for word in ["gusta", "interesa", "museo", "parque", "comida"]):
            return "interests"
        elif any(word in query_lower for word in ["país", "vienen", "españa", "mexico", "argentina"]):
            return "origin_country"
        elif any(word in query_lower for word in ["especial", "necesidad", "discapacidad", "autismo"]):
            return "special_needs"
        else:
            return "welcome"
    
    def _get_collected_info(self, user_id: str) -> str:
        """Получает уже собранную информацию о семье"""
        # В реальной реализации здесь можно хранить промежуточную информацию
        # Пока возвращаем пустую строку
        return "Información aún no recopilada"
    
    def _process_sequential_response(self, query: str, user_id: str) -> str:
        """Обрабатывает ответ пользователя в последовательном режиме"""
        try:
            import json
            
            # Определяем текущий вопрос на основе состояния
            question_map = {
                "kids_ages": "¿Cuántos niños tienes y qué edades tienen?",
                "adults_count": "¿Cuántos adultos viajarán?",
                "budget_level": "¿Cuál es tu presupuesto aproximado para el viaje?",
                "travel_dates": "¿Cuándo planeas viajar?",
                "interests": "¿Qué te interesa más en Madrid?",
                "origin_country": "¿De qué país vienes?",
                "special_needs": "¿Hay alguna necesidad especial en tu familia?"
            }
            
            current_question = question_map.get(self.current_question_step, "¿Cuántos niños tienes y qué edades tienen?")
            collected_info = json.dumps(self.collected_profile_data, ensure_ascii=False)
            
            # Используем LLM для интерпретации ответа пользователя
            extracted_info = llm_interpretation_tool(query, current_question, collected_info)
            
            print(f"   📝 Извлеченная информация: {extracted_info}")
            
            # Парсим JSON ответ
            try:
                info_data = json.loads(extracted_info)
            except:
                info_data = {}
            
            # Проверяем, есть ли ошибка в интерпретации
            if "error" in info_data:
                return f"❌ {info_data.get('message', 'Error al procesar tu respuesta')}"
            
            # Проверяем, есть ли сообщение о непонимании
            if "message" in info_data and not any(key in info_data for key in ["kids_ages", "adults_count", "budget_level", "travel_dates", "interests", "origin_country", "special_needs"]):
                return f"❌ {info_data['message']}\n\n{current_question}"
            
            # Накапливаем собранную информацию
            if any(key in info_data for key in ["kids_ages", "adults_count", "budget_level", "travel_dates", "interests", "origin_country", "special_needs"]):
                self.collected_profile_data.update(info_data)
                print(f"   📊 Накопленные данные: {self.collected_profile_data}")
            
            # Определяем следующий шаг на основе текущего состояния
            if self.current_question_step == "kids_ages" and "kids_ages" in info_data:
                self.current_question_step = "adults_count"
                ages_str = ", ".join(map(str, info_data["kids_ages"]))
                return f"""¡Perfecto! 👶 He anotado que tienes niños de las siguientes edades: {ages_str}

Ahora necesito saber:

👨‍👩‍👧‍👦 **¿Cuántos adultos viajarán?**

(Por ejemplo: "Somos 2 adultos" o "Viajamos 4 adultos")"""
            
            elif self.current_question_step == "adults_count" and "adults_count" in info_data:
                self.current_question_step = "budget_level"
                return f"""¡Excelente! 👨‍👩‍👧‍👦 He anotado que viajan {info_data['adults_count']} adultos.

Ahora necesito saber:

💰 **¿Cuál es tu presupuesto aproximado para el viaje?**

- Bajo (económico)
- Medio (normal)
- Alto (lujo)

(Por ejemplo: "Presupuesto medio" o "Queremos algo económico")"""
            
            elif self.current_question_step == "budget_level" and "budget_level" in info_data:
                self.current_question_step = "travel_dates"
                return f"""¡Genial! 💰 He anotado tu presupuesto: {info_data['budget_level']}

Ahora necesito saber:

📅 **¿Cuándo planeas viajar?**

(Por ejemplo: "Del 15 al 20 de junio" o "En julio por una semana")"""
            
            elif self.current_question_step == "travel_dates" and "travel_dates" in info_data:
                self.current_question_step = "interests"
                return """¡Perfecto! 📅 He anotado las fechas de tu viaje.

Ahora necesito saber:

🎯 **¿Qué les gusta hacer a tu familia?**

(Por ejemplo: "Museos, parques y comida" o "Nos gusta el arte y la naturaleza")"""
            
            elif self.current_question_step == "interests" and "interests" in info_data:
                self.current_question_step = "origin_country"
                interests_str = ", ".join(info_data["interests"])
                return f"""¡Excelente! 🎯 He anotado tus intereses: {interests_str}

Ahora necesito saber:

🌍 **¿De qué país vienen?**

(Por ejemplo: "España" o "México")"""
            
            elif self.current_question_step == "origin_country" and "origin_country" in info_data:
                self.current_question_step = "special_needs"
                return f"""¡Perfecto! 🌍 He anotado que vienen de {info_data['origin_country']}.

Última pregunta:

✨ **¿Tienes alguna preferencia especial para el viaje?**

(Por ejemplo: "Mi hijo tiene autismo" o "Necesitamos silla de ruedas" o "No, todo normal")"""
            
            elif self.current_question_step == "special_needs" and "special_needs" in info_data:
                # Получили всю информацию (включая пустой массив для special_needs), создаем профиль
                return self._create_profile_from_collected_info(user_id)
            
            else:
                # Не удалось извлечь информацию, просим уточнить
                return f"""No pude entender tu respuesta. Por favor, responde de manera más específica.

{current_question}"""
                
        except Exception as e:
            print(f"❌ Ошибка в последовательной обработке: {e}")
            return f"Lo siento, hubo un error al procesar tu respuesta: {str(e)}"
    
    def _create_profile_from_collected_info(self, user_id: str) -> str:
        """Создает профиль семьи из собранной информации"""
        try:
            # Формируем данные для создания профиля из накопленных данных
            # Парсим даты из travel_dates
            start_date = "2024-06-15"  # Дефолтная дата
            end_date = "2024-06-20"    # Дефолтная дата
            
            if "travel_dates" in self.collected_profile_data:
                travel_dates = self.collected_profile_data["travel_dates"]
                if " to " in travel_dates:
                    start_date, end_date = travel_dates.split(" to ")
                elif " - " in travel_dates:
                    start_date, end_date = travel_dates.split(" - ")
            
            profile_data = {
                "family_id": user_id,
                "kids_ages": self.collected_profile_data.get("kids_ages", []),
                "adults_count": self.collected_profile_data.get("adults_count", 2),
                "interests": self.collected_profile_data.get("interests", []),
                "origin_country": self.collected_profile_data.get("origin_country", ""),
                "special_needs": self.collected_profile_data.get("special_needs", [])
            }
            
            # Создаем профиль семьи (без данных поездки)
            profile = FamilyProfileSupabase(
                family_id=profile_data["family_id"],
                kids_ages=profile_data["kids_ages"],
                adults_count=profile_data["adults_count"],
                interests=profile_data["interests"],
                origin_country=profile_data["origin_country"],
                special_needs=profile_data["special_needs"]
            )
            
            # Сохраняем в базу данных
            result = profile.save_to_supabase()
            
            if result:
                # Создаем travel_request с данными поездки
                budget_level = self.collected_profile_data.get("budget_level", "medium")
                
                # Создаем travel_request
                travel_request_id = profile.save_travel_request(
                    request_type="accommodation",
                    request_data={"preferences": {}},
                    trip_preferences="",
                    budget_level=budget_level,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Сбрасываем состояние после успешного создания профиля
                self.collected_profile_data = {}
                self.current_question_step = "kids_ages"
                
                return f"""🎉 **¡Perfecto! He creado tu perfil familiar completo!**

📋 **Resumen de tu familia:**
• Niños: {len(profile_data['kids_ages'])} de edades {profile_data['kids_ages']}
• Adultos: {profile_data['adults_count']}
• Presupuesto: {budget_level}
• Fechas: {start_date} a {end_date}
• Intereses: {', '.join(profile_data['interests']) if profile_data['interests'] else 'No especificados'}
• País: {profile_data['origin_country'] or 'No especificado'}

¡Ahora puedo ayudarte a planificar el viaje perfecto a Madrid! ✨

¿Qué te gustaría saber sobre tu viaje? Por ejemplo:
• "¿Qué hoteles me recomiendas?"
• "¿Dónde podemos comer?"
• "¿Qué actividades hay para niños?" """
            else:
                return "❌ Hubo un error al crear tu perfil. Por favor, intenta de nuevo."
                
        except Exception as e:
            print(f"❌ Ошибка создания профиля: {e}")
            return f"❌ Error al crear tu perfil: {str(e)}"
    

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Тестируем специализированный агент
    agent = PersonalizationReactAgent()
    
    # Простой тест
    response = agent.process_query("Hola, quiero planificar un viaje a Madrid", "test_family")
    print(f"Respuesta del agente: {response}")
