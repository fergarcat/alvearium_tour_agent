# app/agents/personalization_agent.py
import os
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# Импорты из модульной структуры
from models.family_models_supabase import FamilyProfileSupabase, PersonalizedQuery
from core.data_collector import FamilyDataCollector
from services.router_agent import RouterAgent
from tools.personalization_tools import (
    extract_family_info_tool,
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
    route_to_specialized_agent_tool
)

# -----------------------------
# Pure Orchestrator - Main Business Logic
# -----------------------------
class PersonalizedTripPlanner:
    """
    Pure Orchestrator - чистый оркестратор системы
    
    Ответственность:
    - Координация между агентами
    - Выбор стратегии обработки
    - Управление мультиагентным workflow
    - Интеграция с API
    - НЕ управляет данными (делегирует агенту)
    """
    
    def __init__(self):
        print("🚀 Инициализация PersonalizedTripPlanner (Pure Orchestrator)...")
        
        # Инициализация агента с полным управлением данными
        from services.personalization_agent import PersonalizationReactAgent
        from services.router_agent import RouterAgent
        
        self.personalization_agent = PersonalizationReactAgent()
        self.router_agent = RouterAgent()
        
        # Инициализация мультиагентной системы (legacy)
        self.workflow = self._initialize_multi_agent_workflow()
        
        # Инициализация специализированных агентов (legacy)
        self.specialized_agents = self._initialize_specialized_agents()
        
        print("✅ PersonalizedTripPlanner (Pure Orchestrator) инициализирован")
    
    def _initialize_multi_agent_workflow(self):
        """Инициализирует мультиагентный workflow"""
        try:
            from agents.multi_agent_workflow import MultiAgentWorkflow
            workflow = MultiAgentWorkflow()
            print("✅ MultiAgentWorkflow инициализирован")
            return workflow
        except Exception as e:
            print(f"⚠️ Ошибка инициализации MultiAgentWorkflow: {e}")
            return None
    
    def _initialize_specialized_agents(self):
        """Инициализирует специализированные агенты"""
        try:
            # Импортируем существующие агенты (legacy)
            import importlib.util
            spec = importlib.util.spec_from_file_location("llm_agent", "app/services/llm-agent.py")
            llm_agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(llm_agent_module)
            
            agents = {
                "multi_prompt_chain": llm_agent_module.multi_prompt_chain,
                "general_chain": llm_agent_module.general_chain,
                "route_trip_query": llm_agent_module.route_trip_query
            }
            
            print("✅ Специализированные агенты инициализированы")
            return agents
        except Exception as e:
            print(f"⚠️ Ошибка инициализации специализированных агентов: {e}")
            return None
        
    # Методы управления данными перенесены в PersonalizationReactAgent
        
    def process_query(self, query: str, family_id: str = "default") -> str:
        """
        Главный метод оркестрации - новая мультиагентная архитектура
        
        Workflow:
        1. PersonalizationReactAgent собирает информацию
        2. RouterAgent распределяет задачи между специализированными агентами
        3. Агрегация результатов
        4. Возврат персонализированного ответа
        """
        
        try:
            print(f"🎯 Pure Orchestrator: Новая мультиагентная архитектура")
            print(f"   Query: {query[:50]}...")
            print(f"   Family ID: {family_id}")
            
            # 1. Проверяем, есть ли профиль семьи
            profile = self.personalization_agent.get_family_profile(family_id)
            
            if not profile:
                # Если нет профиля - PersonalizationReactAgent приветствует и задает вопросы
                print("🔍 Шаг 1: PersonalizationReactAgent приветствует и собирает информацию...")
                response = self.personalization_agent.process_query(query, family_id)
                print("✅ Pure Orchestrator: Запрос обработан успешно")
                return response
            else:
                # Если есть профиль - используем мультиагентную архитектуру
                print("🔍 Шаг 1: PersonalizationReactAgent собирает информацию...")
                routing_data = self.personalization_agent.prepare_data_for_routing(query, family_id)
                
                # 2. RouterAgent распределяет задачи
                print("🎯 Шаг 2: RouterAgent распределяет задачи...")
                router_response = self.router_agent.process_routing_data(routing_data)
                
                # 3. Форматируем финальный ответ
                print("📋 Шаг 3: Форматирование ответа...")
                final_response = self._format_final_response(query, family_id, router_response, routing_data)
                
                print("✅ Pure Orchestrator: Запрос обработан успешно")
                return final_response
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Pure Orchestrator: Ошибка координации: {e}")
            
            # Fallback к простому агенту
            try:
                print("🔄 Fallback к PersonalizationReactAgent...")
                return self.personalization_agent.process_query(query, family_id)
            except Exception as fallback_error:
                return f"Lo siento, hubo un error al procesar tu consulta: {str(fallback_error)}"
    
    def _format_final_response(self, query: str, family_id: str, router_response: str, routing_data: Dict) -> str:
        """Форматирует финальный ответ для пользователя"""
        try:
            # RouterAgent уже возвращает готовую строку с полным форматированием
            # Просто возвращаем её как есть
            return router_response
            
        except Exception as e:
            print(f"❌ Ошибка форматирования ответа: {e}")
            return f"🐭 **Respuesta del Ratoncito Pérez:**\n\n{query}\n\n[Ошибка форматирования ответа]"
    
    def _needs_multi_agent(self, query: str) -> bool:
        """Определяет, нужен ли мультиагентный подход для запроса"""
        query_lower = query.lower()
        
        # Ключевые слова для мультиагентного подхода
        multi_agent_keywords = [
            "planificar", "viaje completo", "madrid completo", "todo el viaje",
            "recomendar todo", "itinerario completo", "plan completo"
        ]
        
        # Проверяем наличие ключевых слов
        for keyword in multi_agent_keywords:
            if keyword in query_lower:
                return True
        
        # Проверяем множественные потребности
        needs_count = sum([
            any(word in query_lower for word in ["hotel", "alojamiento", "dormir"]),
            any(word in query_lower for word in ["comer", "restaurante", "cena"]),
            any(word in query_lower for word in ["actividad", "hacer", "visitar"]),
            any(word in query_lower for word in ["llegar", "transporte", "metro"])
        ])
        
        return needs_count > 1
    
    # Анализ запросов перенесен в PersonalizationReactAgent
    
    def _process_with_multi_agent_workflow(self, query: str, family_id: str) -> str:
        """Обрабатывает запрос через мультиагентный workflow"""
        try:
            if self.workflow:
                # Используем асинхронный workflow
                import asyncio
                response = asyncio.run(self.workflow.process_request(query, family_id))
                return response
            else:
                # Fallback к агенту
                return self.personalization_agent.process_query(query, family_id)
        except Exception as e:
            print(f"⚠️ Ошибка мультиагентного workflow: {e}")
            # Fallback к агенту
            return self.personalization_agent.process_query(query, family_id)
    
    # Методы управления данными перенесены в PersonalizationReactAgent
    
    def get_workflow_status(self) -> Dict:
        """Возвращает статус мультиагентного workflow"""
        return {
            "workflow_available": self.workflow is not None,
            "specialized_agents_available": self.specialized_agents is not None,
            "personalization_agent_available": self.personalization_agent is not None,
            "orchestrator_type": "Pure Orchestrator"
        }
    
    def get_capabilities(self) -> List[str]:
        """Возвращает список возможностей Pure Orchestrator"""
        capabilities = [
            "Координация между агентами",
            "Выбор стратегии обработки",
            "Управление мультиагентным workflow",
            "Интеграция с API",
            "Fallback к агенту при ошибках"
        ]
        
        if self.workflow:
            capabilities.append("Мультиагентный workflow")
        
        if self.specialized_agents:
            capabilities.append("Специализированные агенты")
        
        # Добавляем возможности агента
        if self.personalization_agent:
            agent_capabilities = self.personalization_agent.get_agent_capabilities()
            capabilities.extend(agent_capabilities)
        
        return capabilities
    
    def start_interactive_session(self, family_id: str = "default"):
        """Запускает интерактивную сессию планирования поездки"""
        print("🎉 ¡Bienvenido al Planificador Mágico del Ratoncito Pérez!")
        print("=" * 60)
        
        # Делегируем инициализацию профиля агенту
        profile = self.personalization_agent.initialize_family_profile(family_id)
        
        print("\n🎯 Ahora puedes hacer preguntas sobre tu viaje a Madrid!")
        print("Ejemplos: '¿Qué hoteles me recomiendas?', '¿Dónde comer con niños?', '¿Qué actividades hacer?'")
        print("Escribe 'salir' para terminar.\n")
        
        while True:
            try:
                query = input("🐭 Tu pregunta: ").strip()
                
                if query.lower() in ["salir", "exit", "quit", "bye"]:
                    print("\n🐭✨ ¡Hasta luego! Que tengas un viaje mágico a Madrid!")
                    break
                
                if not query:
                    print("❌ Por favor, escribe una pregunta.")
                    continue
                
                # Делегируем обработку запроса оркестратору
                response = self.process_query(query, family_id)
                print(f"\n{response}\n")
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n🐭✨ ¡Hasta luego! Que tengas un viaje mágico a Madrid!")
                break
            except Exception as e:
                print(f"❌ ¡Ups! Algo salió mal: {e}")
                print("Inténtalo de nuevo, por favor.\n")

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    planner = PersonalizedTripPlanner()
    
    # Запуск интерактивной сессии
    planner.start_interactive_session()
