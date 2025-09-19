from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List

from app.services.multi_agent_llm import process_user_input, mouse_greeting, conversation_state
from app.services.create_trip import create_trip

app = FastAPI(
    title="Alvearium Tour Agent API", 
    description="API para el agente turístico de Madrid basado en LLM",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class UserInput(BaseModel):
    message: str
    conversation_state: Optional[Dict] = {}

class TripPreferences(BaseModel):
    adults: Optional[str]
    children: Optional[str]
    children_age: Optional[str]
    trip_duration: Optional[str]
    arrival_date: Optional[str]
    departure_date: Optional[str]
    hotels: Optional[str]
    restaurants: Optional[str]
    food_intolerances: Optional[str]
    food_allergies: Optional[str]
    activities: Optional[str]
    transportation: Optional[str]
    special_needs: Optional[str]
    user_language: Optional[str] = "Spanish"

@app.get("/")
async def root():
    """Endpoint de salud de la API"""
    return {"message": "Alvearium Tour Agent API is running"}

@app.post("/chat")
async def chat(user_input: UserInput):
    """
    Procesa la entrada del usuario y devuelve la respuesta del agente
    """
    try:
        response = process_user_input(user_input.message, user_input.conversation_state)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/greeting")
async def get_greeting(language: str = "Spanish"):
    """
    Obtiene el saludo inicial del Ratoncito Pérez
    """
    try:
        greeting = mouse_greeting(language)
        return {"greeting": greeting}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-trip")
async def create_trip_plan(preferences: TripPreferences):
    """
    Crea un plan de viaje basado en las preferencias del usuario
    """
    try:
        trip_plan = create_trip(preferences.model_dump(exclude_unset=True))
        return trip_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
