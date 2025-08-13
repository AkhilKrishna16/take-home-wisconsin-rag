# Flask Legal RAG Chatbot API

A comprehensive Flask API server for the Legal RAG Chatbot system, providing endpoints for chatbot querying, document upload and processing, and vector database management.

## 🚀 Features

### 🤖 Chatbot Functionality
- **Regular Chat**: Send questions and get comprehensive legal answers
- **Streaming Chat**: Real-time streaming responses with word-by-word display
- **Chat History**: View and manage conversation history
- **Safety Features**: Confidence scoring, legal disclaimers, jurisdiction warnings

### 📄 Document Management
- **Document Upload**: Upload legal documents (PDF, DOCX, TXT, HTML, MD)
- **Background Processing**: Automatic chunking, vectorization, OCR, and Pinecone storage
- **Task Tracking**: Monitor processing progress with real-time status updates
- **Document Search**: Semantic search across uploaded documents
- **Document Management**: List, search, and delete documents

### 🔍 Advanced Search
- **Semantic Search**: Find relevant legal content using AI-powered search
- **Metadata Filtering**: Filter by jurisdiction, document type, law status
- **Relevance Scoring**: Get relevance scores for search results

## 📋 API Endpoints

### Health & Status
- `GET /health` - Health check and component status

### Chatbot
- `POST /api/chat` - Send a question to the chatbot
- `POST /api/chat/stream` - Streaming chat response
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### Documents
- `POST /api/documents/upload` - Upload document (background processing)
- `POST /api/documents/search` - Search documents
- `GET /api/documents/list` - List all documents
- `DELETE /api/documents/<id>` - Delete a document

### Task Management
- `GET /api/tasks/<id>` - Get task status and progress
- `GET /api/tasks` - List all background tasks
- `DELETE /api/tasks/<id>` - Delete task from tracking

### System
- `GET /api/stats` - Get system statistics

## 🛠️ Installation

### 1. Install Dependencies
```bash
cd backend/flask_server
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the `backend` directory:
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=legal-rag-index

# Optional: Flask settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Start the Server
```bash
python app.py
```

The server will start on `http://localhost:5000`

## 📖 Usage Examples

### 1. Health Check
```bash
curl http://localhost:5000/health
```

### 2. Chat with Chatbot
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does 18 U.S.C. 2703 say about digital evidence?",
    "jurisdiction": "federal",
    "include_metadata": true
  }'
```

### 3. Streaming Chat
```bash
curl -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the Fourth Amendment protections?",
    "jurisdiction": "federal"
  }'
```

### 4. Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@legal_document.pdf" \
  -F "document_type=Federal Statute" \
  -F "jurisdiction=federal" \
  -F "law_status=current" \
  -F "uploaded_by=user123"
```

### 5. Search Documents
```bash
curl -X POST http://localhost:5000/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "digital evidence collection",
    "max_results": 10,
    "jurisdiction": "federal"
  }'
```

## 🧪 Testing

### Run Test Client
```bash
python test_client.py
```

This will test all API endpoints and demonstrate their usage.

### Manual Testing with curl

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Chat Test
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is digital evidence?"}'
```

#### Document Upload Test
```bash
# Create a test file
echo "This is a test legal document about digital evidence." > test.txt

# Upload it
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@test.txt" \
  -F "document_type=Test Document" \
  -F "jurisdiction=federal"
```

## 🔧 Configuration

### File Upload Settings
- **Max File Size**: 50MB
- **Allowed Extensions**: txt, pdf, docx, doc, html, md
- **Upload Folder**: `uploads/` (auto-created)

### Chatbot Settings
- **Model**: GPT-3.5-turbo (cost-effective)
- **Max Tokens**: 800
- **Temperature**: 0.3 (focused responses)
- **Streaming**: Available for real-time responses

### Vector Database
- **Provider**: Pinecone
- **Embedding Model**: OpenAI text-embedding-ada-002
- **Chunk Size**: Optimized for legal documents

## 📊 Response Format

### Success Response
```json
{
  "data": {
    // Response data here
  },
  "message": "Success message",
  "timestamp": "2024-01-01T12:00:00",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00",
  "status": "error"
}
```

### Chat Response
```json
{
  "data": {
    "question": "What is digital evidence?",
    "answer": "Digital evidence is...",
    "confidence_score": 0.85,
    "safety_warnings": {
      "legal_disclaimer": true
    },
    "metadata": {
      "search_quality": {
        "top_score": 0.892,
        "total_results": 5
      },
      "source_documents": [
        {
          "source_number": 1,
          "relevance_score": 0.892,
          "document_type": "Federal Statute",
          "jurisdiction": "federal"
        }
      ]
    }
  }
}
```

## 🔒 Security Features

- **File Validation**: Secure filename handling
- **Size Limits**: 50MB file upload limit
- **CORS**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and logging

## 🚨 Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- File size limits
- Missing required fields
- Database connection issues
- OpenAI API errors
- Vector database errors

## 📈 Monitoring

### Health Check
Monitor system health and component status:
```bash
curl http://localhost:5000/health
```

### System Statistics
Get detailed system statistics:
```bash
curl http://localhost:5000/api/stats
```

## 🔄 Development

### Adding New Endpoints
1. Add route decorator in `app.py`
2. Implement the endpoint function
3. Add error handling
4. Update this README
5. Add tests to `test_client.py`

### Logging
The server uses Python's logging module with INFO level by default. Check the console output for detailed logs.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Pinecone Connection**: Check API keys and environment settings
3. **OpenAI Errors**: Verify API key and quota
4. **File Upload Issues**: Check file size and type restrictions

### Debug Mode
Run with debug mode for detailed error messages:
```bash
FLASK_DEBUG=True python app.py
```

## 📝 License

This project is part of the Legal RAG Chatbot system.

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Test thoroughly before submitting

---

For more information, see the main project README in the root directory.
