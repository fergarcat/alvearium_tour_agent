import os
import faiss
import numpy as np

VECTOR_DIR = "vector_db"
os.makedirs(VECTOR_DIR, exist_ok=True)
VECTOR_PATH = os.path.join(VECTOR_DIR, "vector_db.index")

def create_or_load_vector_db(embeddings):
    '''
    Crea o carga una base de datos vectorial FAISS.
    
    Args:
        embeddings (np.array): Embeddings de los fragmentos de texto.
    Returns:
        faiss.Index: El índice FAISS cargado o creado.
    '''
    if os.path.exists(VECTOR_PATH):
        index = faiss.read_index(VECTOR_PATH)
        print("Vector DB loaded")
    else:
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings, dtype="float32"))
        faiss.write_index(index, VECTOR_PATH)
        print("Vector DB created and saved")
    return index

def search(query, model, index, chunks, k=3):
    '''
    Realiza una búsqueda de similitud en la base de datos vectorial.
    
    Args:
        query (str): la consulta de busqueda
        model (SentenceTransformer): modelo de embeddings utilizado
        index (faiss.Index): indice FAISS
        chunks (list): lista de fragmentos de texto originales
        k (int): numero de resultados a devolver.
    Returns:
        list: lista de los fragmentos de texto mas relevantes.
    '''
    
    query_emb = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_emb.astype("float32"), k)
    results = [chunks[idx] for idx in indices[0]]
    return results
