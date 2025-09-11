# app/main.py
"""
Главный файл приложения FastAPI
"""

import sys
import os
from pathlib import Path

# Добавляем текущую папку в sys.path для корректных импортов
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем приложение FastAPI
app = FastAPI(
    title="Ratoncito Pérez Travel Planner API",
    description="""
    🐭 **API для магического планировщика поездок Ratoncito Pérez**
    
    Этот API предоставляет персонализированные рекомендации по планированию поездок в Мадрид для семей.
    
    ## Возможности:
    - 👨‍👩‍👧‍👦 Управление профилями семей
    - 🤖 AI-агенты для персонализации
    - 🏨 Рекомендации по отелям
    - 🍽️ Предложения ресторанов
    - 🎯 Планирование активностей
    - 🚌 Советы по транспорту
    - 🗄️ Интеграция с Supabase
    
    ## Версии API:
    - **v1**: Текущая версия с полным функционалом
    """,
    version="1.0.0",
    contact={
        "name": "Ratoncito Pérez Team",
        "email": "support@ratoncitoperez.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API роутеры
from api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

# Корневой endpoint
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "🐭 ¡Bienvenido al Planificador Mágico del Ratoncito Pérez!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health/",
        "status": "ready"
    }

# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик ошибок"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Algo salió mal en el servidor. ¡El Ratoncito Pérez está trabajando para solucionarlo!",
            "details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "Contact support for details"
        }
    )

# Проверка переменных окружения при запуске
@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "OPENAI_API_KEY"]
    optional_vars = ["GOOGLE_PLACES_API_KEY", "OPENWEATHER_API_KEY", "EVENTBRITE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Внимание: Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("   Некоторые функции могут работать некорректно")
    else:
        print("✅ Все необходимые переменные окружения настроены")
    
    # Проверяем опциональные API ключи
    available_apis = []
    for var in optional_vars:
        if os.getenv(var):
            available_apis.append(var.replace("_API_KEY", "").replace("_", " ").title())
    
    if available_apis:
        print(f"🔑 Доступные API: {', '.join(available_apis)}")
    else:
        print("ℹ️ API ключи не настроены - будут использоваться моковые данные")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
