# app/services/router_agent.py
"""
Router Agent - распределяет запросы к специализированным агентам
"""

import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.models.family_models import PersonalizedQuery

class RouterAgent:
    """
    Router Agent - распределяет задачи между специализированными агентами
    
    Ответственность:
    - Получает данные от PersonalizationReactAgent
    - Анализирует, какие специализированные агенты нужны
    - Распределяет задачи между агентами
    - Координирует выполнение
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0
        )
        
        # Специализированные агенты (пока заглушки)
        self.specialized_agents = {
            "hotels": None,      # Агент отелей
            "restaurants": None, # Агент ресторанов  
            "activities": None,  # Агент активностей
            "transport": None    # Агент транспорта
        }
        
        print("✅ RouterAgent инициализирован")
    
    def process_routing_data(self, routing_data: Dict) -> str:
        """
        Главный метод обработки данных от PersonalizationReactAgent
        
        Workflow:
        1. Анализирует данные от PersonalizationReactAgent
        2. Определяет, какие специализированные агенты нужны
        3. Распределяет задачи между агентами
        4. Возвращает готовый ответ пользователю
        """
        try:
            print(f"🎯 RouterAgent: Обработка данных маршрутизации")
            print(f"   Query: {routing_data.get('query', '')[:50]}...")
            print(f"   Family ID: {routing_data.get('family_id', 'unknown')}")
            
            # 1. Анализируем данные
            needed_agents = self._determine_needed_agents(routing_data)
            print(f"   Нужные агенты: {needed_agents}")
            
            # 2. Если агенты не нужны, возвращаем простой ответ
            if not needed_agents:
                return self._create_simple_response_text(routing_data)
            
            # 3. Распределяем задачи между агентами
            agent_results = self._distribute_tasks(routing_data, needed_agents)
            
            # 4. Форматируем финальный ответ для пользователя
            final_response = self._format_final_response_text(routing_data, agent_results)
            
            print("✅ RouterAgent: Задачи распределены и выполнены")
            return final_response
            
        except Exception as e:
            print(f"❌ RouterAgent: Ошибка обработки: {e}")
            return self._create_error_response_text(routing_data, str(e))
    
    def _determine_needed_agents(self, routing_data: Dict) -> List[str]:
        """Определяет, какие специализированные агенты нужны"""
        needed_agents = []
        
        if routing_data.get("needs_hotels", False):
            needed_agents.append("hotels")
        if routing_data.get("needs_restaurants", False):
            needed_agents.append("restaurants")
        if routing_data.get("needs_activities", False):
            needed_agents.append("activities")
        if routing_data.get("needs_transport", False):
            needed_agents.append("transport")
        
        return needed_agents
    
    def _distribute_tasks(self, routing_data: Dict, needed_agents: List[str]) -> Dict[str, str]:
        """Распределяет задачи между специализированными агентами"""
        results = {}
        
        for agent_name in needed_agents:
            try:
                # Пока используем заглушки, позже заменим на реальные агенты
                result = self._call_specialized_agent(agent_name, routing_data)
                results[agent_name] = result
                print(f"   ✅ {agent_name}: Задача выполнена")
            except Exception as e:
                print(f"   ❌ {agent_name}: Ошибка - {e}")
                results[agent_name] = f"Ошибка агента {agent_name}: {str(e)}"
        
        return results
    
    def _call_specialized_agent(self, agent_name: str, routing_data: Dict) -> str:
        """Вызывает специализированный агент с полной информацией о семье"""
        profile = routing_data.get("profile", {})
        family_id = routing_data.get("family_id", "unknown")
        query = routing_data.get("query", "")
        
        # Формируем контекст с полной информацией о семье
        family_context = self._build_family_context(profile, family_id)
        
        # Заглушки для специализированных агентов с полным контекстом
        stub_responses = {
            "hotels": f"""🏨 **Recomendaciones de Hoteles para {family_id}**

{family_context}

**Consulta específica:** {query}

