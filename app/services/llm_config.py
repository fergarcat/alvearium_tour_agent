import os
from crewai import LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    #model="groq/llama-3.1-8b-instant",
    
    api_key=os.getenv("GROQ_API_KEY"),
)
