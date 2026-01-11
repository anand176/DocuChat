# 📁 File Explanation & Complete Data Flow

## 📋 Overview

This document explains each file's purpose and the complete flow from populating data to getting LLM output.

---

## 📁 File Structure & Purpose

### 🚀 **Core Application Files**

#### 1. **`app.py`** - FastAPI Web Server
**Purpose:** Main application entry point and HTTP server

**Key Responsibilities:**
- Creates FastAPI web application
- Sets up HTTP endpoints (GET `/`, POST `/chat`, GET `/health`)
- Initializes Pinecone on startup
- Handles user requests from the frontend
- Routes requests to the LLM chain
- Returns responses to the user

**Key Functions:**
- `startup_event()` - Initializes Pinecone when app starts
- `home()` - Serves the HTML chat interface
- `chat_endpoint()` - Receives user messages, processes them, returns AI responses

---

#### 2. **`populate_data.py`** - Data Population Script
**Purpose:** One-time script to load cricket knowledge into Pinecone

**Key Responsibilities:**
- Loads sample cricket data
- Splits data into chunks
- Converts text to embeddings
- Stores vectors in Pinecone

**Flow:**
1. Calls `init_pinecone()` to connect to Pinecone
2. Gets sample cricket data from `data_loader.py`
3. Splits data into chunks
4. Calls `add_texts()` to store in Pinecone

---

### 📦 **Source Code Files (`src/`)**

#### 3. **`src/data_loader.py`** - Data Loading & Processing
**Purpose:** Handles loading and chunking cricket data

**Key Functions:**
- `get_sample_cricket_data()` - Returns sample cricket knowledge text
- `split_text_into_chunks()` - Splits long text into smaller chunks (1000 chars with 200 overlap)
- `load_cricket_data_from_text()` - Processes text into chunked documents
- `load_cricket_data_from_file()` - Loads data from a file

**Why chunking?**
- Pinecone works better with smaller, focused text chunks
- Overlap (200 chars) ensures context isn't lost at chunk boundaries
- Each chunk becomes a searchable vector

---

#### 4. **`src/vector_store.py`** - Pinecone Vector Database Management
**Purpose:** Manages Pinecone connection, embeddings, and vector operations

**Key Functions:**
- `init_pinecone()` - Connects to Pinecone, creates index if needed (384 dimensions)
- `get_embeddings_model()` - Loads SentenceTransformer model (`all-MiniLM-L6-v2`)
- `add_texts()` - Converts text to embeddings and stores in Pinecone
- `query_vectors()` - Searches Pinecone for similar vectors

**Key Components:**
- **Embedding Model:** `all-MiniLM-L6-v2` (converts text → 384-dim vectors)
- **Pinecone Index:** Stores vectors for similarity search
- **Functions:** Add vectors, query similar vectors

---

#### 5. **`src/llm_chain.py`** - LLM Integration & RAG Pipeline
**Purpose:** Handles Gemini LLM, RAG (Retrieval-Augmented Generation), and response generation

**Key Functions:**
- `get_gemini_model()` - Initializes Google Gemini model
- `generate_response()` - Main RAG function:
  1. Queries Pinecone for relevant context
  2. Formats prompt with context + history + question
  3. Calls Gemini to generate answer
  4. Returns answer + sources
- `format_chat_history()` - Formats conversation history for prompt
- `get_conversational_chain()` - Compatibility wrapper (maintains API consistency)

**The RAG Process:**
1. **Retrieval:** Get relevant documents from Pinecone
2. **Augmentation:** Add context to the prompt
3. **Generation:** Gemini generates answer using context

---

#### 6. **`src/helper.py`** - Utility Functions
**Purpose:** Helper utilities (currently not actively used, but available)

**Functions:**
- `format_chat_history()` - Format history for LangChain (legacy)
- `extract_sources()` - Extract source metadata
- `validate_environment()` - Check required environment variables

**Note:** Some functions here may be legacy from LangChain implementation.

---

#### 7. **`src/prompt.py`** - Prompt Templates
**Purpose:** Stores prompt templates (currently not used, prompt is in `llm_chain.py`)

**Note:** This file exists but the actual prompt is hardcoded in `llm_chain.py`. Could be refactored to use templates from here.

---

### 🎨 **Frontend Files**

#### 8. **`templates/index.html`** - Chat Interface
**Purpose:** HTML UI for the chatbot

**Features:**
- Chat interface with message bubbles
- JavaScript to send/receive messages
- Real-time chat updates
- Loading indicators

#### 9. **`static/style.css`** - Styling
**Purpose:** CSS styling for the chat interface

**Features:**
- Modern gradient design
- Responsive layout
- Smooth animations

---

### ⚙️ **Configuration Files**

#### 10. **`requirements.txt`** - Python Dependencies
**Purpose:** Lists all Python packages needed

**Key packages:**
- `fastapi` - Web framework
- `google-generativeai` - Gemini LLM
- `pinecone-client` - Pinecone SDK
- `sentence-transformers` - Embeddings
- `uvicorn` - ASGI server