**Recomendaciones personalizadas:**
- Hoteles familiares con servicios para niños
- Ubicación cerca de atracciones familiares
- Presupuesto: {profile.get('budget_level', 'medium')}
- Fechas: {profile.get('start_date', 'No especificadas')} a {profile.get('end_date', 'No especificadas')}

[Заглушка - агент отелей с контекстом]""",
            
            "restaurants": f"""🍽️ **Recomendaciones de Restaurantes para {family_id}**

{family_context}

**Consulta específica:** {query}

**Recomendaciones personalizadas:**
- Restaurantes familiares con menú infantil
- Intereses culinarios: {', '.join(profile.get('interests', [])) if profile.get('interests') else 'No especificados'}
- Necesidades especiales: {', '.join(profile.get('special_needs', [])) if profile.get('special_needs') else 'Ninguna'}
- Presupuesto: {profile.get('budget_level', 'medium')}

[Заглушка - агент ресторанов con контекстом]""",
            
            "activities": f"""🎯 **Recomendaciones de Actividades para {family_id}**

{family_context}

**Consulta específica:** {query}

**Recomendaciones personalizadas:**
- Actividades apropiadas para las edades: {profile.get('kids_ages', [])}
- Intereses: {', '.join(profile.get('interests', [])) if profile.get('interests') else 'No especificados'}
- Necesidades especiales: {', '.join(profile.get('special_needs', [])) if profile.get('special_needs') else 'Ninguna'}
- Presupuesto: {profile.get('budget_level', 'medium')}

[Заглушка - агент активностей с контекстом]""",
            
            "transport": f"""🚌 **Recomendaciones de Transporte para {family_id}**

{family_context}

**Consulta específica:** {query}

**Recomendaciones personalizadas:**
- Opciones de transporte familiar
- Accesibilidad: {', '.join(profile.get('special_needs', [])) if profile.get('special_needs') else 'No hay necesidades especiales'}
- Presupuesto: {profile.get('budget_level', 'medium')}
- Fechas: {profile.get('start_date', 'No especificadas')} a {profile.get('end_date', 'No especificadas')}

[Заглушка - агент транспорта с контекстом]"""
        }
        
        return stub_responses.get(agent_name, f"Неизвестный агент: {agent_name}")
    
    def _build_family_context(self, profile, family_id: str) -> str:
        """Строит полный контекст семьи для специализированных агентов"""
        # Проверяем, что profile - это словарь
        if not isinstance(profile, dict):
            return f"**Perfil Familiar Completo:**\n• **ID Familia:** {family_id}\n• **Datos:** No disponibles"
        
        kids_ages = profile.get('kids_ages', [])
        adults_count = profile.get('adults_count', 0)
        interests = profile.get('interests', [])
        special_needs = profile.get('special_needs', [])
        budget_level = profile.get('budget_level', 'medium')
        language_preference = profile.get('language_preference', 'es')
        start_date = profile.get('start_date', 'No especificada')
        end_date = profile.get('end_date', 'No especificada')
        
        context = f"""**Perfil Familiar Completo:**
• **ID Familia:** {family_id}
• **Composición:** {adults_count} adultos, {len(kids_ages)} niños
• **Edades de los niños:** {kids_ages if kids_ages else 'No hay niños'}
• **Presupuesto:** {budget_level}
• **Fechas de viaje:** {start_date} a {end_date}
• **Idioma preferido:** {language_preference}"""
        
        if interests:
            context += f"\n• **Intereses:** {', '.join(interests)}"
        
        if special_needs:
            context += f"\n• **Necesidades especiales:** {', '.join(special_needs)}"
        else:
            context += f"\n• **Necesidades especiales:** Ninguna"
            
        return context
    
    def _aggregate_results(self, routing_data: Dict, agent_results: Dict[str, str]) -> Dict:
        """Агрегирует результаты от всех агентов"""
        return {
            "query": routing_data.get("query", ""),
            "family_id": routing_data.get("family_id", ""),
            "query_type": routing_data.get("query_type", "general"),
            "agent_results": agent_results,
            "status": "success",
            "message": "Задачи успешно распределены и выполнены"
        }
    
    def _create_simple_response(self, routing_data: Dict) -> Dict:
        """Создает простой ответ, если специализированные агенты не нужны"""
        return {
            "query": routing_data.get("query", ""),
            "family_id": routing_data.get("family_id", ""),
            "query_type": routing_data.get("query_type", "general"),
            "agent_results": {},
            "status": "simple",
            "message": "Специализированные агенты не требуются"
        }
    
    def _create_simple_response_text(self, routing_data: Dict) -> str:
        """Создает простой текстовый ответ, если специализированные агенты не нужны"""
        profile = routing_data.get("profile", {})
        family_id = routing_data.get("family_id", "unknown")
        query = routing_data.get("query", "")
        
        return f"""
