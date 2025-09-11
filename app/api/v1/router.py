# app/api/v1/router.py
"""
Главный роутер для API версии 1
"""

from fastapi import APIRouter
from .endpoints import health, families, agents

# Создаем главный роутер для v1
api_router = APIRouter()

# Подключаем все endpoints
api_router.include_router(health.router)
api_router.include_router(families.router)
api_router.include_router(agents.router)