#### 11. **`env_template.txt`** - Environment Variables Template
**Purpose:** Template for `.env` file with API keys

**Required variables:**
- `PINECONE_API_KEY` - Pinecone API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `PINECONE_INDEX_NAME` - Index name (default: cricket-chatbot)

---

## 🔄 Complete Data Flow: From Population to LLM Output

### Phase 1: Initial Setup & Data Population

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Populate Data (One-time setup)                      │
└─────────────────────────────────────────────────────────────┘

1. User runs: python populate_data.py
   │
   ├─→ populate_data.py calls init_pinecone()
   │   │
   │   ├─→ vector_store.py: init_pinecone()
   │   │   ├─→ Connects to Pinecone using API key
   │   │   ├─→ Checks if index "cricket-chatbot" exists
   │   │   └─→ Creates index (384 dims) if doesn't exist
   │   │
   │   └─→ Returns Pinecone index object
   │
   ├─→ populate_data.py calls get_sample_cricket_data()
   │   │
   │   └─→ data_loader.py: get_sample_cricket_data()
   │       └─→ Returns cricket knowledge text
   │
   ├─→ populate_data.py calls load_cricket_data_from_text()
   │   │
   │   └─→ data_loader.py: load_cricket_data_from_text()
   │       ├─→ Calls split_text_into_chunks()
   │       │   └─→ Splits text into chunks (1000 chars, 200 overlap)
   │       │
   │       └─→ Returns list of dicts: [{"text": "...", "metadata": {...}}, ...]
   │
   └─→ populate_data.py calls add_texts()
       │
       └─→ vector_store.py: add_texts()
           ├─→ Gets embeddings model (SentenceTransformer)
           ├─→ Converts each text chunk to embedding (384-dim vector)
           ├─→ Prepares vectors with IDs and metadata
           └─→ Upserts to Pinecone (stores in cloud)

Result: Cricket knowledge stored as vectors in Pinecone ✅
```

---

### Phase 2: Application Startup

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Start Application                                    │
└─────────────────────────────────────────────────────────────┘

1. User runs: python app.py
   │
   └─→ app.py: startup_event()
       │
       └─→ vector_store.py: init_pinecone()
           ├─→ Connects to Pinecone
           └─→ Gets existing index (already created)
       
Result: FastAPI server running, Pinecone connected ✅
```

---

### Phase 3: User Sends Question (Live Query Flow)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: User Question → LLM Response                         │
└─────────────────────────────────────────────────────────────┘

1. User types question in browser: "What are cricket formats?"
   │
   ├─→ Browser sends POST /chat to FastAPI
   │   │
   │   └─→ app.py: chat_endpoint()
   │       │
   │       ├─→ Validates Pinecone initialized
   │       │
   │       ├─→ Converts history: [[h1, a1], [h2, a2]] → [(h1, a1), (h2, a2)]
   │       │
   │       └─→ Calls get_conversational_chain(chat_history)
   │           │
   │           └─→ llm_chain.py: get_conversational_chain()
   │               └─→ Returns ChainWrapper object
   │
   ├─→ app.py calls chain.invoke({"question": "What are cricket formats?"})
   │   │
   │   └─→ llm_chain.py: ChainWrapper.invoke()
   │       │
   │       └─→ llm_chain.py: generate_response()
   │           │
   │           ├─→ Step A: RETRIEVAL
   │           │   └─→ vector_store.py: query_vectors()
   │           │       ├─→ Gets embeddings model
   │           │       ├─→ Converts question to embedding: "What are..." → [0.23, -0.45, ...] (384 numbers)
   │           │       ├─→ Queries Pinecone: index.query(vector=embedding, top_k=3)
   │           │       └─→ Returns top 3 similar documents:
   │           │           [
   │           │             {"text": "Cricket has three formats...", "metadata": {...}, "score": 0.89},
   │           │             {"text": "Test cricket is played...", "metadata": {...}, "score": 0.85},
   │           │             {"text": "ODI format uses...", "metadata": {...}, "score": 0.82}
   │           │           ]
   │           │
   │           ├─→ Step B: CONTEXT PREPARATION
   │           │   ├─→ Extracts text from documents: context_text = "Cricket has three formats...\n\nTest cricket..."
   │           │   ├─→ Extracts sources: sources = ["cricket_knowledge_base"]
   │           │   └─→ Formats chat history: history_text = "Human: ...\nAssistant: ..."
   │           │
   │           ├─→ Step C: PROMPT CONSTRUCTION
   │           │   └─→ Builds prompt string:
   │           │       """
   │           │       You are a helpful cricket knowledge assistant...
   │           │       
   │           │       Context:
   │           │       Cricket has three formats: Test (5 days), ODI (50 overs), T20 (20 overs)...
   │           │       
   │           │       Chat History:
   │           │       None
   │           │       
   │           │       Human: What are cricket formats?
   │           │       Assistant:
   │           │       """
   │           │
   │           ├─→ Step D: GENERATION (LLM Call)
   │           │   └─→ google.generativeai: model.generate_content(prompt)
   │           │       ├─→ Sends prompt to Gemini API
   │           │       ├─→ Gemini processes prompt with context
   │           │       └─→ Returns: "Cricket has three main formats: 1. Test cricket..."
   │           │
   │           └─→ Returns: {"answer": "...", "sources": ["cricket_knowledge_base"]}
   │
   └─→ app.py formats response
       │
       └─→ Returns JSON to browser:
           {
             "response": "Cricket has three main formats: 1. Test cricket...",
             "sources": ["cricket_knowledge_base"]
           }
       
