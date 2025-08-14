# Wisconsin Legal RAG Chatbot

A comprehensive legal document retrieval and question-answering system designed for Wisconsin law enforcement officers. This RAG (Retrieval-Augmented Generation) chatbot provides intelligent access to Wisconsin State Statutes, case law, department policies, and training materials.

## 🚀 Features

### Core Functionality
- **Intelligent Document Processing**: Supports PDF, DOCX, and text files with OCR capabilities
- **Advanced RAG System**: Hybrid search combining semantic and keyword matching
- **Real-time Chat Interface**: Streaming responses with source citations
- **Document Download**: Click-to-download original source documents
- **Chat History**: Intelligent LLM-based chat naming and session management
- **Mobile-Responsive Design**: Optimized for field use on mobile devices

### Legal-Specific Features
- **Jurisdiction-Aware Search**: Prioritizes Wisconsin-specific laws and policies
- **Citation Tracking**: Maintains legal citation chains and cross-references
- **Confidence Scoring**: Match scores for source relevance
- **Safety Warnings**: Flags outdated or jurisdiction-specific information
- **Quick Access Queries**: Pre-built queries for common legal scenarios

### User Experience
- **Stop Generation**: Interrupt ongoing responses
- **Auto-Save**: Intelligent chat session management
- **Export Functionality**: Export conversations as reports
- **Toast Notifications**: User-friendly error and success messages
- **Dark/Light Theme**: Modern UI with accessibility features

## 🏗️ Architecture

### Backend (Python/Flask)
- **Vector Database**: Pinecone for semantic search
- **Document Processing**: Intelligent chunking with metadata preservation
- **LLM Integration**: OpenAI GPT for response generation
- **OCR Support**: pytesseract for image-based PDF processing
- **API Endpoints**: RESTful API with streaming support

### Frontend (React/TypeScript)
- **Modern UI**: Built with Tailwind CSS and shadcn/ui
- **Real-time Updates**: Server-Sent Events for streaming
- **State Management**: React hooks for efficient state handling
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Pinecone API key
- OpenAI API key

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd take-home-wisconsin-rag
```

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r flask_server/requirements.txt

# Set environment variables
export PINECONE_API_KEY="your-pinecone-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export PINECONE_ENVIRONMENT="your-pinecone-environment"
export PINECONE_INDEX_NAME="your-index-name"
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### 1. Start the Backend Server
```bash
cd backend
source ../venv/bin/activate
python3 main.py
```
The backend will start on `http://localhost:5001`

### 2. Start the Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5173`

## 📚 Usage

### Document Upload
1. Click "Upload Documents" in the sidebar
2. Select PDF, DOCX, or text files
3. Choose document type (statutes, case law, policies, training)
4. Documents are automatically processed and indexed

### Chat Interface
1. Type your legal question in the chat input
2. Receive streaming responses with source citations
3. Click on source documents to download originals
4. Use quick query buttons for common scenarios

### Chat Management
- **Auto-Save**: Chats are automatically saved with intelligent naming
- **Load History**: Access previous conversations from the sidebar
- **Export**: Download chat reports in various formats
- **Clear Chat**: Start new conversations

### Advanced Features
- **Stop Generation**: Click the stop button to interrupt responses
- **Source Downloads**: Click download icons on source cards
- **Confidence Scores**: View match scores for source relevance
- **Mobile Optimization**: Responsive design for field use

## 🔧 Configuration

### Environment Variables
```bash
# Required
PINECONE_API_KEY=your-pinecone-api-key
OPENAI_API_KEY=your-openai-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=your-index-name

# Optional
FLASK_ENV=development
DEBUG=True
```

### Document Processing Settings
- **Chunk Size**: Configurable text chunking for optimal retrieval
- **Metadata Preservation**: Maintains legal citations and document structure
- **OCR Support**: Automatic text extraction from image-based PDFs

## 📁 Project Structure

```
take-home-wisconsin-rag/
├── backend/
│   ├── flask_server/          # Flask application
│   ├── chatbot/              # RAG chatbot implementation
│   ├── document_processing/  # Document processing pipeline
│   ├── vector_db/           # Vector database operations
│   ├── pdfs/                # Document storage
│   └── processed_documents/ # Processed document metadata
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── lib/            # API and utilities
│   │   └── pages/          # Page components
│   └── public/             # Static assets
└── venv/                   # Python virtual environment
```

## 🔍 API Endpoints

### Chat Endpoints
- `POST /api/chat/stream` - Streaming chat responses
- `POST /api/chat/save` - Save chat session
- `GET /api/chat/list-saved` - List saved chats
- `GET /api/chat/load/{filename}` - Load saved chat
- `POST /api/chat/generate-name` - Generate chat name with LLM

### Document Endpoints
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents/download/{filename}` - Download documents
- `GET /api/documents/list` - List processed documents

### Processing Endpoints
- `POST /api/process` - Process uploaded documents
- `GET /api/tasks/{task_id}` - Get processing task status
- `GET /api/tasks` - List all processing tasks

## 🧪 Testing

**Performance Metrics as deliverable -- already in `backend/`.**

### Backend Tests
```bash
cd backend
python -m pytest testing/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Setup
1. Set production environment variables
2. Configure reverse proxy (nginx)
3. Set up SSL certificates
4. Configure database backups
5. Set up monitoring and logging

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🔒 Security Features

- **Input Validation**: Sanitized user inputs
- **File Upload Security**: Restricted file types and sizes
- **Path Traversal Protection**: Secure file access
- **CORS Configuration**: Proper cross-origin settings
- **API Rate Limiting**: Request throttling

## 📊 Performance

- **Streaming Responses**: Real-time chat experience
- **Caching**: Optimized document retrieval
- **Lazy Loading**: Efficient resource management
- **Mobile Optimization**: Responsive design for field use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information

## 🔄 Changelog

### Version 1.0.0
- Initial release with core RAG functionality
- Document processing pipeline
- Real-time chat interface
- Mobile-responsive design
- LLM-based chat naming
- Document download functionality
- Auto-save and chat history
- Stop generation feature
- Export functionality
- Comprehensive error handling

---

**Built for Wisconsin Law Enforcement** 🚔

This system is designed to provide quick, accurate access to legal information in the field, helping officers make informed decisions while maintaining compliance with Wisconsin laws and department policies.
