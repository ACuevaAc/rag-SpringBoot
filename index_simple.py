import os
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader  # alternativa ligera a PyPDFLoader

docs_path = "./data"
persist_dir = "./chroma_db"

print("1. Leyendo PDFs...")
all_chunks = []
all_metadatas = []
chunk_size = 1000
overlap = 200

def chunk_text(text, chunk_size, overlap):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

for filename in os.listdir(docs_path):
    if filename.endswith(".pdf"):
        path = os.path.join(docs_path, filename)
        reader = PdfReader(path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        chunks = chunk_text(full_text, chunk_size, overlap)
        all_chunks.extend(chunks)
        all_metadatas.extend([{"source": filename} for _ in chunks])

print(f"2. Generados {len(all_chunks)} fragmentos.")

print("3. Conectando a ChromaDB...")
client = chromadb.PersistentClient(path=persist_dir)
ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434/api/embeddings"
)
collection = client.get_or_create_collection(
    name="spring_docs",
    embedding_function=ollama_ef
)

print("4. Insertando fragmentos (esto puede tardar)...")
batch_size = 100
for i in range(0, len(all_chunks), batch_size):
    batch_chunks = all_chunks[i:i+batch_size]
    batch_metas = all_metadatas[i:i+batch_size]
    ids = [f"doc_{j}" for j in range(i, i+len(batch_chunks))]
    collection.add(
        documents=batch_chunks,
        metadatas=batch_metas,
        ids=ids
    )
print("¡Indexación completada!")