🎯 **Respuesta del RouterAgent:**

Hola! He analizado tu consulta: "{query}"

Para tu familia {family_id}, no necesito activar agentes especializados en este momento. 

¿Hay algo específico en lo que pueda ayudarte? Por ejemplo:
• "¿Qué hoteles me recomiendas?"
• "¿Dónde podemos comer?"
• "¿Qué actividades hay para niños?"
• "¿Cómo llegar a Madrid?"

**Perfil familiar:** {family_id} - {len(profile.get('kids_ages', []))} niños, {profile.get('adults_count', 0)} adultos
"""
    
    def _create_error_response(self, routing_data: Dict, error: str) -> Dict:
        """Создает ответ об ошибке"""
        return {
            "query": routing_data.get("query", ""),
            "family_id": routing_data.get("family_id", ""),
            "query_type": routing_data.get("query_type", "general"),
            "agent_results": {},
            "status": "error",
            "message": f"Ошибка RouterAgent: {error}"
        }
    
    def _create_error_response_text(self, routing_data: Dict, error: str) -> str:
        """Создает текстовый ответ об ошибке"""
        return f"""
❌ **Error del RouterAgent:**

Lo siento, hubo un error al procesar tu consulta: {error}

Por favor, intenta de nuevo o reformula tu pregunta.
"""
        
    def route_personalized_query(self, personalized_context: str, suggested_agent: str = "all") -> str:
        """Определяет, к какому специализированному агенту направить запрос"""
        
        routing_prompt = PromptTemplate(
            template="""
            Eres un agente router que decide qué agente especializado debe manejar una consulta.
            
            CONSULTA PERSONALIZADA: {personalized_context}
            AGENTE SUGERIDO: {suggested_agent}
            
            Determina el agente más apropiado:
            - "hotels" - para alojamiento y hoteles
            - "restaurants" - para restaurantes y comida
            - "activities" - para actividades y atracciones
            - "transportation" - para transporte
            - "all" - para consultas generales que requieren múltiples agentes
            
            Responde solo con el nombre del agente.
            """,
            input_variables=["personalized_context", "suggested_agent"]
        )
        
        chain = routing_prompt | self.llm
        response = chain.invoke({
            "personalized_context": personalized_context,
            "suggested_agent": suggested_agent
        })
        
        return response.strip().lower()
    
    def route_by_keywords(self, query: str) -> str:
        """Маршрутизация на основе ключевых слов в запросе"""
        query_lower = query.lower()
        
        # Ключевые слова для каждого агента
        hotel_keywords = ["hotel", "alojamiento", "hospedaje", "dormir", "habitación"]
        restaurant_keywords = ["restaurante", "comida", "cenar", "almorzar", "desayunar", "comer"]
        activity_keywords = ["actividad", "museo", "parque", "atracción", "visitar", "hacer", "ver"]
        transport_keywords = ["transporte", "metro", "autobús", "taxi", "caminar", "llegar", "ir"]
        
        # Подсчет совпадений
        hotel_score = sum(1 for keyword in hotel_keywords if keyword in query_lower)
        restaurant_score = sum(1 for keyword in restaurant_keywords if keyword in query_lower)
        activity_score = sum(1 for keyword in activity_keywords if keyword in query_lower)
        transport_score = sum(1 for keyword in transport_keywords if keyword in query_lower)
        
        # Определение агента с наибольшим количеством совпадений
        scores = {
            "hotels": hotel_score,
            "restaurants": restaurant_score,
            "activities": activity_score,
            "transportation": transport_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return "all"  # Если нет совпадений, используем общий агент
        
        return max(scores, key=scores.get)
    
    def get_agent_description(self, agent_name: str) -> str:
        """Возвращает описание агента"""
        descriptions = {
            "hotels": "Especialista en recomendaciones de hoteles y alojamiento familiar",
            "restaurants": "Especialista en restaurantes familiares y opciones gastronómicas",
            "activities": "Especialista en actividades turísticas y atracciones para familias",
            "transportation": "Especialista en opciones de transporte y movilidad",
            "all": "Asistente general para planificación completa de viajes"
        }
        return descriptions.get(agent_name, "Agente especializado")
    
    def _format_final_response_text(self, routing_data: Dict, agent_results: Dict[str, str]) -> str:
        """Форматирует финальный ответ для пользователя"""
        try:
            profile = routing_data.get("profile", {})
            family_id = routing_data.get("family_id", "unknown")
            query = routing_data.get("query", "")
            query_type = routing_data.get("query_type", "general")
            
            # Формируем ответ от специализированных агентов
            specialized_responses = []
            for agent_name, result in agent_results.items():
                if agent_name == "hotels":
                    specialized_responses.append(f"🏨 **Recomendaciones de Hoteles:**\n{result}")
                elif agent_name == "restaurants":
                    specialized_responses.append(f"🍽️ **Recomendaciones de Restaurantes:**\n{result}")
                elif agent_name == "activities":
                    specialized_responses.append(f"🎯 **Recomendaciones de Actividades:**\n{result}")
                elif agent_name == "transport":
                    specialized_responses.append(f"🚌 **Recomendaciones de Transporte:**\n{result}")
            
            # Объединяем все ответы
            combined_response = "\n\n".join(specialized_responses) if specialized_responses else "No hay recomendaciones específicas disponibles."
            
            # Создаем расширенный профиль для отображения
            # Проверяем, что profile - это словарь, а не строка
            if isinstance(profile, dict):
                family_summary = self._build_family_summary(profile, family_id)
            else:
                family_summary = f"**👨‍👩‍👧‍👦 Tu perfil familiar:** {family_id}"
            
            return f"""
