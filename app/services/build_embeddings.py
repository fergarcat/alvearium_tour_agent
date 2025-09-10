# ingestion/build_embeddings.py
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Cargar PDFs
pdfs = [
    "data/Gastronomia_Madrid.pdf",
    "data/Transporte_publico_Madrid.pdf",
    "data/Festividades_Madrid.pdf"
]

docs = []
for pdf in pdfs:
    loader = PyPDFLoader(pdf)
    docs.extend(loader.load())

# Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(chunks, embeddings)

# Guardar índice local
vectorstore.save_local("vectorstore")