Result: User sees answer in chat interface ✅
```

---

## 🔍 Detailed Step-by-Step Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

SETUP PHASE (One-time):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
populate_data.py
    │
    ├─→ init_pinecone() ────────────────────────────┐
    │   (vector_store.py)                           │
    │   Creates Pinecone index (384 dims)           │
    │                                                │
    ├─→ get_sample_cricket_data() ──────────────────┤
    │   (data_loader.py)                            │
    │   Returns cricket text                        │
    │                                                │
    ├─→ load_cricket_data_from_text() ──────────────┤
    │   (data_loader.py)                            │
    │   Splits into chunks                          │
    │                                                │
    └─→ add_texts() ────────────────────────────────┤
        (vector_store.py)                           │
        │                                            │
        ├─→ SentenceTransformer.encode()            │
        │   Text → 384-dim vectors                  │
        │                                            │
        └─→ Pinecone.upsert() ──────────────────────┘
            Stores vectors in cloud


QUERY PHASE (Per request):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User Browser
    │
    └─→ POST /chat {"message": "What are formats?", "history": []}
        │
        └─→ app.py: chat_endpoint()
            │
            └─→ llm_chain.py: generate_response()
                │
                ├─→ RETRIEVAL ───────────────────────────────────┐
                │   vector_store.py: query_vectors()             │
                │   │                                            │
                │   ├─→ SentenceTransformer.encode()            │
                │   │   "What are formats?" → [0.23, -0.45, ...]│
                │   │                                            │
                │   └─→ Pinecone.index.query()                  │
                │       Returns top 3 similar documents          │
                │                                                │
                ├─→ AUGMENTATION ────────────────────────────────┤
                │   Build prompt with:                           │
                │   - Retrieved context                          │
                │   - Chat history                               │
                │   - User question                              │
                │                                                │
                └─→ GENERATION ──────────────────────────────────┤
                    google.generativeai: generate_content()      │
                    │                                            │
                    └─→ Gemini API ──────────────────────────────┘
                        Returns answer
                            │
                            └─→ app.py: JSON response
                                │
                                └─→ Browser: Display answer
```

---

## 📊 Key Data Transformations

### 1. **Text → Chunks**
```
Long cricket text (2000 chars)
    ↓
split_text_into_chunks()
    ↓
["Chunk 1 (chars 0-1000)", "Chunk 2 (chars 800-1800)", ...]
```

### 2. **Chunks → Embeddings**
```
Text chunk: "Cricket has three formats..."
    ↓
SentenceTransformer.encode()
    ↓
Vector: [0.23, -0.45, 0.67, ..., 0.12] (384 numbers)
```

### 3. **Embeddings → Pinecone Storage**
```
Vector + Metadata
    ↓
Pinecone.upsert()
    ↓
Stored in cloud index
```

### 4. **Query → Similar Vectors**
```
User question: "What are formats?"
    ↓
Embedding: [0.25, -0.43, 0.69, ...]
    ↓
Pinecone.query() (cosine similarity)
    ↓
Top 3 matching documents
```

### 5. **Context + Question → LLM Response**
```
Retrieved context + Question + History
    ↓
Prompt construction
    ↓
Gemini API
    ↓
Generated answer
```

---

## 🎯 File Dependencies Graph

```
app.py
  ├─→ src/vector_store.py (init_pinecone, get_vector_store)
  └─→ src/llm_chain.py (get_conversational_chain)

populate_data.py
  ├─→ src/vector_store.py (init_pinecone, add_texts)
  └─→ src/data_loader.py (get_sample_cricket_data, load_cricket_data_from_text)

src/llm_chain.py
  └─→ src/vector_store.py (query_vectors)

src/vector_store.py
  └─→ (External) SentenceTransformer, Pinecone

src/data_loader.py
  └─→ (Standalone utility functions)
```

---

## 🔑 Key Concepts

### **RAG (Retrieval-Augmented Generation)**
1. **Retrieval:** Search Pinecone for relevant context
2. **Augmentation:** Add context to prompt
3. **Generation:** LLM generates answer using context

### **Vector Embeddings**
- Text → Numbers (384 dimensions)
- Similar text = Similar vectors
- Enables semantic search

### **Chunking**
- Splits long text into smaller pieces
- Overlap ensures context continuity
- Each chunk = one searchable vector

---

This completes the full flow from data population to LLM output! 🎉
