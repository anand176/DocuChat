# 🏏 Cricket Chatbot - Architecture & Flow Explanation

## Overview

This document explains how the cricket chatbot works from end-to-end, including the architecture, data flow, and component interactions.

---

## 📐 Architecture Diagram

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/JSON
       │
┌──────▼────────────────────────────────────┐
│         FastAPI Backend (app.py)          │
│  ┌─────────────────────────────────────┐  │
│  │  GET /          → Serve HTML UI     │  │
│  │  POST /chat     → Handle Messages   │  │
│  │  GET /health    → Health Check      │  │
│  └─────────────────────────────────────┘  │
└──────┬───────────────────┬────────────────┘
       │                   │
       │                   │
┌──────▼─────────┐  ┌──────▼──────────────────┐
│  LangChain     │  │  Pinecone Vector Store  │
│  Orchestrator  │  │  (Vector Database)      │
│                │  │                         │
│  ┌──────────┐  │  │  ┌──────────────────┐  │
│  │ Conversa-│  │  │  │ Cricket Knowledge│  │
│  │ tional   │  │  │  │ Embeddings       │  │
│  │ Retrieval│◄─┼──┼──┤ (384-dim vectors)│  │
│  │ Chain    │  │  │  └──────────────────┘  │
│  └────┬─────┘  │  └─────────────────────────┘
│       │        │
│  ┌────▼──────┐ │
│  │ Gemini LLM│ │
│  │ (gemini-  │ │
│  │  pro)     │ │
│  └───────────┘ │
└────────────────┘
```

---

## 🔄 Complete Flow Breakdown

### Phase 1: Application Startup (Initialization)

```
1. Server starts (python app.py)
   ↓
2. FastAPI app initializes
   ↓
3. @app.on_event("startup") triggers
   ↓
4. init_pinecone() called:
   - Connects to Pinecone using API key
   - Checks if index "cricket-chatbot" exists
   - Creates index if needed (384 dimensions, cosine metric)
   - Initializes PineconeVectorStore with HuggingFace embeddings
   ↓
5. Application ready to accept requests
```

**Files Involved:**
- `app.py` (lines 26-37)
- `src/vector_store.py` (init_pinecone function)

---

### Phase 2: User Opens the Chat Interface

```
1. User navigates to http://localhost:8000
   ↓
2. Browser sends GET / request
   ↓
3. FastAPI serves index.html template
   ↓
4. Browser loads:
   - HTML structure (templates/index.html)
   - CSS styles (static/style.css)
   - JavaScript for chat functionality
   ↓
5. User sees the chat interface
```

**Files Involved:**
- `app.py` (line 48-51: GET / endpoint)
- `templates/index.html`
- `static/style.css`

---

### Phase 3: User Sends a Message (Main Flow)

This is the **core RAG (Retrieval-Augmented Generation)** flow:

#### Step 1: User Input → Frontend Processing

```
User types: "What are the different formats of cricket?"
   ↓
JavaScript (index.html):
- Captures form submission
- Shows loading indicator
- Prepares request with:
  {
    "message": "What are the different formats of cricket?",
    "history": [[prev_human, prev_ai], ...]  // Previous conversation
  }
   ↓
POST /chat request sent to FastAPI
```

**Files Involved:**
- `templates/index.html` (sendMessage function, lines 53-93)

---

#### Step 2: FastAPI Receives Request

```
POST /chat endpoint receives request:
   ↓
app.py chat_endpoint():
1. Validates Pinecone is initialized
2. Extracts message and history from request
3. Converts history format: [[h, a], ...] → [(h, a), ...]
4. Calls get_conversational_chain(chat_history=history_tuples)
```

**Files Involved:**
- `app.py` (lines 53-90: chat_endpoint function)

---

#### Step 3: LangChain Chain Setup

```
get_conversational_chain() in llm_chain.py:
   ↓
