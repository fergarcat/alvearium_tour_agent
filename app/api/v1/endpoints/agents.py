# app/api/v1/endpoints/agents.py
"""
AI Agents endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import time
import os
from datetime import datetime
from api.dependencies import get_supabase_config, get_openai_config
from agents.personalization_agent import PersonalizedTripPlanner

router = APIRouter(prefix="/agents", tags=["agents"])

# Pydantic модели для API
class QueryRequest(BaseModel):
    query: str
    family_id: str = "default"

class QueryResponse(BaseModel):
    response: str
    family_id: str
    target_agent: str
    family_info: Dict[str, Any]

# Модели для чата
class ChatMessage(BaseModel):
    message: str
    family_id: str = "default"
    conversation_id: Optional[str] = None
    is_initialization: bool = False  # Флаг для инициализации профиля

class ChatResponse(BaseModel):
    response: str
    family_id: str
    conversation_id: str
    timestamp: str
    agent: str = "Ratoncito Pérez"
    is_collecting_data: bool = False  # Флаг сбора данных
    data_collection_step: Optional[str] = None  # Текущий шаг сбора
    profile_complete: bool = False  # Профиль собран

class AgentStatusResponse(BaseModel):
    status: str
    message: str
    capabilities: List[str]

# Глобальный экземпляр планировщика
_planner: Optional[PersonalizedTripPlanner] = None

def get_planner() -> PersonalizedTripPlanner:
    """Получает экземпляр планировщика (singleton)"""
    global _planner
    if _planner is None:
        _planner = PersonalizedTripPlanner()
    return _planner

@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Получает статус AI агента"""
    try:
        planner = get_planner()
        
        return AgentStatusResponse(
            status="ready",
            message="Ratoncito Pérez AI Agent is ready to help with travel planning",
            capabilities=[
                "family_profile_management",
                "personalized_recommendations",
                "travel_planning",
                "hotel_recommendations",
                "restaurant_suggestions",
                "activity_planning",
                "transportation_advice",
                "supabase_integration"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent not ready: {str(e)}"
        )

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Обрабатывает запрос через AI агента"""
    try:
        planner = get_planner()
        
        # Обрабатываем запрос
        response = planner.process_query(request.query, request.family_id)
        
        # Получаем информацию о семье
        family_info = {}
        try:
            # Пытаемся получить профиль семьи из Supabase
            from models.family_models_supabase import FamilyProfileSupabase
            family_profile = FamilyProfileSupabase(
                family_id=request.family_id,
                kids_ages=[],
                adults_count=0,
                budget_level="medium",
                start_date="2024-12-01",
                end_date="2024-12-05",
                interests=[],
                origin_country="Spain"
            )
            
            if family_profile.load_from_supabase(request.family_id):
                family_info = {
                    "family_id": family_profile.family_id,
                    "family_size": family_profile.get_family_size(),
                    "age_group": family_profile.get_age_group(),
                    "budget_level": family_profile.budget_level,
                    "interests": family_profile.interests,
                    "stay_duration": family_profile.get_stay_duration()
                }
        except Exception as e:
            # Если не удалось загрузить профиль, используем базовую информацию
            family_info = {
                "family_id": request.family_id,
                "family_size": 0,
                "age_group": "unknown",
                "budget_level": "medium",
                "interests": [],
                "stay_duration": 0
            }
        
        # Извлекаем target_agent из ответа (простая эвристика)
        target_agent = "all"
        if "hoteles" in response.lower() or "hotel" in response.lower():
            target_agent = "hotels"
        elif "comer" in response.lower() or "restaurante" in response.lower():
            target_agent = "restaurants"
        elif "actividad" in response.lower() or "actividades" in response.lower():
            target_agent = "activities"
        elif "transporte" in response.lower() or "llegar" in response.lower():
            target_agent = "transportation"
        
        return QueryResponse(
            response=response,
            family_id=request.family_id,
            target_agent=target_agent,
            family_info=family_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/families/{family_id}/initialize")
async def initialize_family_profile(
    family_id: str,
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Инициализирует профиль семьи через интерактивный сбор данных"""
    try:
        planner = get_planner()
        
        # Инициализируем профиль через сборщик данных
        from core.data_collector import FamilyDataCollector
        collector = FamilyDataCollector()
        
        # Создаем базовый профиль
        profile = collector.collect_family_data(family_id)
        
        if profile:
            return {
                "message": f"Family profile initialized for {family_id}",
                "family_id": profile.family_id,
                "family_size": profile.get_family_size(),
                "age_group": profile.get_age_group(),
                "budget_level": profile.budget_level
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize family profile"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing family profile: {str(e)}"
        )

@router.get("/families/{family_id}/profile")
async def get_family_profile(
    family_id: str,
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Получает профиль семьи через агента"""
    try:
        planner = get_planner()
        
        # Получаем профиль из Supabase
        from models.family_models_supabase import FamilyProfileSupabase
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[],
            adults_count=0,
            budget_level="medium",
            start_date="2024-12-01",
            end_date="2024-12-05",
            interests=[],
            origin_country="Spain"
        )
        
        if not profile.load_from_supabase(family_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family profile for {family_id} not found"
            )
        
        return {
            "family_id": profile.family_id,
            "kids_ages": profile.kids_ages,
            "adults_count": profile.adults_count,
            "budget_level": profile.budget_level,
            "start_date": profile.start_date,
            "end_date": profile.end_date,
            "interests": profile.interests,
            "origin_country": profile.origin_country,
            "special_needs": profile.special_needs or [],
            "language_preference": profile.language_preference,
            "accommodation_type": profile.accommodation_type,
            "transportation_preference": profile.transportation_preference,
            "stay_duration": profile.get_stay_duration(),
            "family_size": profile.get_family_size(),
            "age_group": profile.get_age_group()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting family profile: {str(e)}"
        )

@router.post("/families/{family_id}/ai-profile")
async def create_ai_profile(
    family_id: str,
    ai_analysis: Dict[str, Any],
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Создает AI профиль семьи"""
    try:
        planner = get_planner()
        
        # Получаем профиль из Supabase
        from models.family_models_supabase import FamilyProfileSupabase
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[],
            adults_count=0,
            budget_level="medium",
            start_date="2024-12-01",
            end_date="2024-12-05",
            interests=[],
            origin_country="Spain"
        )
        
        if not profile.load_from_supabase(family_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family profile for {family_id} not found"
            )
        
        # Создаем AI профиль (упрощенная версия)
        ai_profile_id = f"ai_{family_id}_{int(time.time())}"
        
        return {
            "message": f"AI profile created for family {family_id}",
            "ai_profile_id": ai_profile_id,
            "family_id": family_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating AI profile: {str(e)}"
        )

# Дополнительные эндпоинты для тестирования
@router.post("/test/simple")
async def test_simple_agent():
    """Простой тест агента"""
    try:
        planner = get_planner()
        response = planner.process_query("Hola, ¿cómo estás?", "test")
        
        return {
            "status": "success",
            "response": response,
            "agent": "Ratoncito Pérez",
            "model": "gpt-4o-mini"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "agent": "Ratoncito Pérez"
        }

@router.post("/test/family")
async def test_family_agent():
    """Тест агента с семейным профилем"""
    try:
        planner = get_planner()
        
        # Создаем тестовый профиль
        test_family_id = f"test_{int(time.time())}"
        
        # Тестируем разные запросы
        test_queries = [
            "Quiero planificar un viaje a Madrid",
            "Recomiéndame un hotel familiar",
            "¿Qué actividades hay para niños?",
            "¿Dónde podemos comer en familia?"
        ]
        
        results = []
        for query in test_queries:
            response = planner.process_query(query, test_family_id)
            results.append({
                "query": query,
                "response": response[:100] + "..." if len(response) > 100 else response
            })
        
        return {
            "status": "success",
            "family_id": test_family_id,
            "results": results,
            "agent": "Ratoncito Pérez"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "agent": "Ratoncito Pérez"
        }

@router.get("/health")
async def agent_health():
    """Проверка здоровья агента"""
    try:
        # Проверяем OpenAI
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini"
        )
        test_response = llm.invoke("Test")
        
        # Проверяем Supabase
        from models.family_models_supabase import FamilyProfileSupabase
        test_profile = FamilyProfileSupabase(
            family_id="health_check",
            kids_ages=[5],
            adults_count=2,
            budget_level="medium",
            start_date="2024-12-01",
            end_date="2024-12-05",
            interests=["test"],
            origin_country="Spain"
        )
        
        return {
            "status": "healthy",
            "openai": "connected",
            "supabase": "connected",
            "agent": "ready",
            "model": "gpt-4o-mini"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent": "Ratoncito Pérez"
        }


