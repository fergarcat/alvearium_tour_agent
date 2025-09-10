from pdf_loader import download_pdfs, load_all_pdfs
from embedder import split_text, generate_embeddings
from vector_store import create_or_load_vector_db, search

# descargar y cargar PDFs
pdf_paths = download_pdfs()
pdf_text = load_all_pdfs(pdf_paths)

# generar embeddings
chunks = split_text(pdf_text)
embeddings, model = generate_embeddings(chunks)

# crear/cargar vectores
index = create_or_load_vector_db(embeddings)

# ejemplo de prueba
query = "What is the main conclusion of the document?"
results = search(query, model, index, chunks, k=3)

print("\nSearch results:\n")
for i, fragment in enumerate(results, 1):
    print(f"Fragment {i}:\n{fragment}\n")