1. get_llm() - Creates/returns Gemini LLM instance:
   - ChatGoogleGenerativeAI(model="gemini-pro")
   - Temperature: 0.7
   - Uses GOOGLE_API_KEY
   ↓
2. get_retriever() - Creates/returns Pinecone retriever:
   - Gets vector_store instance
   - Creates retriever with k=3 (top 3 similar documents)
   - Search type: similarity
   ↓
3. Creates ConversationBufferMemory:
   - Loads chat_history into memory
   - Stores previous Q&A pairs
   ↓
4. Creates ConversationalRetrievalChain:
   - Combines LLM + Retriever + Memory
   - Uses custom QA_PROMPT template
   - Returns source documents
```

**Files Involved:**
- `src/llm_chain.py` (get_conversational_chain function, lines 43-97)

---

#### Step 4: Retrieval Phase (RAG - Retrieval)

```
chain.invoke({"question": user_message}) triggered
   ↓
ConversationalRetrievalChain internally:
   ↓
1. User question: "What are the different formats of cricket?"
   ↓
2. Embedding Generation:
   - HuggingFaceEmbeddings model converts question to vector
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - Output: 384-dimensional vector
   ↓
3. Vector Similarity Search in Pinecone:
   - Searches for top k=3 most similar vectors
   - Uses cosine similarity
   - Returns 3 document chunks with highest similarity scores
   ↓
4. Retrieved Context:
   [
     "Cricket has three main formats: Test (5 days), ODI (50 overs), T20 (20 overs)...",
     "Test cricket is the longest format played over 5 days...",
     "Twenty20 (T20) is the shortest format with 20 overs per side..."
   ]
```

**Files Involved:**
- `src/vector_store.py` (embeddings model, line 17-19)
- `src/llm_chain.py` (retriever setup, lines 32-41)
- Pinecone Cloud (vector database)

---

#### Step 5: Prompt Construction

```
LangChain constructs the final prompt:
   ↓
Template Structure:
┌─────────────────────────────────────────┐
│ You are a helpful cricket knowledge     │
│ assistant...                            │
│                                         │
│ Context:                                │
│ [Retrieved 3 document chunks combined]  │
│                                         │
│ Chat History:                           │
│ [Previous conversation if any]          │
│                                         │
│ Human: What are the different formats   │
│        of cricket?                      │
│ Assistant:                              │
└─────────────────────────────────────────┘
```

**Files Involved:**
- `src/llm_chain.py` (QA_PROMPT template, lines 54-65)

---

#### Step 6: LLM Generation (RAG - Augmented Generation)

```
Constructed prompt sent to Gemini:
   ↓
Google Gemini API (gemini-pro):
- Processes the prompt with context
- Generates answer based on:
  * Retrieved cricket knowledge (context)
  * Conversation history
  * Its training data
   ↓
Response: "Cricket has three main formats:
           1. Test cricket - played over 5 days...
           2. One Day International (ODI) - 50 overs...
           3. Twenty20 (T20) - 20 overs per side..."
```

**Files Involved:**
- `src/llm_chain.py` (Gemini LLM, lines 16-30)
- Google Gemini API (external service)

---

#### Step 7: Response Processing

```
Chain returns result:
{
  "answer": "Cricket has three main formats...",
  "source_documents": [
    Document(page_content="...", metadata={"source": "cricket_knowledge_base"}),
    Document(page_content="...", metadata={"source": "cricket_knowledge_base"}),
    Document(page_content="...", metadata={"source": "cricket_knowledge_base"})
  ],
  "chat_history": [...]
}
   ↓
app.py extracts:
- answer from result
- sources from source_documents metadata
   ↓
Returns JSON response:
{
  "response": "Cricket has three main formats...",
  "sources": ["cricket_knowledge_base"]
}
```

**Files Involved:**
- `app.py` (response processing, lines 76-90)

---

#### Step 8: Frontend Updates

```
JavaScript receives response:
   ↓
1. Hides loading indicator
2. Adds bot response to chat UI
3. Updates chatHistory array:
   chatHistory.push([user_message, bot_response])