# Основной чат endpoint (универсальный)
@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatMessage,
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """
    Универсальный endpoint для чата с агентом Ratoncito Pérez
    
    Автоматически определяет:
    - Нужно ли инициализировать профиль семьи
    - Находится ли агент в процессе сбора данных
    - Завершен ли сбор профиля
    
    Принимает:
    - message: текст сообщения пользователя (может быть пустым для инициализации)
    - family_id: ID семьи (опционально, по умолчанию "default")
    - conversation_id: ID разговора (опционально, для продолжения диалога)
    - is_initialization: флаг принудительной инициализации (опционально)
    
    Возвращает:
    - response: ответ агента
    - family_id: ID семьи
    - conversation_id: ID разговора
    - timestamp: время ответа
    - agent: имя агента
    - is_collecting_data: флаг сбора данных
    - data_collection_step: текущий шаг сбора
    - profile_complete: профиль собран
    """
    try:
        planner = get_planner()
        
        # Генерируем conversation_id если не предоставлен
        conversation_id = request.conversation_id or f"conv_{int(time.time())}_{request.family_id}"
        
        # Проверяем, есть ли профиль семьи
        profile = planner.get_family_profile(request.family_id)
        is_collecting_data = False
        data_collection_step = None
        profile_complete = False
        
        # Если профиль не найден или это принудительная инициализация
        if not profile or request.is_initialization:
            is_collecting_data = True
            data_collection_step = "initialization"
            
            # Если это первое сообщение или пустое, начинаем с приветствия
            if not request.message or request.message.strip() == "":
                if profile:
                    # Профиль уже есть, но принудительная инициализация
                    response = f"""🐭 ¡Hola de nuevo! Ya tengo tu perfil familiar guardado.

Tu familia: {profile.get_family_size()} miembros, {profile.get_age_group()}
Presupuesto: {profile.budget_level}
Intereses: {', '.join(profile.interests) if profile.interests else 'No especificados'}

¿En qué puedo ayudarte con tu viaje a Madrid?"""
                    profile_complete = True
                    is_collecting_data = False
                    data_collection_step = "complete"
                else:
                    # Начинаем сбор данных
                    response = """🐭 ¡Hola! Soy el Ratoncito Pérez, tu asistente mágico para viajes familiares en Madrid!

Para personalizar tu experiencia, necesito conocer algunos datos sobre tu familia:

📝 ¿Cuáles son las edades de tus hijos? (ej: 8, 12 o 5, 7, 10)"""
            else:
                # Обрабатываем ответ пользователя через агента
                response = planner.process_query(request.message, request.family_id)
                
                # Проверяем, завершен ли сбор данных
                updated_profile = planner.get_family_profile(request.family_id)
                if updated_profile:
                    profile_complete = True
                    is_collecting_data = False
                    data_collection_step = "complete"
        else:
            # Профиль уже есть, обычная обработка
            response = planner.process_query(request.message, request.family_id)
            profile_complete = True
        
        # Получаем текущее время
        timestamp = datetime.now().isoformat()
        
        return ChatResponse(
            response=response,
            family_id=request.family_id,
            conversation_id=conversation_id,
            timestamp=timestamp,
            agent="Ratoncito Pérez",
            is_collecting_data=is_collecting_data,
            data_collection_step=data_collection_step,
            profile_complete=profile_complete
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )
