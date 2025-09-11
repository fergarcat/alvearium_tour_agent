from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

def split_text(text, chunk_size=500, chunk_overlap=50):
    """
    Divide un texto largo en fragmentos más pequeños.
    Args
        text (str): texto a dividir
        chunk_size (int): tamaño maximo de cada fragmento
        chunk_overlap (int): La cantidad de superposicion entre fragmentos
    Returns:
        list: lista de fragmentos de texto
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def generate_embeddings(chunks, model_name="all-MiniLM-L6-v2"):
    '''
    genera embeddings de una lista de fragmentos de texto utilizando un modelo pre-entrenado.
    '''
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings, model
