# app/api/v1/endpoints/health.py
"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import os
from api.dependencies import get_supabase_config, get_openai_config

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """Базовая проверка здоровья API"""
    return {
        "status": "healthy",
        "service": "Ratoncito Pérez Travel Planner",
        "version": "1.0.0"
    }

@router.get("/supabase", response_model=Dict[str, Any])
async def check_supabase_connection(supabase_config: Dict[str, str] = Depends(get_supabase_config)):
    """Проверка подключения к Supabase"""
    try:
        from supabase import create_client, Client
        
        client: Client = create_client(supabase_config["url"], supabase_config["key"])
        
        # Простой запрос для проверки подключения
        result = client.table("families").select("id").limit(1).execute()
        
        return {
            "status": "connected",
            "database": "Supabase",
            "message": "Connection successful"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Supabase connection failed: {str(e)}"
        )

@router.get("/openai", response_model=Dict[str, Any])
async def check_openai_connection(openai_config: Dict[str, str] = Depends(get_openai_config)):
    """Проверка подключения к OpenAI"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            openai_api_key=openai_config["api_key"],
            model="gpt-4o-mini",
            temperature=0.1
        )
        
        # Простой тест
        response = llm.invoke("Hello")
        
        return {
            "status": "connected",
            "llm": "OpenAI",
            "model": "gpt-4o-mini",
            "message": "Connection successful"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI connection failed: {str(e)}"
        )

@router.get("/full", response_model=Dict[str, Any])
async def full_health_check(
    supabase_config: Dict[str, str] = Depends(get_supabase_config),
    openai_config: Dict[str, str] = Depends(get_openai_config)
):
    """Полная проверка всех сервисов"""
    health_status = {
        "api": {"status": "healthy"},
        "supabase": {"status": "unknown"},
        "openai": {"status": "unknown"},
        "overall": "unknown"
    }
    
    # Проверяем Supabase
    try:
        from supabase import create_client
        client = create_client(supabase_config["url"], supabase_config["key"])
        client.table("families").select("id").limit(1).execute()
        health_status["supabase"] = {"status": "healthy"}
    except Exception as e:
        health_status["supabase"] = {"status": "unhealthy", "error": str(e)}
    
    # Проверяем OpenAI
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(openai_api_key=openai_config["api_key"], model="gpt-4o-mini")
        llm.invoke("Hello")
        health_status["openai"] = {"status": "healthy"}
    except Exception as e:
        health_status["openai"] = {"status": "unhealthy", "error": str(e)}
    
    # Определяем общий статус
    all_healthy = all(
        service["status"] == "healthy" 
        for service in health_status.values() 
        if isinstance(service, dict) and "status" in service
    )
    
    health_status["overall"] = "healthy" if all_healthy else "unhealthy"
    
    return health_status
