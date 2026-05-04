# 📘 Asistente RAG - Documentación de Spring Boot

Un asistente inteligente basado en **RAG (Retrieval Augmented Generation)** que responde preguntas sobre la documentación de Spring Boot utilizando modelos de IA locales.

---

## 📋 Tabla de Contenidos

1. [¿Qué es RAG?](#qué-es-rag)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura de Carpetas](#estructura-de-carpetas)
5. [Instalación](#instalación)
6. [Cómo Funciona](#cómo-funciona)
7. [Uso](#uso)
8. [Flujo de Datos](#flujo-de-datos)

---

## 🤖 ¿Qué es RAG?

**RAG (Retrieval Augmented Generation)** es una técnica que combina dos componentes:

### 1. **Retrieval (Recuperación)**
- Busca fragmentos relevantes de documentos basándose en una consulta
- Utiliza vectores/embeddings para encontrar contenido similar
- Es más eficiente que procesar toda la documentación

### 2. **Generation (Generación)**
- Toma los fragmentos recuperados como contexto
- Usa un modelo de lenguaje (LLM) para generar respuestas coherentes
- Genera respuestas más precisas y fundamentadas que si usara solo la IA

### ¿Por qué RAG?
- ✅ Respuestas basadas en hechos reales (no alucinaciones)
- ✅ Documentación actualizada sin reentrenar modelos
- ✅ Funciona completamente **offline** (sin internet)
- ✅ Control total sobre los datos
- ✅ Uso eficiente de recursos

---

## 🏗️ Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────┐
│                   USUARIO                               │
│              (Streamlit Web App)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   ┌─────────┐                  ┌──────────┐
   │ Pregunta│                  │ Respuesta│
   └────┬────┘                  └────▲─────┘
        │                             │
        │ 1. EMBEDDING                │
        ▼                             │ 5. RESPUESTA
   ┌──────────────┐                  │
   │ OLLAMA       │                  │ 4. LLM (GENERACIÓN)
   │ nomic-       │                  │
   │ embed-text   │                  │
   └────┬─────────┘                  │
        │                       ┌────┴──────┐
        │ 2. BÚSQUEDA          │  OLLAMA    │
        ▼                       │ llama3.2   │
   ┌────────────────────┐      └──▲─────────┘
   │   ChromaDB         │         │
   │ (Base Vectorial)   │         │
   │                    │    3. CONTEXTO
   │  spring_docs       │   (Top K documentos)
   │  collection        │
   └────────────────────┘
        ▲
        │ Indexación (una sola vez)
        │
   ┌────┴────────────────────┐
   │    PDFs en /data        │
   │  (Spring Documentation) │
   └─────────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

### **1. ChromaDB** 🗄️
- **Base de datos vectorial** que almacena embeddings de los documentos
- Almacena fragmentos de texto junto con sus vectores (representaciones numéricas)
- Permite búsquedas rápidas y precisas usando similitud de vectores
- **Persistent**: Almacena los datos en disco (`./chroma_db`)

### **2. Ollama** 🦙
Ejecuta modelos de IA **completamente locales** sin necesidad de APIs externas:
- **nomic-embed-text**: Convierte texto en vectores (embeddings)
- **llama3.2:3b**: Modelo de lenguaje para generar respuestas

### **3. Streamlit** 🎨
Framework para crear interfaces web interactivas:
- Crea un chat visual sin necesidad de HTML/CSS/JavaScript
- Maneja el estado de las conversaciones automáticamente
- Renderiza componentes con una sola función

### **4. PyPDF2** 📄
Lee y extrae texto de archivos PDF

---

## 📁 Estructura de Carpetas

```
spring-rag-app/
│
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias de Python
├── app.py                       # Interfaz Streamlit (chatbot)
├── index_simple.py              # Script de indexación
│
├── data/                        # 📚 PDFs de documentación
│   └── *.pdf                    # (Debes agregar tus PDFs aquí)
│
├── chroma_db/                   # 🗄️ Base de datos vectorial
│   ├── chroma.sqlite3           # Almacenamiento persistente
│   └── ...                      # (Se crea automáticamente)
│
└── env/                         # 🐍 Entorno virtual Python
    └── ...                      # (Se crea con venv)
```

### ¿Qué hace cada carpeta?

- **`data/`**: Lugar donde pones los archivos PDF que quieres indexar
- **`chroma_db/`**: Almacena la base de datos vectorial (no la modifiques manualmente)
- **`env/`**: Entorno aislado con todas las librerías necesarias

---

## 📦 Instalación

### Paso 1: Instalar Ollama
Descarga e instala Ollama desde: https://ollama.ai

Luego, descarga los modelos necesarios en una terminal:
```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

Inicia el servidor de Ollama (debe estar corriendo siempre):
```bash
ollama serve
```

### Paso 2: Configurar el Entorno Python

```bash
# Crear entorno virtual
python -m venv env

# Activar (Windows)
env\Scripts\activate

# Activar (Linux/Mac)
source env/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `chromadb==1.5.8` - Base de datos vectorial
- `ollama` - Cliente para los modelos locales
- `streamlit` - Framework para la interfaz
- `PyPDF2` - Lectura de PDFs

### Paso 4: Agregar Documentos

Coloca los archivos PDF en la carpeta `data/`:
```
data/
  ├── spring_boot_guide.pdf
  ├── spring_web_docs.pdf
  └── spring_security.pdf
```

---

## 🚀 Cómo Funciona

### **Fase 1: Indexación (Una sola vez)**

Se ejecuta `index_simple.py` para procesar todos los PDFs:

#### 1️⃣ **Lectura de PDFs**
```python
for filename in os.listdir("./data"):
    if filename.endswith(".pdf"):
        reader = PdfReader(path)
        full_text = page.extract_text()  # Extrae texto
```
- Lee cada PDF de la carpeta `data/`
- Extrae todo el texto de las páginas

#### 2️⃣ **Chunking (Fragmentación)**
```python
chunks = []
for i in range(0, len(text), chunk_size - overlap):
    chunks.append(text[i:i + chunk_size])  # Fragmentos de 1000 caracteres
```
- Divide el texto en **fragmentos pequeños** (1000 caracteres)
- Usa **overlap** (solapamiento) de 200 caracteres para no perder contexto
- Esto permite búsquedas más precisas

**Ejemplo:**
```
Documento: "La anotación @RestController combina @Controller 
            y @ResponseBody. Sirve para crear APIs REST..."

Fragmento 1: "La anotación @RestController combina @Controller 
              y @ResponseBody. Sirve para crear APIs REST..."

Fragmento 2: "APIs REST. Es la forma estándar de crear servicios
              web en Spring Boot..."
```

#### 3️⃣ **Generación de Embeddings**
```python
ollama_ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434/api/embeddings"
)
```
- Cada fragmento se convierte en un **vector** (lista de números)
- El modelo `nomic-embed-text` transforma texto en vectores de 768 dimensiones
- Textos similares tendrán vectores similares

**Ejemplo:**
```
Texto: "Spring Boot es un framework para Java"
Vector: [0.234, -0.156, 0.892, 0.445, ..., 0.123]  # 768 números

Texto: "Spring Framework es una plataforma para Java"  
Vector: [0.241, -0.162, 0.889, 0.451, ..., 0.119]  # Similar al anterior
```

#### 4️⃣ **Almacenamiento en ChromaDB**
```python
collection.add(
    documents=batch_chunks,
    metadatas=batch_metas,
    ids=ids
)
```
- Almacena cada fragmento con su:
  - **Texto** original
  - **Vector** (embedding)
  - **Metadata** (archivo de origen)
- Indexa todo para búsquedas rápidas

---

### **Fase 2: Respuesta a Preguntas (Streamlit)**

Se ejecuta `app.py` para responder preguntas interactivamente:

#### 1️⃣ **El Usuario Hace una Pregunta**
```
Usuario: "¿Cómo uso @RestController en Spring Boot?"
```

#### 2️⃣ **Embedding de la Pregunta**
```python
query_vector = ollama.embed("¿Cómo uso @RestController en Spring Boot?")
# Vector: [0.230, -0.160, 0.895, 0.440, ..., 0.120]
```
- La pregunta se convierte al mismo vector que los documentos
- Se usa el mismo modelo `nomic-embed-text`

#### 3️⃣ **Búsqueda Vectorial (Retrieval)**
```python
results = collection.query(
    query_texts=["¿Cómo uso @RestController?"],
    n_results=3  # Top 3 fragmentos más similares
)
```

**¿Cómo calcula la similitud?**
- Usa **similitud del coseno** entre vectores
- Fragmentos con vectores cercanos al de la pregunta suben a arriba
- Extrae los Top 3 fragmentos más relevantes

**Resultado:**
```
Fragmento 1 (similitud: 0.92):
"@RestController es una anotación que combina @Controller 
 y @ResponseBody. Sirve para crear APIs REST..."

Fragmento 2 (similitud: 0.88):
"Las APIs REST en Spring Boot usan @RestController 
 para mapear rutas HTTP..."

Fragmento 3 (similitud: 0.85):
"@PostMapping y @GetMapping se usan con @RestController 
 para definir endpoints..."
```

#### 4️⃣ **Construcción del Prompt**
```python
prompt = f"""Eres un asistente experto en Spring Boot. 
Responde basándote ÚNICAMENTE en el siguiente contexto.

Contexto:
{fragmento_1}

{fragmento_2}

{fragmento_3}

Pregunta: ¿Cómo uso @RestController en Spring Boot?

Respuesta:"""
```
- Combina la pregunta con los fragmentos relevantes
- Instruye al LLM a usar solo esa información
- Evita "alucinaciones" (respuestas inventadas)

#### 5️⃣ **Generación de Respuesta (Generation)**
```python
response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": prompt}]
)
```
- El modelo `llama3.2:3b` lee el contexto
- Genera una respuesta coherente basada SOLO en ese contexto
- Si no hay info suficiente, responde honestamente

**Respuesta:**
```
"@RestController es una anotación que combina @Controller 
 y @ResponseBody, facilitando la creación de APIs REST. 
 
 Ejemplo:

 @RestController
 @RequestMapping("/api")
 public class UserController {
     @GetMapping("/{id}")
     public User getUser(@PathVariable Long id) {
         return userService.findById(id);
     }
 }

 Cuando devuelves objetos, se serializan automáticamente a JSON."
```

#### 6️⃣ **Mostrar Respuesta en Streamlit**
- La respuesta aparece en el chat interactivo
- El usuario puede ver las fuentes consultadas
- Se mantiene el historial de la conversación

---

## 📝 ¿Cómo Funciona Streamlit?

### **Características Principales:**

#### 1. **@st.cache_resource** - Caché Global
```python
@st.cache_resource
def load_chroma_collection():
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection(name=COLLECTION_NAME)
    return collection
```
- Carga la BD vectorial **una sola vez**
- Si se re-ejecuta el script, reutiliza el objeto en caché
- Evita recargar ChromaDB en cada interacción

#### 2. **st.session_state** - Estado del Chat
```python
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.messages.append({"role": "user", "content": prompt})
```
- Mantiene el historial de mensajes
- Persiste mientras el usuario esté en la misma sesión
- Se reinicia cuando el usuario recarga la página

#### 3. **st.chat_input()** - Entrada del Usuario
```python
if prompt := st.chat_input("¿Qué quieres saber sobre Spring Boot?"):
    # Procesar pregunta
```
- Input específico para chats
- El símbolo `:=` es **walrus operator** (asignación con evaluación)
- Solo ejecuta el bloque si el usuario escribió algo

#### 4. **st.chat_message()** - Mostrar Mensajes
```python
with st.chat_message("user"):
    st.markdown(prompt)

with st.chat_message("assistant"):
    st.markdown(respuesta)
```
- Renderiza burbujas de chat como una conversación real
- "user" muestra alineado a la derecha
- "assistant" muestra alineado a la izquierda

#### 5. **st.spinner()** - Indicador de Carga
```python
with st.spinner("Buscando en la documentación..."):
    context_docs, metadatas = retrieve_context(prompt, collection)
```
- Muestra un spinner mientras se ejecuta el código
- Mejora la UX: el usuario sabe que algo está pasando

#### 6. **st.expander()** - Secciones Colapsables
```python
with st.expander("📄 Fuentes consultadas"):
    for i, doc in enumerate(context_docs):
        st.write(f"**Fuente {i+1}:** {metadatas[i]['source']}")
```
- Las fuentes están ocultas por defecto
- El usuario puede expandirlas si las quiere ver

---

## 🎯 Uso

### **Paso 1: Iniciar Ollama**
Abre una terminal y corre:
```bash
ollama serve
```
(Dejala corriendo en segundo plano)

### **Paso 2: Indexar los Documentos**
En otra terminal:
```bash
cd spring-rag-app
env\Scripts\activate  # Windows
python index_simple.py
```

**Output esperado:**
```
1. Leyendo PDFs...
2. Generados 152 fragmentos.
3. Conectando a ChromaDB...
4. Insertando fragmentos (esto puede tardar)...
¡Indexación completada!
```

### **Paso 3: Iniciar la Aplicación**
```bash
streamlit run app.py
```

Se abrirá automáticamente: `http://localhost:8501`

### **Paso 4: Hacer Preguntas**
En la interfaz web:
1. Escribe una pregunta sobre Spring Boot
2. Presiona Enter
3. Espera mientras busca y genera la respuesta
4. Lee la respuesta y expande "Fuentes consultadas" si quieres ver de dónde vino

---

## 🔄 Flujo Completo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE INDEXACIÓN                          │
└─────────────────────────────────────────────────────────────────┘

1. PDFs en carpeta /data
   │
   ├─> PyPDF2.PdfReader.extract_text()
   │   └─> Extrae texto completo de cada PDF
   │
   ├─> chunk_text(text, chunk_size=1000, overlap=200)
   │   └─> Divide en fragmentos pequeños
   │
   ├─> OllamaEmbeddingFunction (nomic-embed-text)
   │   └─> Convierte cada fragmento a vector (768D)
   │
   └─> ChromaDB.collection.add()
       └─> Almacena en BD vectorial con metadata
           └─> chroma_db/ (base de datos persistente)


┌─────────────────────────────────────────────────────────────────┐
│                FLUJO DE RESPUESTA A PREGUNTAS                    │
└─────────────────────────────────────────────────────────────────┘

1. Usuario escribe en Streamlit
   │
   ├─> Pregunta: "¿Cómo uso @RestController?"
   │
   ├─> OllamaEmbeddingFunction (mismo modelo)
   │   └─> Convierte pregunta a vector
   │
   ├─> ChromaDB.collection.query()
   │   ├─> Calcula similitud coseno
   │   ├─> Ordena por similitud descendente
   │   └─> Retorna Top 3 fragmentos + metadata
   │
   ├─> Construcción de Prompt
   │   ├─> "Eres experto en Spring Boot..."
   │   ├─> Inserta los 3 fragmentos
   │   └─> Añade la pregunta del usuario
   │
   ├─> Ollama.chat(model="llama3.2:3b")
   │   └─> Genera respuesta basada en contexto
   │
   └─> Streamlit.chat_message()
       └─> Muestra respuesta en la UI
           └─> Usuario ve respuesta + fuentes
```

---

## 🔍 Ejemplo Completo

### **Entrada:**
```
Usuario: "¿Cuál es la diferencia entre @Service y @Component?"
```

### **Fase 1: Embedding**
```
Pregunta convertida a vector:
[0.125, 0.456, -0.234, 0.892, ..., 0.567]  # 768 dimensiones
```

### **Fase 2: Búsqueda**
ChromaDB busca fragmentos similares:
```
Resultado 1 (similitud: 0.91):
"@Service es una especialización de @Component. 
 Se usa para la lógica de negocio. 
 @Component es la anotación genérica para beans..."

Resultado 2 (similitud: 0.87):
"Las anotaciones estéreo (@Service, @Repository, @Controller) 
 heredan de @Component pero tienen significados semánticos..."

Resultado 3 (similitud: 0.84):
"@Service permite inyectar la lógica entre capas. 
 Es una buena práctica separar @Repository, @Service y @Controller..."
```

### **Fase 3: Generación**
```
Prompt enviado a llama3.2:3b:
───────────────────────────────
"Eres un asistente experto en Spring Boot.
Responde ÚNICAMENTE basándote en el contexto.

Contexto:
[Resultado 1]
[Resultado 2]
[Resultado 3]

Pregunta: ¿Cuál es la diferencia entre @Service y @Component?"
───────────────────────────────
```

### **Salida:**
```
@Service es una especialización de @Component diseñada 
específicamente para la capa de lógica de negocio. 
Ambas son estereotipos, pero @Service tiene un propósito 
semántico claro:

- @Component: Anotación genérica para cualquier bean
- @Service: Específica para servicios de negocio

Ventajas de usar @Service:
1. Mayor claridad en la arquitectura
2. Facilita búsqueda y mantenimiento
3. Herramientas IDE ofrecen soporte específico

Ejemplo:
@Service
public class UserService {
    private UserRepository userRepository;
    
    public User findUser(Long id) {
        return userRepository.findById(id);
    }
}

Fuentes consultadas:
- spring_boot_guide.pdf
- spring_core_concepts.pdf
```

---

## ⚙️ Configuración Avanzada

### Cambiar la cantidad de fragmentos recuperados:
En `app.py`, línea con `retrieve_context()`:
```python
# Por defecto: 3 fragmentos
context_docs, metadatas = retrieve_context(prompt, collection, n_results=5)  # Cambiar a 5
```

### Cambiar el tamaño de fragmentos:
En `index_simple.py`:
```python
chunk_size = 1500  # Más grande = menos fragmentos, menos precisión
overlap = 300      # Más overlap = más contexto entre fragmentos
```

### Cambiar los modelos de Ollama:
```python
# En index_simple.py y app.py
EMBEDDING_MODEL = "all-minilm"  # Alternativa más ligera
LLM_MODEL = "mistral:latest"    # Alternativa más potente
```

---

## 🐛 Solución de Problemas

### **"Connection refused" al conectar con Ollama**
- ✅ Asegúrate que `ollama serve` está corriendo en otra terminal
- ✅ Verifica que `http://localhost:11434` es accesible

### **"Collection not found" en app.py**
- ✅ Primero debes indexar: `python index_simple.py`
- ✅ Asegúrate que `index_simple.py` finalizó sin errores

### **Respuestas lentas**
- ✅ ChromaDB carga en la primera consulta (caché después)
- ✅ Usa menos fragmentos en `n_results=3`
- ✅ Modelos más pequeños: `mistral:7b` → `llama3.2:3b`

### **Memoria llena**
- ✅ Los modelos de Ollama pesan: nomic-embed-text (~40MB), llama3.2:3b (~2GB)
- ✅ ChromaDB es ligero (~100MB para miles de documentos)

---

## 📚 Recursos

- **ChromaDB**: https://docs.trychroma.com/
- **Ollama**: https://github.com/ollama/ollama
- **Streamlit**: https://docs.streamlit.io/
- **RAG Concept**: https://www.promptingguide.ai/techniques/rag

---

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente.

---

**Creado con ❤️ para apasionados de Spring Boot y IA local**
