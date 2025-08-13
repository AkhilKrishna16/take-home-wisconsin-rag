# Wisconsin Statutes RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Wisconsin legal documents, built with Flask, LangChain, Pinecone, and React.

## Features

- **Streaming Chat**: Real-time, character-by-character responses with slower typing animation
- **Document Upload**: Drag-and-drop interface for uploading personal documents (PDF, DOCX, TXT, MD, HTML)
- **Semantic Search**: Advanced RAG system with Pinecone vector database
- **Source Citations**: Dynamic display of relevant source documents for each query
- **Background Processing**: Documents are processed and indexed in the background
- **Health Monitoring**: Real-time connection status and component health checks

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- Pinecone API key

### Backend Setup

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend:**
   ```bash
   python start_backend.py
   ```

The server will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

### Chat Interface

1. **Ask Questions**: Type legal questions in the chat interface
2. **View Sources**: Relevant source documents appear on the right side
3. **Real-time Responses**: Watch responses stream in character by character

### Document Upload

1. **Click "Upload Documents"** in the header
2. **Drag and Drop** files or click to browse
3. **Supported Formats**: PDF, DOCX, DOC, TXT, MD, HTML
4. **Background Processing**: Documents are automatically chunked and indexed
5. **Document Count**: See how many documents are in your knowledge base

### Example Queries

- "What is the 4th amendment?"
- "Explain Wisconsin's open records law"
- "What are the requirements for a search warrant?"
- "How does the state handle juvenile cases?"

## API Endpoints

### Chat
- `POST /api/chat/stream` - Streaming chat endpoint
- `POST /api/chat/sources` - Get source documents for a query

### Documents
- `POST /api/documents/upload` - Upload and process documents
- `GET /api/documents/list` - List all documents
- `DELETE /api/documents/<id>` - Delete a document
- `POST /api/documents/search` - Search documents

### System
- `GET /health` - Health check
- `GET /api/tasks/<id>` - Get task status
- `GET /api/tasks` - List all tasks

## Architecture

### Backend Components

- **Flask Server**: REST API with streaming support
- **LangChain RAG**: Advanced retrieval and generation
- **Pinecone Vector DB**: Semantic document storage
- **Document Processor**: Multi-format document processing
- **Background Tasks**: Asynchronous document processing

### Frontend Components

- **React + TypeScript**: Modern UI framework
- **Streaming Chat**: Real-time response display
- **Document Upload**: Drag-and-drop interface
- **Source Display**: Dynamic source document cards
- **Health Monitoring**: Connection status indicators

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Optional
PINECONE_INDEX_NAME=legal-documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
LOG_LEVEL=INFO
```

### File Upload Settings

- **Max File Size**: 50MB
- **Supported Formats**: PDF, DOCX, DOC, TXT, MD, HTML
- **Processing**: Automatic chunking and vectorization
- **Storage**: Temporary files cleaned up after processing

## Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Adding New Document Types

1. Update `ALLOWED_EXTENSIONS` in `flask_server/app.py`
2. Add processor in `document_processing/document_processor.py`
3. Update frontend file input accept attribute

### Customizing RAG System

- Modify prompts in `chatbot/langchain_rag_chatbot.py`
- Adjust chunking parameters in `document_processing/document_chunker.py`
- Configure vector database settings in `vector_db/vector_database.py`

## Troubleshooting

### Common Issues

1. **Port 5000 in use**: The backend now uses port 5001 to avoid conflicts with macOS AirPlay
2. **Missing API keys**: Ensure all required environment variables are set
3. **Upload failures**: Check file size and format restrictions
4. **Processing errors**: Monitor backend logs for detailed error messages

### Logs

- **Backend logs**: `backend/backend.log`
- **Frontend logs**: Browser developer console
- **Task status**: Available via `/api/tasks` endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is for educational and informational purposes only. It does not provide legal advice. Always consult with qualified legal counsel for specific legal matters.
