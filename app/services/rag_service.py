import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

# Utils
from .pdf_loader import download_pdfs, load_all_pdfs

# LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# =====================
# Configuración inicial
# =====================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("⚠️ No se encontró GROQ_API_KEY en .env")

# La ruta base ahora se calcula correctamente desde este archivo
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# =====================
# Construcción del vectorstore
# =====================
def build_vectorstore():
    """Descarga PDFs, construye embeddings y guarda el vectorstore."""
    pdf_paths = download_pdfs("pdf_ids.txt")
    print(f"📥 PDFs descargados: {len(pdf_paths)}")

    all_text = load_all_pdfs(pdf_paths)
    if not all_text.strip():
        raise ValueError("⚠️ No se extrajo texto de los PDFs")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([all_text])
    print(f"✂️ Chunks creados: {len(docs)}")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(VECTORSTORE_DIR))
    print(f"✅ Vectorstore creado en {VECTORSTORE_DIR}")


# =====================
# Consultar vectorstore
# =====================
def query_vectorstore(query: str, vectorstore: FAISS, k: int = 3, score_threshold: float = 0.3):
    """Busca en el vectorstore con puntajes y filtra resultados poco relevantes."""
    results = vectorstore.similarity_search_with_score(query, k=k)

    # Filtrar por score
    filtered = [doc.page_content for doc, score in results if score >= score_threshold]

    if not filtered:
        return ["⚠️ No encontré información relevante en los PDFs"]

    return filtered


# =====================
# Llamada a Groq API
# =====================
def call_groq(messages, model="llama-3.1-8b-instant"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"Groq API error {res.status_code}: {res.text}")
    return res.json()["choices"][0]["message"]["content"]


# =====================
# Agente mágico del Ratoncito Pérez
# =====================
def ratoncito_perez_agent(query: str, vectorstore: FAISS):
    """Agente mágico que responde usando PDFs + Groq."""
    pdf_context = query_vectorstore(query, vectorstore, k=5)
    context = "\n\n".join(pdf_context)

    prompt = f"""
    🐭✨ Soy el Ratoncito Pérez, tu guía turístico mágico en Madrid.

    👨‍👩‍👧 Pregunta de la familia:
    {query}

    📚 Información encontrada en mis libritos mágicos:
    {context}

    ✨ Instrucciones para mi respuesta:
    1. Da recomendaciones claras de actividades, restaurantes y transporte.
    2. Habla en tono cálido, mágico y divertido para los niños.
    3. Incluye consejos prácticos para los padres.
    4. Añade siempre un "secreto mágico del Ratoncito Pérez".
    5. Responde en máximo 5 párrafos.
    """

    messages = [{"role": "user", "content": prompt}]
    response = call_groq(messages)
    return response

# =====================
# Bloque de ejecución principal para testing
# =====================
if __name__ == "__main__":
    print("--- 🚀 Iniciando el sistema RAG del Ratoncito Pérez... ---")
    
    try:
        # Verifica si el vectorstore existe, si no, lo construye
        if not VECTORSTORE_DIR.exists() or not os.listdir(VECTORSTORE_DIR):
            print("⏳ El vectorstore no existe o está vacío. Creando uno nuevo...")
            build_vectorstore()
        else:
            print("✅ El vectorstore ya existe. Saltando la creación.")

        # Carga el vectorstore en memoria para la prueba
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        test_vectorstore = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("✅ Vectorstore cargado para prueba.")
        
        # Ejemplo de una consulta para verificar que todo funciona
        print("\n--- 🧠 Realizando una consulta de prueba... ---")
        test_query = "¿Qué actividades hay en Madrid para familias con niños?"
        
        # Llama a tu agente mágico, pasando el vectorstore
        response = ratoncito_perez_agent(test_query, test_vectorstore)

        print("\n--- ✅ El sistema RAG está funcionando correctamente. ---")
        print("\n✨ La respuesta del Ratoncito Pérez es:")
        print(response)
        
    except Exception as e:
        print(f"\n❌ ¡Ocurrió un error! El sistema RAG no pudo ejecutarse. \nError: {e}")