4. Scrolls chat to bottom
5. Enables send button
6. User sees the response
```

**Files Involved:**
- `templates/index.html` (JavaScript handlers, lines 76-92)

---

## 🔑 Key Components Explained

### 1. **RAG (Retrieval-Augmented Generation)**
   - **Retrieval**: Searches Pinecone for relevant cricket knowledge
   - **Augmentation**: Adds retrieved context to the prompt
   - **Generation**: Gemini generates answer using context + its knowledge

### 2. **Vector Embeddings**
   - Text → Numbers (384-dimensional vectors)
   - Semantic similarity: Similar meanings = Similar vectors
   - Enables fast similarity search in Pinecone

### 3. **ConversationalRetrievalChain**
   - Orchestrates the entire flow
   - Manages: retrieval → context → memory → LLM → response
   - Handles conversation history automatically

### 4. **Memory (ConversationBufferMemory)**
   - Stores previous Q&A pairs
   - Allows context-aware follow-up questions
   - Example: User asks "What is Test cricket?" → AI explains → User asks "How long does it last?" → AI knows "it" refers to Test cricket

---

## 📊 Data Flow Summary

```
User Question
    ↓
[Embedding] → Vector Representation
    ↓
[Pinecone Search] → Top 3 Relevant Documents
    ↓
[Prompt Construction] → Question + Context + History
    ↓
[Gemini LLM] → Generated Answer
    ↓
[Response Processing] → Answer + Sources
    ↓
User Receives Answer
```

---

## 🗂️ File Responsibilities

| File | Responsibility |
|------|---------------|
| `app.py` | FastAPI server, HTTP endpoints, request/response handling |
| `src/llm_chain.py` | LangChain chain setup, Gemini LLM configuration, prompt templates |
| `src/vector_store.py` | Pinecone connection, embeddings, vector store management |
| `src/data_loader.py` | Cricket data processing, text splitting, document creation |
| `templates/index.html` | Frontend UI, JavaScript for chat interaction |
| `static/style.css` | Styling for the chat interface |
| `populate_data.py` | Script to load cricket data into Pinecone |

---

## 🔄 Initial Data Population Flow

When you run `python populate_data.py`:

```
1. Load sample cricket data (get_sample_cricket_data())
   ↓
2. Split into chunks (RecursiveCharacterTextSplitter)
   - Chunk size: 1000 characters
   - Overlap: 200 characters
   ↓
3. Generate embeddings for each chunk
   - HuggingFace model creates 384-dim vectors
   ↓
4. Store in Pinecone
   - Each chunk → Vector + Metadata
   - Index: "cricket-chatbot"
   ↓
5. Ready for similarity search
```

---

## 💡 Why This Architecture?

1. **Pinecone**: Fast, scalable vector search (handles millions of vectors)
2. **LangChain**: Standardizes LLM workflows, handles complexity
3. **Gemini**: Powerful LLM with good understanding
4. **RAG**: Provides accurate, context-aware answers (no hallucination)
5. **FastAPI**: Modern, fast Python web framework
6. **Separation of Concerns**: Each component has a clear responsibility

---

## 🎯 Example Flow Walkthrough

**User asks:** "Tell me about IPL"

1. **Embedding**: "Tell me about IPL" → `[0.23, -0.45, 0.67, ...]` (384 numbers)
2. **Search**: Pinecone finds 3 documents mentioning IPL, tournaments, T20
3. **Context**: Retrieved docs about IPL, T20 format, franchise tournaments
4. **Prompt**: Question + Context + History → Full prompt for Gemini
5. **LLM**: Gemini generates: "IPL (Indian Premier League) is a T20 franchise tournament..."
6. **Response**: User sees the answer with relevant context

---

This architecture ensures the chatbot provides accurate, context-aware answers by combining the power of vector search (Pinecone) with generative AI (Gemini), orchestrated by LangChain, and delivered through a modern web interface (FastAPI + HTML/CSS).
