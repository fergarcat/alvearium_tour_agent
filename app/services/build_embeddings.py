from pathlib import Path
from pdf_loader import download_pdfs, load_all_pdfs
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# =====================
# Configuración inicial
# =====================
BASE_DIR = Path(__file__).resolve().parent.parent  # /app
VECTORSTORE_DIR = BASE_DIR / "vectorstore"


# =====================
# Construcción del vectorstore
# =====================
def build_embeddings():
    """
    Descarga los PDFs listados en pdf_ids.txt, 
    genera embeddings y guarda el vectorstore en app/vectorstore.
    """
    # 1. Descargar PDFs
    pdf_paths = download_pdfs("pdf_ids.txt")
    print(f"📥 PDFs descargados: {len(pdf_paths)}")

    # 2. Cargar todo el texto
    all_text = load_all_pdfs(pdf_paths)
    if not all_text.strip():
        raise ValueError("⚠️ No se pudo extraer texto de los PDFs")

    # 3. Dividir en chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([all_text])
    print(f"✂️ Chunks creados: {len(docs)}")

    # 4. Generar embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 5. Construir y guardar el vectorstore
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(VECTORSTORE_DIR))
    print(f"✅ Vectorstore creado en {VECTORSTORE_DIR}")


# =====================
# Main
# =====================
if __name__ == "__main__":
    build_embeddings()
