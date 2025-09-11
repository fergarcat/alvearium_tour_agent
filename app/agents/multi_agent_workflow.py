# app/agents/multi_agent_workflow.py
"""
Мультиагентный workflow для координации специализированных агентов
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class MultiAgentWorkflow:
    """
    Координатор для управления цепочкой специализированных агентов
    """
    
    def __init__(self):
        """Инициализация workflow с агентами"""
        print("🔧 Инициализация MultiAgentWorkflow...")
        
        # Импортируем существующий PersonalizationReactAgent как координатора
        try:
            from services.personalization_agent import PersonalizationReactAgent
            # Координатор - главный агент, который принимает запросы
            self.coordinator = PersonalizationReactAgent()
            print("✅ Координатор (PersonalizationReactAgent) инициализирован")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации координатора: {e}")
            self.coordinator = None
        
        # Специализированные агенты (пока заглушки, добавим позже)
        self.specialized_agents = {
            "hotels": None,      # Агент отелей
            "restaurants": None, # Агент ресторанов  
            "activities": None,  # Агент активностей
            "transport": None    # Агент транспорта
        }
        
        # Агрегатор ответов
        self.aggregator = ResponseAggregator()
        
        print("✅ MultiAgentWorkflow инициализирован")
        print(f"   - Координатор: {type(self.coordinator).__name__}")
        print(f"   - Специализированных агентов: {len([a for a in self.specialized_agents.values() if a is not None])}")
    
    async def process_request(self, query: str, family_id: str = "default") -> str:
        """
        Основной метод обработки запроса через мультиагентный workflow
        
        Args:
            query: Запрос пользователя
            family_id: ID семьи
            
        Returns:
            Персонализированный ответ
        """
        print(f"\n🚀 MultiAgentWorkflow: Обработка запроса")
        print(f"   Query: {query[:50]}...")
        print(f"   Family ID: {family_id}")
        
        try:
            # 1. Анализ запроса через координатора
            print("📊 Шаг 1: Анализ запроса...")
            analysis = await self._analyze_query(query, family_id)
            print(f"   Результат анализа: {analysis}")
            
            # 2. Определяем, нужны ли специализированные агенты
            needed_agents = self._determine_needed_agents(query, analysis)
            print(f"   Нужные агенты: {needed_agents}")
            
            if not needed_agents:
                # Если специалисты не нужны, используем только координатора
                print("🎯 Используем только координатора...")
                if self.coordinator:
                    return await self.coordinator.process_query(query, family_id)
                else:
                    return f"🐭 ¡Hola! Soy el Ratoncito Pérez. {query} [Координатор недоступен]"
            
            # 3. Параллельный вызов специализированных агентов
            print("🔄 Шаг 2: Параллельные вызовы агентов...")
            specialized_results = await self._call_specialized_agents(
                query, family_id, needed_agents
            )
            
            # 4. Агрегация результатов
            print("📋 Шаг 3: Агрегация результатов...")
            final_response = await self.aggregator.consolidate(
                query, family_id, specialized_results, analysis
            )
            
            print("✅ MultiAgentWorkflow: Запрос обработан успешно")
            return final_response
            
        except Exception as e:
            print(f"❌ MultiAgentWorkflow: Ошибка обработки: {e}")
            # Fallback к координатору
            if self.coordinator:
                try:
                    return await self.coordinator.process_query(query, family_id)
                except Exception as coord_error:
                    print(f"❌ Ошибка координатора: {coord_error}")
                    return f"🐭 ¡Hola! Soy el Ratoncito Pérez. {query} [Ошибка системы]"
            else:
                return f"🐭 ¡Hola! Soy el Ratoncito Pérez. {query} [Координатор недоступен]"
    
    async def _analyze_query(self, query: str, family_id: str) -> Dict[str, Any]:
        """
        Анализ запроса для определения типа помощи
        
        Args:
            query: Запрос пользователя
            family_id: ID семьи
            
        Returns:
            Результат анализа
        """
        # Используем координатора для анализа
        try:
            # Простой анализ на основе ключевых слов
            query_lower = query.lower()
            
            analysis = {
                "query_type": "general",
                "needs_hotels": any(word in query_lower for word in ["hotel", "alojamiento", "dormir", "reservar"]),
                "needs_restaurants": any(word in query_lower for word in ["comer", "restaurante", "cena", "almuerzo", "desayuno"]),
                "needs_activities": any(word in query_lower for word in ["actividad", "hacer", "visitar", "turismo", "museo"]),
                "needs_transport": any(word in query_lower for word in ["llegar", "transporte", "metro", "autobús", "taxi"]),
                "is_planning": any(word in query_lower for word in ["planificar", "viaje", "madrid", "recomendar"]),
                "family_id": family_id,
                "timestamp": datetime.now().isoformat()
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
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа запроса: {e}")
            return {"query_type": "general", "family_id": family_id}
    
    def _determine_needed_agents(self, query: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Определяет, какие специализированные агенты нужны
        
        Args:
            query: Запрос пользователя
            analysis: Результат анализа
            
        Returns:
            Список нужных агентов
        """
        needed_agents = []
        
        if analysis.get("needs_hotels", False):
            needed_agents.append("hotels")
        if analysis.get("needs_restaurants", False):
            needed_agents.append("restaurants")
        if analysis.get("needs_activities", False):
            needed_agents.append("activities")
        if analysis.get("needs_transport", False):
            needed_agents.append("transport")
        
        return needed_agents
    
    async def _call_specialized_agents(
        self, 
        query: str, 
        family_id: str, 
        needed_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Параллельный вызов специализированных агентов
        
        Args:
            query: Запрос пользователя
            family_id: ID семьи
            needed_agents: Список нужных агентов
            
        Returns:
            Результаты от всех агентов
        """
        results = {}
        
        # Пока у нас нет специализированных агентов, используем заглушки
        for agent_name in needed_agents:
            if agent_name in self.specialized_agents:
                try:
                    # Заглушка для специализированного агента
                    result = await self._call_agent_stub(agent_name, query, family_id)
                    results[agent_name] = result
                    print(f"   ✅ {agent_name}: {result[:50]}...")
                except Exception as e:
                    print(f"   ❌ {agent_name}: Ошибка - {e}")
                    results[agent_name] = f"Ошибка агента {agent_name}: {str(e)}"
        
        return results
    
    async def _call_agent_stub(self, agent_name: str, query: str, family_id: str) -> str:
        """
        Заглушка для специализированного агента
        
        Args:
            agent_name: Имя агента
            query: Запрос
            family_id: ID семьи
            
        Returns:
            Заглушка ответа
        """
        # Имитируем задержку работы агента
        await asyncio.sleep(0.1)
        
        stub_responses = {
            "hotels": f"🏨 Рекомендации отелей для семьи {family_id}: [Заглушка - агент отелей]",
            "restaurants": f"🍽️ Рекомендации ресторанов для семьи {family_id}: [Заглушка - агент ресторанов]",
            "activities": f"🎯 Рекомендации активностей для семьи {family_id}: [Заглушка - агент активностей]",
            "transport": f"🚌 Рекомендации транспорта для семьи {family_id}: [Заглушка - агент транспорта]"
        }
        
        return stub_responses.get(agent_name, f"Неизвестный агент: {agent_name}")


class ResponseAggregator:
    """
    Агрегатор для объединения ответов от специализированных агентов
    """
    
    def __init__(self):
        self.name = "ResponseAggregator"
    
    async def consolidate(
        self, 
        query: str, 
        family_id: str, 
        specialized_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> str:
        """
        Объединяет результаты от всех агентов в единый ответ
        
        Args:
            query: Исходный запрос
            family_id: ID семьи
            specialized_results: Результаты от специализированных агентов
            analysis: Анализ запроса
            
        Returns:
            Объединенный ответ
        """
        print(f"📋 Агрегация результатов для семьи {family_id}")
        
        # Заголовок ответа
        response_parts = [
            f"🐭 **Respuesta del Ratoncito Pérez (Multi-Agent):**",
            f"",
            f"**Consulta:** {query}",
            f"**Familia:** {family_id}",
            f"**Tipo de consulta:** {analysis.get('query_type', 'general')}",
            f""
        ]
        
        # Добавляем результаты от специализированных агентов
        if specialized_results:
            response_parts.append("**Recomendaciones especializadas:**")
            response_parts.append("")
            
            for agent_name, result in specialized_results.items():
                agent_emoji = {
                    "hotels": "🏨",
                    "restaurants": "🍽️", 
                    "activities": "🎯",
                    "transport": "🚌"
                }.get(agent_name, "🤖")
                
                response_parts.append(f"{agent_emoji} **{agent_name.title()}:**")
                response_parts.append(f"{result}")
                response_parts.append("")
        
        # Заключение
        response_parts.extend([
            "---",
            f"*Respuesta generada por MultiAgentWorkflow - {datetime.now().strftime('%H:%M:%S')}*"
        ])
        
        return "\n".join(response_parts)


# Пример использования
if __name__ == "__main__":
    import asyncio
    
    async def test_workflow():
        workflow = MultiAgentWorkflow()
        
        # Тестовые запросы
        test_queries = [
            "Quiero planificar un viaje a Madrid con mi familia",
            "¿Qué hoteles me recomiendas?",
            "¿Dónde podemos comer en familia?",
            "¿Qué actividades hay para niños?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"TEST: {query}")
            print('='*60)
            
            response = await workflow.process_request(query, "test_family")
            print(f"\nRESPONSE:\n{response}")
    
    # Запуск теста
    asyncio.run(test_workflow())
