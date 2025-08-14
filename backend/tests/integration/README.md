# Integration Tests

Integration tests for API endpoints and system components working together.

## 📋 Test Files

### `test_flask_app.py`
Comprehensive Flask API endpoint testing:
- Health check endpoints
- Chat API functionality
- Document management endpoints
- Chat saving and loading
- Error handling and validation
- Response formatting

**Endpoints Tested:**
- `GET /health` - System health check
- `POST /api/chat` - Chat message processing
- `GET /api/documents` - Document listing
- `POST /api/chat/save` - Chat session saving
- `GET /api/chat/list-saved` - Saved chat listing
- `DELETE /api/chat/delete/{filename}` - Chat deletion

### `test_advanced_rag.py`
Advanced RAG system integration testing:
- Query enhancement functionality
- Hybrid search implementation
- Context window management
- Citation chain following
- Relevance scoring evaluation
- Interactive testing mode

**Features Tested:**
- ✅ Query expansion and enhancement
- ✅ Semantic + keyword search combination
- ✅ Legal terminology processing
- ✅ Citation extraction and linking
- ✅ Context management for legal completeness

## 🏃 Running Integration Tests

```bash
# Run all integration tests
cd backend

# Flask API tests
python3 tests/integration/test_flask_app.py

# Advanced RAG tests
python3 tests/integration/test_advanced_rag.py

# RAG tests with specific modes
python3 tests/integration/test_advanced_rag.py enhancement
python3 tests/integration/test_advanced_rag.py search
python3 tests/integration/test_advanced_rag.py context
python3 tests/integration/test_advanced_rag.py interactive
```

## 📊 Expected Results

### Flask API Tests
- **Expected**: 15 tests with some warnings due to dependencies
- **Runtime**: ~10-15 seconds
- **Dependencies**: Flask app, vector database (optional)

### Advanced RAG Tests
- **Expected**: Successful query processing and enhancement
- **Runtime**: ~30-60 seconds (with database)
- **Dependencies**: Pinecone, embedding models, LangChain

## 🔧 Test Configuration

### Required Environment Variables
```bash
PINECONE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
PINECONE_INDEX_NAME=legal-documents
```

### Dependencies
- **Full functionality**: Requires vector database and LLM access
- **Limited testing**: Some tests can run with mocked responses
- **Network access**: Required for embedding models and API calls

## ⚠️ Common Issues

### Database Connection
```
Error: Pinecone client not available
Solution: Check API key and network connection
```

### Model Loading
```
Error: Model not found
Solution: Models download automatically on first use
```

### API Rate Limits
```
Error: OpenAI API rate limit
Solution: Wait and retry, or use different API key tier
```

## 📈 Test Outputs

### Flask Tests
- Console output with pass/fail status
- Error messages for debugging
- Response time measurements

### RAG Tests
- Query enhancement examples
- Search result quality metrics
- Interactive demo mode for manual testing
