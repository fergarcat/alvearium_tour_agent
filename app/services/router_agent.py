
"""
ReAct Router Agent - использует схему Reasoning → Acting → Observing для принятия решений
"""

import os
import json
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import BaseTool
from app.models.family_models import PersonalizedQuery

class AnalyzeQueryTool(BaseTool):
    """Инструмент для интеллектуального анализа запроса пользователя через LLM"""
    name: str = "analyze_query"
    description: str = "Анализирует запрос пользователя с помощью LLM и определяет, какие типы агентов нужны (activities, restaurants, hotels, transport)"
    llm: ChatOpenAI = None
    
    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    def _run(self, query: str) -> str:
        """Анализирует запрос с помощью LLM и возвращает JSON с нужными агентами"""
        try:
            # Создаем промпт для анализа запроса
            analysis_prompt = PromptTemplate(
                template="""Eres un experto analista de consultas de viajes. Analiza la siguiente consulta del usuario y determina qué tipos de servicios necesita.

CONSULTA DEL USUARIO: "{query}"

TIPOS DE SERVICIOS DISPONIBLES:
1. **activities** - Actividades, museos, parques, talleres, entretenimiento, turismo
2. **restaurants** - Restaurantes, comida, bares, cafés, gastronomía, donde comer
3. **hotels** - Hoteles, alojamiento, hospedaje, donde dormir
4. **transport** - Transporte, cómo llegar, movilidad, metro, autobús, taxi

INSTRUCCIONES:
- Analiza el CONTENIDO y CONTEXTO de la consulta, no solo palabras clave
- Considera las intenciones implícitas del usuario
- Si la consulta es ambigua, considera múltiples opciones
- Si menciona "plan completo" o "día completo", probablemente necesite múltiples servicios

RESPONDE SOLO EN FORMATO JSON:
{{
    "query_type": "activities|restaurants|hotels|transport|combined|general",
    "analysis": {{
        "needs_activities": true/false,
        "needs_restaurants": true/false,
        "needs_hotels": true/false,
        "needs_transport": true/false
    }},
    "reasoning": "Explicación breve de por qué se eligieron estos servicios",
    "confidence": 0.0-1.0
}}

EJEMPLOS:
- "¿Qué museos puedo visitar?" → {{"query_type": "activities", "needs_activities": true}}
- "¿Dónde puedo comer bien?" → {{"query_type": "restaurants", "needs_restaurants": true}}
- "Planifica mi día en Madrid" → {{"query_type": "combined", "needs_activities": true, "needs_restaurants": true}}
- "¿Cómo llegar al aeropuerto?" → {{"query_type": "transport", "needs_transport": true}}""",
                input_variables=["query"]
            )
            
            # Вызываем LLM для анализа
            chain = analysis_prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Парсим JSON ответ
            try:
                result = json.loads(response.content)
                
                # Валидируем результат
                if not isinstance(result, dict):
                    raise ValueError("Respuesta no es un diccionario")
                
                if "query_type" not in result:
                    raise ValueError("Falta query_type en la respuesta")
                
                if "analysis" not in result:
                    raise ValueError("Falta analysis en la respuesta")
                
                # Добавляем reasoning если отсутствует
                if "reasoning" not in result:
                    result["reasoning"] = f"Analizado con LLM: {result.get('query_type', 'unknown')}"
                
                # Добавляем confidence если отсутствует
                if "confidence" not in result:
                    result["confidence"] = 0.8
                
                print(f"🧠 AnalyzeQueryTool: LLM анализ завершен")
                print(f"   • Query type: {result.get('query_type')}")
                print(f"   • Confidence: {result.get('confidence')}")
                print(f"   • Reasoning: {result.get('reasoning')}")
                
                return json.dumps(result, ensure_ascii=False)
                
            except json.JSONDecodeError as e:
                print(f"❌ AnalyzeQueryTool: Ошибка парсинга JSON: {e}")
                print(f"   • LLM ответ: {response.content}")
                
                # Fallback к простому анализу
                return self._fallback_analysis(query)
                
        except Exception as e:
            print(f"❌ AnalyzeQueryTool: Ошибка LLM анализа: {e}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> str:
        """Fallback анализ через ключевые слова если LLM не работает"""
        query_lower = query.lower()
        
        analysis = {
            "needs_activities": any(word in query_lower for word in [
                "actividad", "actividades", "hacer", "visitar", "turismo", "museo", "museos", 
                "parque", "parques", "diversión", "entretenimiento", "taller", "talleres", 
                "excursión", "excursiones", "plan", "planes", "recomendaciones", "atracciones"
            ]),
            "needs_restaurants": any(word in query_lower for word in [
                "comer", "restaurante", "cena", "almuerzo", "desayuno", "desayunar", 
                "cenar", "almorzar", "comida", "bar", "café", "cafeteria", "mesa", 
                "reservar mesa", "donde comer", "donde cenar", "donde desayunar", "gastronomía"
            ]),
            "needs_hotels": any(word in query_lower for word in [
                "hotel", "alojamiento", "dormir", "hospedaje", "reservar", "habitación", 
                "alojarse", "pernoctar", "estancia"
            ]),
            "needs_transport": any(word in query_lower for word in [
                "transporte", "llegar", "moverse", "metro", "autobús", "taxi", "coche", 
                "caminar", "desplazarse", "viajar", "ir a", "cómo llegar"
            ])
        }
        
        # Определяем приоритетный тип запроса
        if analysis["needs_activities"] and analysis["needs_restaurants"]:
            query_type = "combined"
        elif analysis["needs_activities"]:
            query_type = "activities"
        elif analysis["needs_restaurants"]:
            query_type = "restaurants"
        elif analysis["needs_hotels"]:
            query_type = "hotels"
        elif analysis["needs_transport"]:
            query_type = "transport"
        else:
            query_type = "general"
        
        result = {
            "query_type": query_type,
            "analysis": analysis,
            "reasoning": f"Fallback анализ (ключевые слова): {query_type}",
            "confidence": 0.6
        }
        
        print(f"⚠️ AnalyzeQueryTool: Используем fallback анализ")
        return json.dumps(result, ensure_ascii=False)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)

