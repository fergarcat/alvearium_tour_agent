# app/core/router_agent.py
"""
Роутер агент для маршрутизации запросов к специализированным агентам
"""

import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class RouterAgent:
    """Сервисный класс для маршрутизации запросов"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.1
        )
        
        # Ключевые слова для маршрутизации
        self.keywords = {
            "hotels": ["hotel", "alojamiento", "hospedaje", "dormir", "habitación", "reserva"],
            "restaurants": ["restaurante", "comer", "cena", "almuerzo", "desayuno", "comida", "cocina"],
            "activities": ["actividad", "actividades", "museo", "parque", "teatro", "espectáculo", "diversión"],
            "transportation": ["transporte", "llegar", "ir", "metro", "autobús", "taxi", "coche", "caminar"],
            "all": ["plan", "completo", "todo", "itinerario", "viaje", "recomendaciones"]
        }
    
    def route_personalized_query(self, personalized_context: str, suggested_agent: str = "all") -> str:
        """
        Маршрутизирует персонализированный запрос к нужному агенту
        """
        try:
            # Простая маршрутизация по ключевым словам
            context_lower = personalized_context.lower()
            
            for agent, keywords in self.keywords.items():
                if any(keyword in context_lower for keyword in keywords):
                    return agent
            
            return suggested_agent
            
        except Exception as e:
            print(f"Ошибка маршрутизации: {e}")
            return "all"
    
    def route_by_keywords(self, query: str) -> str:
        """
        Простая маршрутизация по ключевым словам
        """
        query_lower = query.lower()
        
        # Подсчитываем совпадения для каждого агента
        scores = {}
        for agent, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[agent] = score
        
        # Возвращаем агента с наибольшим количеством совпадений
        if scores:
            return max(scores, key=scores.get)
        
        return "all"
    
    def get_agent_description(self, agent_name: str) -> str:
        """
        Возвращает описание агента
        """
        descriptions = {
            "hotels": "Специализируется на рекомендациях по отелям и размещению",
            "restaurants": "Специализируется на рекомендациях по ресторанам и еде",
            "activities": "Специализируется на рекомендациях по активностям и развлечениям",
            "transportation": "Специализируется на рекомендациях по транспорту",
            "all": "Предоставляет комплексные рекомендации по всем аспектам путешествия"
        }
        
        return descriptions.get(agent_name, "Агент не найден")
    
    def analyze_query_intent(self, query: str) -> Dict[str, any]:
        """
        Анализирует намерение запроса
        """
        query_lower = query.lower()
        
        # Определяем тип запроса
        query_type = self.route_by_keywords(query)
        
        # Определяем срочность (простая эвристика)
        urgency_keywords = ["urgente", "rápido", "inmediato", "ahora"]
        is_urgent = any(keyword in query_lower for keyword in urgency_keywords)
        
        # Определяем сложность
        complexity_keywords = ["complejo", "detallado", "específico", "personalizado"]
        is_complex = any(keyword in query_lower for keyword in complexity_keywords)
        
        return {
            "query_type": query_type,
            "is_urgent": is_urgent,
            "is_complex": is_complex,
            "confidence": 0.8  # Простая уверенность
        }
