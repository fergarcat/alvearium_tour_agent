# services/__init__.py
from pathlib import Path
from .rag_service import build_vectorstore, FAISS, HuggingFaceEmbeddings
from .tasks import set_vectorstore


_vectorstore_instance = None

def initialize_rag_system():
    """Initialize the RAG system"""
    global _vectorstore_instance
    if _vectorstore_instance:
        return _vectorstore_instance
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    VECTORSTORE_DIR = BASE_DIR / "vectorstore"
    
    try:
        if not VECTORSTORE_DIR.exists() or not any(VECTORSTORE_DIR.iterdir()):
            print("⏳ Building vectorstore...")
            build_vectorstore()
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        _vectorstore_instance = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        set_vectorstore(_vectorstore_instance)
        print("✅ RAG system initialized successfully")
        return _vectorstore_instance
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return None

def get_vectorstore():
    """Get the initialized vectorstore instance"""
    return _vectorstore_instance

# Auto-initialize when the module is imported
try:
    initialize_rag_system()
except Exception as e:
    print(f"⚠️  Auto-initialization failed: {e}")