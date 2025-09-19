import os
from dotenv import load_dotenv
from crewai import LLM

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# Conexión a OpenAI a través de variables de entorno
llm = LLM(
    model="gpt-4o",  # o "gpt-4", "gpt-3.5-turbo"
    api_key=os.getenv("OPENAI_API_KEY")
)
