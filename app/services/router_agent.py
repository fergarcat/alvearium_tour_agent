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
    
    def process_routing_data(self, routing_data: Dict) -> Dict:
        """
        Главный метод обработки данных от PersonalizationReactAgent
        
        Workflow:
        1. Анализирует данные от PersonalizationReactAgent
        2. Определяет, какие специализированные агенты нужны
        3. Распределяет задачи между агентами
        4. Возвращает результаты
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
                return self._create_simple_response(routing_data)
            
            # 3. Распределяем задачи между агентами
            agent_results = self._distribute_tasks(routing_data, needed_agents)
            
            # 4. Агрегируем результаты
            final_response = self._aggregate_results(routing_data, agent_results)
            
            print("✅ RouterAgent: Задачи распределены и выполнены")
            return final_response
            
        except Exception as e:
            print(f"❌ RouterAgent: Ошибка обработки: {e}")
            return self._create_error_response(routing_data, str(e))
    
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
        """Вызывает специализированный агент (пока заглушка)"""
        # Заглушки для специализированных агентов
        stub_responses = {
            "hotels": f"🏨 Рекомендации отелей для семьи {routing_data.get('family_id', 'unknown')}: [Заглушка - агент отелей]",
            "restaurants": f"🍽️ Рекомендации ресторанов для семьи {routing_data.get('family_id', 'unknown')}: [Заглушка - агент ресторанов]",
            "activities": f"🎯 Рекомендации активностей для семьи {routing_data.get('family_id', 'unknown')}: [Заглушка - агент активностей]",
            "transport": f"🚌 Рекомендации транспорта для семьи {routing_data.get('family_id', 'unknown')}: [Заглушка - агент транспорта]"
        }
        
        return stub_responses.get(agent_name, f"Неизвестный агент: {agent_name}")
    
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