class CallActivitiesAgentTool(BaseTool):
    """Инструмент для вызова ActivitiesAgent"""
    name: str = "call_activities_agent"
    description: str = "Вызывает ActivitiesAgent для получения рекомендаций по активностям"
    activities_agent: Any = None
    
    def __init__(self, activities_agent):
        super().__init__()
        self.activities_agent = activities_agent
    
    def _run(self, routing_data_json: str) -> str:
        """Вызывает ActivitiesAgent с данными маршрутизации"""
        try:
            routing_data = json.loads(routing_data_json)
            
            if not self.activities_agent:
                return json.dumps({
                    "success": False,
                    "error": "ActivitiesAgent не инициализирован",
                    "fallback": "Используем заглушку для активностей"
                }, ensure_ascii=False)
            
            result = self.activities_agent.process_request(routing_data)
            
            # Извлекаем текстовую часть
            if isinstance(result, dict):
                activities_text = result.get("activities_text", "")
                if not activities_text:
                    structured_data = result.get("structured_data", {})
                    if isinstance(structured_data, dict):
                        activities_text = structured_data.get("activities_text", "")
                
                return json.dumps({
                    "success": True,
                    "agent": "activities",
                    "result": activities_text or str(result),
                    "reasoning": "ActivitiesAgent успешно обработал запрос"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "success": True,
                    "agent": "activities", 
                    "result": str(result),
                    "reasoning": "ActivitiesAgent вернул результат"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "reasoning": f"Ошибка в ActivitiesAgent: {e}"
            }, ensure_ascii=False)
    
    async def _arun(self, routing_data_json: str) -> str:
        return self._run(routing_data_json)

