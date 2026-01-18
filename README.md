# Docuchat 🚀

A modern document knowledge chatbot built with **React**, **FastAPI**, **Pinecone** vector database, and **Google Gemini** LLM. Upload your documents and ask questions about them using RAG (Retrieval Augmented Generation).

## ✨ Features

- 🤖 **Powered by Google Gemini** for natural language understanding
- 📊 **Pinecone vector database** for efficient similarity search
- ⚛️ **React frontend** with modern UI/UX
- 🚀 **FastAPI backend** with RESTful API
- 🐳 **Docker-based** deployment with Docker Compose
- 💬 **Conversational memory** for context-aware responses
- 📄 **Multi-format support**: PDF, DOCX, TXT files
- 🔍 **Semantic search** over your document knowledge base

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  React Frontend │────────▶│  FastAPI Backend│
│   (Port 3000)   │  REST   │   (Port 8000)   │
└─────────────────┘   API   └─────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ Pinecone │    │  Gemini  │    │ Sentence │
              │  Vector  │    │   LLM    │    │Transformers│
              │   Store  │    │          │    │ Embeddings │
              └──────────┘    └──────────┘    └──────────┘
```

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **Pinecone API key** (sign up at https://www.pinecone.io/)
- **Google API key** for Gemini (get it from https://makersuite.google.com/app/apikey)

## 🚀 Quick Start with Docker

### 1. Clone and Setup

```bash
cd Docuchat
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=cricket-chatbot

# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Build and Run with Docker Compose

**Production Mode:**
```bash
docker-compose up --build
```

**Development Mode (with hot reload):**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
Docuchat/
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Production Dockerfile
│   └── src/
│       ├── vector_store.py   # Pinecone integration
│       ├── llm_chain.py      # Gemini LLM chain
│       └── data_loader.py    # Document processing
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.tsx           # Main app component
│   │   ├── App.css           # Styles
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   └── KnowledgeBase.tsx
│   │   └── services/
│   │       └── api.ts        # API client
│   ├── Dockerfile            # Production Dockerfile
│   ├── Dockerfile.dev        # Development Dockerfile
│   └── nginx.conf            # Nginx configuration
│
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose
└── .env                      # Environment variables
```

## 🎯 Usage

### Chat Interface

1. Navigate to the **Chat** tab
2. Type your questions about uploaded documents
3. Get AI-powered responses with source citations

### Knowledge Base Management

1. Switch to the **Knowledge Base** tab
2. Upload PDF, DOCX, or TXT files
3. View all uploaded documents
4. Delete documents when needed

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send chat messages and get AI responses |
| `POST` | `/add_document` | Upload a document to the knowledge base |
| `DELETE` | `/delete_document/{source}` | Delete a document by source name |
| `GET` | `/list_documents` | List all documents in the knowledge base |
| `GET` | `/health` | Health check endpoint |

## 🛠️ Development

### Running Backend Locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Running Frontend Locally (without Docker)

```bash
cd frontend
npm install
npm run dev
```

### Hot Reload in Docker

Use the development compose file for automatic code reloading:

```bash
docker-compose -f docker-compose.dev.yml up
```

## 🔧 Configuration

### Backend Environment Variables

- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment (default: `gcp-starter`)
- `PINECONE_INDEX_NAME`: Index name (default: `cricket-chatbot`)
- `GOOGLE_API_KEY`: Google Gemini API key

### Frontend Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

## 🐛 Troubleshooting

### Pinecone Issues
- Verify your `PINECONE_API_KEY` is correct
- Check your Pinecone environment/region settings
- Ensure sufficient quota on your Pinecone account

### Gemini API Issues
- Verify your `GOOGLE_API_KEY` is correct
- Check API quota availability

### Docker Issues
- Ensure Docker and Docker Compose are installed
- Check that ports 3000 and 8000 are available
- Try rebuilding: `docker-compose up --build --force-recreate`

### CORS Issues
- Backend allows origins: `http://localhost:3000` and `http://localhost:5173`
- Update `backend/app.py` if using different ports

## 📦 Building for Production

```bash
# Build production images
docker-compose build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🎨 Customization

### Change LLM Model

Edit `backend/src/llm_chain.py`:
```python
model = genai.GenerativeModel('gemini-2.5-flash')  # Change model here
```

### Adjust Retrieval Parameters

Edit `backend/src/vector_store.py`:
```python
results = index.query(
    vector=query_embedding,
    top_k=3,  # Change number of results
    include_metadata=True
)
```

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📸 Screenshots

![Chat Interface](https://github.com/user-attachments/assets/131e156c-c602-451f-a92c-f07a39f2f829)
![Knowledge Base](https://github.com/user-attachments/assets/65e33596-8c94-4e7e-948d-2a3d102e0999)
