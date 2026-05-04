import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import ollama

# Configuración de rutas (misma que usaste en index_simple.py)
persist_dir = "./chroma_db"
COLLECTION_NAME = "spring_docs"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"

# Cargar la base de datos vectorial (solo una vez, gracias a @st.cache_resource)
@st.cache_resource
def load_chroma_collection():
    client = chromadb.PersistentClient(path=persist_dir)
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
        url="http://localhost:11434/api/embeddings"
    )
    # La colección ya existe gracias al indexado previo
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ollama_ef)
    return collection

# Función para buscar fragmentos relevantes en ChromaDB
def retrieve_context(query, collection, n_results=3):
    # El embedding de la pregunta lo hace Chroma automáticamente usando la misma función
    results = collection.query(query_texts=[query], n_results=n_results)
    # results['documents'] es una lista de listas: [[doc1, doc2, ...]]
    documents = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    return documents, metadatas

# Función para generar respuesta con Ollama
def generate_answer(query, context_docs):
    # Unir los fragmentos en un solo texto
    context = "\n\n".join(context_docs)
    prompt = f"""Eres un asistente experto en Spring Boot. Responde la pregunta basándote ÚNICAMENTE en el siguiente contexto. Si la respuesta no está en el contexto, di "No tengo suficiente información en la documentación proporcionada".

Contexto:
{context}

Pregunta: {query}

Respuesta:"""
    
    response = ollama.chat(model=LLM_MODEL, messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Asistente Spring Boot RAG", layout="wide")
st.title("📘 Asistente RAG - Documentación de Spring Boot")
st.markdown("Haz preguntas sobre los manuales que has indexado.")

# Cargar la colección (una sola vez)
collection = load_chroma_collection()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input del usuario
if prompt := st.chat_input("¿Qué quieres saber sobre Spring Boot?"):
    # Añadir pregunta al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 1. Recuperar contexto relevante
    with st.spinner("Buscando en la documentación..."):
        context_docs, metadatas = retrieve_context(prompt, collection, n_results=3)
    
    if not context_docs:
        respuesta = "No encontré fragmentos relevantes en la documentación. ¿Puedes reformular la pregunta?"
    else:
        # 2. Generar respuesta con el LLM
        with st.spinner("Generando respuesta..."):
            respuesta = generate_answer(prompt, context_docs)
    
    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(respuesta)
        # Opcional: mostrar fuentes
        with st.expander("📄 Fuentes consultadas"):
            for i, doc in enumerate(context_docs):
                fuente = metadatas[i].get("source", "desconocida") if metadatas else "desconocida"
                st.write(f"**Fuente {i+1}:** {fuente}")
                st.write(doc[:500] + "..." if len(doc) > 500 else doc)
                st.write("---")
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})