class CallRestaurantsAgentTool(BaseTool):
    """Инструмент для вызова RestoranAgent"""
    name: str = "call_restaurants_agent"
    description: str = "Вызывает RestoranAgent для получения рекомендаций по ресторанам"
    restaurants_agent: Any = None
    
    def __init__(self, restaurants_agent):
        super().__init__()
        self.restaurants_agent = restaurants_agent
    
    def _run(self, routing_data_json: str) -> str:
        """Вызывает RestoranAgent с данными маршрутизации"""
        try:
            routing_data = json.loads(routing_data_json)
            
            if not self.restaurants_agent:
                return json.dumps({
                    "success": False,
                    "error": "RestoranAgent не инициализирован",
                    "fallback": "Используем заглушку для ресторанов"
                }, ensure_ascii=False)
            
            result = self.restaurants_agent.process_request(routing_data)
            
            # Извлекаем текстовую часть
            if isinstance(result, dict):
                restaurant_text = result.get("restaurant_text", "")
                if not restaurant_text:
                    structured_data = result.get("structured_data", {})
                    if isinstance(structured_data, dict):
                        restaurant_text = structured_data.get("restaurant_text", "")
                
                return json.dumps({
                    "success": True,
                    "agent": "restaurants",
                    "result": restaurant_text or str(result),
                    "reasoning": "RestoranAgent успешно обработал запрос"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "success": True,
                    "agent": "restaurants",
                    "result": str(result),
                    "reasoning": "RestoranAgent вернул результат"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "reasoning": f"Ошибка в RestoranAgent: {e}"
            }, ensure_ascii=False)
    
    async def _arun(self, routing_data_json: str) -> str:
        return self._run(routing_data_json)

class RouterAgent:
    """
    ReAct Router Agent - использует схему Reasoning → Acting → Observing
    
    Ответственность:
    - Получает данные от PersonalizationReactAgent
    - Анализирует запрос через ReAct цикл
    - Принимает решения о том, какие агенты вызвать
    - Координирует выполнение и собирает результаты
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0
        )
        
        # Инициализируем специализированных агентов
        self.activities_agent = self._init_activities_agent()
        self.restaurants_agent = self._init_restaurant_agent()
        
        # Создаем инструменты для ReAct агента
        self.tools = [
            AnalyzeQueryTool(),
            CallActivitiesAgentTool(self.activities_agent),
            CallRestaurantsAgentTool(self.restaurants_agent)
        ]
        
        # Создаем ReAct агента
        self.react_agent = self._create_react_agent()
        
        print("✅ ReAct RouterAgent инициализирован")
    
    def _create_react_agent(self):
        """Создает ReAct агента с промптом и инструментами"""
        prompt = PromptTemplate(
            template="""Eres un RouterAgent experto que analiza consultas de usuarios y decide qué agentes especializados llamar.

Tienes acceso a las siguientes herramientas:
{tools}

Usa el siguiente formato:

