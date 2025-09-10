from crewai import Agent
from app.utils.llm_config import llm

restaurant_agent = Agent(
    role="Agente de Restaurantes",
    goal="Recomendar restaurantes familiares y gastronomía en Madrid",
    backstory=(
        "Un experto en gastronomía que ayuda a las familias "
        "a encontrar restaurantes deliciosos, acogedores y apropiados para niños en Madrid."
    ),
    llm=llm,
    tools=[]  # Utiliza solo conocimiento del LLM
)