🎯 **Respuesta del RouterAgent (Multi-Agent):**

{combined_response}

---

**📋 Resumen de tu consulta:**
• **Consulta:** {query}
• **Tipo:** {query_type}
• **Agentes utilizados:** {', '.join(agent_results.keys()) if agent_results else 'Ninguno'}

{family_summary}

¿Hay algo más en lo que pueda ayudarte con tu viaje a Madrid?
"""
            
        except Exception as e:
            print(f"❌ Ошибка форматирования финального ответа: {e}")
            return f"❌ Error al formatear respuesta: {str(e)}"
    
    def _build_family_summary(self, profile, family_id: str) -> str:
        """Создает краткое резюме семьи для финального ответа"""
        # Проверяем, что profile - это словарь
        if not isinstance(profile, dict):
            return f"**👨‍👩‍👧‍👦 Tu perfil familiar:** {family_id}"
        
        kids_ages = profile.get('kids_ages', [])
        adults_count = profile.get('adults_count', 0)
        interests = profile.get('interests', [])
        special_needs = profile.get('special_needs', [])
        budget_level = profile.get('budget_level', 'medium')
        start_date = profile.get('start_date', 'No especificada')
        end_date = profile.get('end_date', 'No especificada')
        
        summary = f"""**👨‍👩‍👧‍👦 Tu perfil familiar:**
• **Familia:** {family_id} ({adults_count} adultos, {len(kids_ages)} niños)
• **Edades de los niños:** {kids_ages if kids_ages else 'No hay niños'}
• **Presupuesto:** {budget_level}
• **Fechas:** {start_date} a {end_date}"""
        
        if interests:
            summary += f"\n• **Intereses:** {', '.join(interests)}"
        
        if special_needs:
            summary += f"\n• **Necesidades especiales:** {', '.join(special_needs)}"
            
        return summary
