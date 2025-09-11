# retriever/vectorstore.py
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def load_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

def query_vectorstore(query, k=3):
    vs = load_vectorstore()
    results = vs.similarity_search(query, k=k)
    return [r.page_content for r in results]
