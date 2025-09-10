import os
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Importaciones de tu servicio, ahora sin el cache global
from app.services.rag_service import build_vectorstore, ratoncito_perez_agent, query_vectorstore

# Configuración del log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Directorio del vectorstore, debe coincidir con el de rag_service.py
BASE_DIR = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# Variable global para el vectorstore, inicializada a None
_vectorstore = None

# =================================================================
# Evento de inicio: Se ejecuta al arrancar el servidor de FastAPI
# =================================================================
@app.on_event("startup")
def startup_event():
    """
    Inicializa el sistema RAG al iniciar la API.
    Verifica si el vectorstore existe, lo construye si es necesario y lo carga.
    """
    global _vectorstore
    logger.info("--- 🚀 Iniciando el sistema RAG para la API... ---")

    # 1. Verifica si la carpeta del vectorstore existe y no está vacía
    if not VECTORSTORE_DIR.exists() or not os.listdir(VECTORSTORE_DIR):
        logger.warning("⏳ Vectorstore no encontrado. Creando uno nuevo. Esto puede tomar unos minutos...")
        try:
            build_vectorstore()
            logger.info("✅ Vectorstore creado exitosamente.")
        except Exception as e:
            logger.error(f"❌ Error al construir el vectorstore: {e}")
            raise RuntimeError("Error de inicialización: El vectorstore no pudo ser construido.")
    else:
        logger.info("✅ Vectorstore ya existe. Saltando la creación.")

    # 2. Carga el vectorstore en memoria, listo para ser usado por la API
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        _vectorstore = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("✅ Vectorstore cargado en memoria.")
    except Exception as e:
        logger.error(f"❌ Error al cargar el vectorstore: {e}")
        raise RuntimeError("Error de inicialización: El vectorstore no pudo ser cargado.")
    
    logger.info("--- ✨ Sistema RAG listo y operativo. ---")


# =================================================================
# Endpoint de la API
# =================================================================
# Modelo de entrada para la consulta
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_ratoncito_perez(request: QueryRequest):
    """
    Endpoint para hacer preguntas al agente mágico del Ratoncito Pérez.
    Usa el vectorstore cargado en memoria para dar una respuesta.
    """
    global _vectorstore
    query = request.query
    
    # Asegura que el vectorstore esté cargado antes de la consulta
    if _vectorstore is None:
        raise RuntimeError("El sistema RAG aún no está inicializado. Por favor, intente de nuevo en unos momentos.")
    
    logger.info(f"Recibida consulta: '{query}'")
    
    # Llama al agente RAG con la consulta, pasándole el vectorstore
    try:
        response = ratoncito_perez_agent(query, _vectorstore)
        logger.info("Consulta procesada exitosamente.")
        return {"response": response}
    except Exception as e:
        logger.error(f"❌ Error al procesar la consulta: {e}")
        return {"error": "Ocurrió un error al generar la respuesta. Inténtelo más tarde."}

    
