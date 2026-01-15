# Quick Setup Guide

## Prerequisites
- Docker and Docker Compose installed
- Pinecone API key
- Google Gemini API key

## Setup Steps

### 1. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# PINECONE_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
```

### 2. Run the Application

**Option A: Production Mode**
```bash
docker-compose up --build
```

**Option B: Development Mode (with hot reload)**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Use the Application
1. Open http://localhost:3000
2. Go to "Knowledge Base" tab
3. Upload PDF, DOCX, or TXT files
4. Switch to "Chat" tab
5. Ask questions about your documents!

## Stopping the Application
```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are in use, edit `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # Change 3000 to 3001 for frontend
  - "8001:8000"  # Change 8000 to 8001 for backend
```

### Rebuild Containers
```bash
docker-compose up --build --force-recreate
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```