Thought: (razona sobre qué hacer)
Action: (la acción a tomar, debe ser una de [{tool_names}])
Action Input: (entrada para la acción)
Observation: (resultado de la acción)
... (este Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: (razono sobre el resultado final)
Final Answer: (respuesta final al usuario)

IMPORTANTE:
1. SIEMPRE empieza analizando la consulta con analyze_query
2. Basándote en el análisis, decide qué agentes especializados llamar
3. Si necesitas actividades, llama a call_activities_agent
4. Si necesitas restaurantes, llama a call_restaurants_agent
5. Puedes llamar múltiples agentes si es necesario
6. Combina los resultados de manera coherente

Contexto del usuario:
- Query: {query}
- Family ID: {family_id}
- Profile: {profile}

{agent_scratchpad}

¡Comienza analizando la consulta!""",
            input_variables=["tools", "tool_names", "query", "family_id", "profile", "agent_scratchpad"]
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, max_iterations=5)
    
    def _init_activities_agent(self):
        """Инициализирует ActivitiesAgent"""
        try:
            print("🔧 RouterAgent: Инициализация ActivitiesAgent...")
            from app.services.activities_agent import create_activities_agent
            agent = create_activities_agent()
            print(f"✅ RouterAgent: ActivitiesAgent успешно инициализирован: {type(agent)}")
            return agent
        except Exception as e:
            print(f"❌ RouterAgent: Ошибка инициализации ActivitiesAgent: {e}")
            import traceback
            print(f"📋 Детали ошибки: {traceback.format_exc()}")
            return None
    
    def _init_restaurant_agent(self):
        """Инициализирует RestoranAgent"""
        try:
            print("🔧 RouterAgent: Инициализация RestoranAgent...")
            from app.services.restoran_agent import create_restaurant_agent
            agent = create_restaurant_agent()
            print(f"✅ RouterAgent: RestoranAgent успешно инициализирован: {type(agent)}")
            return agent
        except Exception as e:
            print(f"❌ RouterAgent: Ошибка инициализации RestoranAgent: {e}")
            import traceback
            print(f"📋 Детали ошибки: {traceback.format_exc()}")
            return None
    
    def process_routing_data(self, routing_data: Dict) -> str:
        """
        Главный метод обработки данных через ReAct агента
        
        ReAct Workflow:
        1. Reasoning: Анализирует запрос и определяет стратегию
        2. Acting: Вызывает соответствующие инструменты (агенты)
        3. Observing: Оценивает результаты и принимает решения
        4. Повторяет цикл до получения полного ответа
        """
        try:
            print(f"🧠 ReAct RouterAgent: Начинаю анализ через ReAct цикл")
            print(f"   Query: {routing_data.get('query', '')[:50]}...")
            print(f"   Family ID: {routing_data.get('family_id', 'unknown')}")
            
            # Подготавливаем контекст для ReAct агента
            query = routing_data.get('query', '')
            family_id = routing_data.get('family_id', 'unknown')
            profile = routing_data.get('profile', {})
            
            # Создаем JSON строку для передачи в инструменты
            routing_data_json = json.dumps(routing_data, ensure_ascii=False)
            
            # Запускаем ReAct агента
            print(f"🔄 ReAct RouterAgent: Запуск цикла Reasoning → Acting → Observing")
            
            result = self.react_agent.invoke({
                "query": query,
                "family_id": family_id,
                "profile": json.dumps(profile, ensure_ascii=False),
                "routing_data": routing_data_json
            })
            
            print("✅ ReAct RouterAgent: Цикл завершен успешно")
            return result.get("output", "No se pudo procesar la consulta")
            
        except Exception as e:
            print(f"❌ ReAct RouterAgent: Ошибка в ReAct цикле: {e}")
            import traceback
            print(f"📋 Детали ошибки: {traceback.format_exc()}")
            return self._create_error_response_text(routing_data, str(e))
    
    def _create_error_response_text(self, routing_data: Dict, error: str) -> str:
        """Создает ответ об ошибке"""
        return f"""
❌ **Error del RouterAgent:**

No se pudo procesar la consulta debido a un error técnico.

**Detalles del error:** {error}

**Consulta:** {routing_data.get('query', 'N/A')}
**Family ID:** {routing_data.get('family_id', 'N/A')}

Por favor, intenta reformular tu consulta o contacta al soporte técnico.
"""
    
    def _create_simple_response_text(self, routing_data: Dict) -> str:
        """Создает простой ответ без специализированных агентов"""
        return f"""
🤖 **Respuesta del RouterAgent:**

Hola! He recibido tu consulta: "{routing_data.get('query', '')}"

Para poder ayudarte mejor, necesito más información específica sobre lo que buscas:
- ¿Actividades para hacer?
- ¿Restaurantes para comer?
- ¿Hoteles para alojarse?
- ¿Transporte para moverse?

Por favor, especifica qué tipo de recomendaciones necesitas.
"""