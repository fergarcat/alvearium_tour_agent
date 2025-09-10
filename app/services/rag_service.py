import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# LangChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# =====================
# Configuración inicial
# =====================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("⚠️ No se encontró GROQ_API_KEY en .env")

BASE_DIR = Path(__file__).resolve().parent.parent  # /app
DATA_DIR = BASE_DIR / "data"


# =====================
# Construcción del vectorstore
# =====================
def build_vectorstore():
    docs = []
    for file in DATA_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(file))
        file_docs = loader.load()
        print(f"📄 {file.name}: {len(file_docs)} páginas")
        docs.extend(file_docs)

    if not docs:
        raise ValueError("⚠️ No se cargaron documentos desde ningún PDF.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"✂️ Chunks creados: {len(chunks)}")

    # HuggingFace embeddings (gratis y local)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore")
    print("✅ Vectorstore creado y guardado en ./vectorstore")


# =====================
# Cargar vectorstore y buscar
# =====================
def query_vectorstore(query: str, k: int = 3):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    results = vs.similarity_search(query, k=k)
    return [r.page_content for r in results]


# =====================
# Llamada a Groq API
# =====================
def call_groq(messages, model="llama-3.1-8b-instant"):

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"Groq API error {res.status_code}: {res.text}")
    return res.json()["choices"][0]["message"]["content"]


# =====================
# Agente mágico del Ratoncito Pérez
# =====================
def ratoncito_perez_agent(query: str):
    # Recuperar contexto desde PDFs
    pdf_context = query_vectorstore(query, k=3)
    context = "\n\n".join(pdf_context)

    prompt = f"""
    Eres el Ratoncito Pérez 🐭✨, un asistente turístico mágico.
    Tu misión es ayudar a familias que visitan Madrid a planificar su viaje.

    Instrucciones:
    - Usa la información recuperada (gastronomía, transporte, festividades).
    - Habla en tono cálido, mágico y divertido para los niños.
    - Incluye consejos prácticos para los padres.
    - Recomienda actividades, restaurantes, transportes y festividades.
    - Añade siempre un "secreto mágico del Ratoncito Pérez".

    Pregunta del usuario:
    {query}

    Información de contexto:
    {context}
    """

    messages = [{"role": "user", "content": prompt}]
    response = call_groq(messages)
    return response


# =====================
# Main
# =====================
if __name__ == "__main__":
    # Construir vectorstore una vez (luego comentar esta línea)
    build_vectorstore()

    # Ejemplo de consulta
    pregunta = "Qué podemos hacer en Madrid en mayo con niños pequeños"
    respuesta = ratoncito_perez_agent(pregunta)
    print("\n🤖 Respuesta del Ratoncito Pérez:\n")
    print(respuesta)
