#  DocuChat

A smart cricket knowledge chatbot built with FastAPI, Pinecone vector database, Google Gemini LLM, and LangChain. This chatbot can answer questions about cricket using RAG (Retrieval Augmented Generation) capabilities.

## Features

- 🤖 Powered by Google Gemini (gemini-pro) for natural language understanding
- 📊 Pinecone vector database for efficient similarity search
- 🔗 LangChain for orchestrating the RAG pipeline
- 🎨 Modern web UI with HTML/CSS
- 💬 Conversational memory for context-aware responses
- 🔍 Semantic search over cricket knowledge base

## Prerequisites

- **Python 3.8 - 3.12** (Python 3.13+ may have compatibility issues)
  - **Recommended: Python 3.12** for best compatibility
  - Python 3.14 is currently too new and not supported by many packages
- Pinecone API key (sign up at https://www.pinecone.io/)
- Google API key for Gemini (get it from https://makersuite.google.com/app/apikey)

### ⚠️ Python Version Warning
If you're using Python 3.13 or 3.14, you'll need to use Python 3.12 or earlier. See `PYTHON_VERSION_NOTE.md` for details.

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Cricket-Chatbot
   ```

2. **Create a virtual environment (if not already created):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file in the Cricket-Chatbot directory:**
   ```env
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=gcp-starter
   PINECONE_INDEX_NAME=cricket-chatbot

   # Google Gemini API Configuration
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Setup

1. **Populate the vector store with cricket data:**
   ```bash
   python populate_data.py
   ```
   This script will:
   - Initialize Pinecone connection
   - Create an index if it doesn't exist
   - Load sample cricket knowledge
   - Split and embed the documents
   - Store them in Pinecone

2. **Run the FastAPI application:**
   ```bash
   python app.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Open your browser and navigate to:**
   ```
   http://localhost:8000
   ```

## Project Structure

```
Cricket-Chatbot/
├── app.py                 # FastAPI main application
├── populate_data.py       # Script to populate vector store
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── templates/
│   └── index.html        # Chat UI HTML
├── static/
│   └── style.css         # Chat UI styles
└── src/
    ├── __init__.py
    ├── vector_store.py   # Pinecone vector store setup
    ├── llm_chain.py      # LangChain + Gemini chain
    ├── data_loader.py    # Data loading utilities
    ├── helper.py         # Helper functions
    └── prompt.py         # Prompt templates
```

## Usage

1. Start the application (see Setup section)
2. Open the web interface at `http://localhost:8000`
3. Type your cricket-related questions in the chat input
4. The chatbot will retrieve relevant context from the vector database and generate accurate responses

### Example Questions

- "What are the different formats of cricket?"
- "Tell me about the IPL tournament"
- "What is the highest score in Test cricket?"
- "Explain the rules of cricket"

## API Endpoints

- `GET /` - Serves the chat UI
- `POST /chat` - Chat endpoint that accepts messages and returns AI responses
- `GET /health` - Health check endpoint

## Customization

### Adding More Cricket Data

Edit `src/data_loader.py` and modify the `get_sample_cricket_data()` function to include more cricket knowledge, or load data from external files/databases.

### Changing the LLM Model

In `src/llm_chain.py`, modify the `model` parameter in `ChatGoogleGenerativeAI`:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # Change to "gemini-pro-vision" or other models
    ...
)
```

### Adjusting Retrieval Parameters

In `src/llm_chain.py`, modify the `search_kwargs` in the retriever:
```python
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Change k to retrieve more/fewer documents
)
```

## Troubleshooting

1. **Pinecone initialization errors:**
   - Verify your `PINECONE_API_KEY` is correct
   - Check your Pinecone environment/region settings
   - Ensure you have sufficient quota on your Pinecone account

2. **Gemini API errors:**
   - Verify your `GOOGLE_API_KEY` is correct
   - Check that you have enabled the Gemini API in Google Cloud Console
   - Ensure you have API quota available

3. **Import errors:**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Try upgrading pip: `pip install --upgrade pip`

4. **Empty vector store:**
   - Run `python populate_data.py` to populate the database
   - Check that the index name matches in `.env` and your Pinecone dashboard

## License

This project is open source and available for personal and educational use.
## Images


<img width="901" height="563" alt="image" src="https://github.com/user-attachments/assets/131e156c-c602-451f-a92c-f07a39f2f829" />
<img width="863" height="564" alt="image" src="https://github.com/user-attachments/assets/65e33596-8c94-4e7e-948d-2a3d102e0999" />


## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
