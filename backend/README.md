# 🏗️ Legal RAG System Backend

This directory contains the backend components of the Legal RAG System, organized into logical modules for better maintainability and clarity.

## 📁 Directory Structure

```
backend/
├── chatbot/                    # 🤖 Chatbot Components
│   ├── __init__.py
│   ├── langchain_rag_chatbot.py      # LangChain RAG chatbot with safety features
│   └── interactive_langchain_chatbot.py  # Interactive chatbot interface
│
├── document_processing/        # 📄 Document Processing
│   ├── __init__.py
│   ├── document_processor.py   # Main document processing pipeline
│   └── document_chunker.py     # Text chunking and metadata extraction
│
├── rag_system/                # 🔍 RAG System
│   ├── __init__.py
│   ├── advanced_rag_system.py # Advanced RAG with hybrid search
│   └── ask_questions.py       # Question answering interface
│
├── vector_db/                 # 🗄️ Vector Database
│   ├── __init__.py
│   ├── vector_database.py     # Pinecone vector database integration
│   └── requirements_vector_db.txt  # Vector DB dependencies
│
├── testing/                   # 🧪 Testing
│   ├── __init__.py
│   ├── test_langchain_safety_features.py  # Safety features testing
│   └── test_advanced_rag.py   # RAG system testing
│
├── examples/                  # 📚 Examples
│   ├── __init__.py
│   ├── example_vector_db_usage.py  # Vector DB usage examples
│   └── explore_database.py    # Database exploration tools
│
├── docs/                      # 📖 Documentation
│   ├── __init__.py
│   └── README_VECTOR_DB.md    # Vector database documentation
│
├── processed_documents/       # 📁 Processed Documents
├── env_template.txt           # 🔧 Environment Variables Template
├── test.py                    # 🧪 Basic Test Script
└── README.md                  # 📖 This file
```

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Copy environment template
cp env_template.txt .env

# Edit with your API keys
nano .env
```

### 2. Install Dependencies

```bash
# Install vector database dependencies
pip install -r vector_db/requirements_vector_db.txt

# Install LangChain dependencies
pip install langchain langchain-openai
```

### 3. Run Examples

```bash
# Test the system
python test.py

# Run vector database example
python examples/example_vector_db_usage.py

# Test safety features
python testing/test_langchain_safety_features.py
```

## 🔧 Component Overview

### 🤖 Chatbot (`chatbot/`)

**LangChain RAG Chatbot** with comprehensive safety features:
- ✅ Confidence scoring for responses
- ✅ Outdated information flagging  
- ✅ Jurisdiction-specific warnings
- ✅ Legal disclaimers
- ✅ Use of force query handling
- ✅ Source citations in all responses

**Files:**
- `langchain_rag_chatbot.py` - Main chatbot with LangChain integration
- `interactive_langchain_chatbot.py` - Interactive command-line interface

### 📄 Document Processing (`document_processing/`)

**Advanced document processing pipeline:**
- Document classification (case law, policy, training)
- Intelligent text chunking
- Metadata extraction (statutes, cases, dates)
- Vector database indexing

**Files:**
- `document_processor.py` - Main processing pipeline
- `document_chunker.py` - Text chunking and metadata extraction

### 🔍 RAG System (`rag_system/`)

**Advanced RAG with hybrid search:**
- Hybrid search algorithms
- Relevance scoring
- Citation chain building
- Query preprocessing
- Jurisdiction filtering

**Files:**
- `advanced_rag_system.py` - Advanced RAG system
- `ask_questions.py` - Question answering interface

### 🗄️ Vector Database (`vector_db/`)

**Pinecone vector database integration:**
- Legal-optimized embeddings
- Metadata filtering
- Efficient indexing
- Semantic search

**Files:**
- `vector_database.py` - Pinecone integration
- `requirements_vector_db.txt` - Dependencies

### 🧪 Testing (`testing/`)

**Comprehensive testing suite:**
- Safety features validation
- RAG system testing
- Performance testing
- Integration testing

**Files:**
- `test_langchain_safety_features.py` - Safety features testing
- `test_advanced_rag.py` - RAG system testing

### 📚 Examples (`examples/`)

**Usage examples and tools:**
- Vector database usage examples
- Database exploration tools
- System demonstration scripts

**Files:**
- `example_vector_db_usage.py` - Vector DB examples
- `explore_database.py` - Database exploration

### 📖 Documentation (`docs/`)

**System documentation:**
- Vector database setup guide
- API documentation
- Usage guides

**Files:**
- `README_VECTOR_DB.md` - Vector database documentation

## 🔗 Key Features

### Safety & Accuracy Features ✅

All safety features from the requirements are implemented:

1. **Confidence Scoring** - Assess response confidence based on context quality
2. **Outdated Information Flagging** - Warn about potentially outdated legal information
3. **Jurisdiction-Specific Warnings** - Flag jurisdiction-specific information
4. **Legal Disclaimers** - Include appropriate legal disclaimers
5. **Use of Force Query Handling** - Special handling for use of force queries
6. **Source Citations** - Include legal authorities and citations in all responses

### Technical Features ✅

- **LangChain Integration** - Modern RAG framework with GPT-3.5-turbo
- **Pinecone Vector Database** - Scalable vector storage and retrieval
- **Advanced Search** - Hybrid semantic + keyword search
- **Metadata Filtering** - Statute, case, and jurisdiction filtering
- **Performance Optimized** - Efficient chunking and indexing

## 🎯 Usage Examples

### Basic Usage

```python
# Import chatbot
from chatbot.langchain_rag_chatbot import LangChainLegalRAGChatbot

# Initialize
chatbot = LangChainLegalRAGChatbot()

# Ask a question
response = chatbot.ask("What does 18 U.S.C. 2703 say about digital evidence?")
print(response['answer'])
```

### Document Processing

```python
# Import processor
from document_processing.document_processor import DocumentProcessor

# Initialize
processor = DocumentProcessor(use_vector_db=True)

# Process document
result = processor.process_document("legal_document.pdf")
print(f"Processed: {result['chunk_count']} chunks")
```

### RAG System

```python
# Import RAG system
from rag_system.advanced_rag_system import AdvancedLegalRAG
from vector_db.vector_database import LegalVectorDatabase

# Initialize
vector_db = LegalVectorDatabase()
rag_system = AdvancedLegalRAG(vector_db)

# Ask question
response = rag_system.ask_question("What are the Fourth Amendment protections?")
print(f"Found {response['total_results']} results")
```

## 🔧 Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=legal-documents

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Document Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Dependencies

Install required packages:

```bash
# Vector database dependencies
pip install -r vector_db/requirements_vector_db.txt

# LangChain dependencies
pip install langchain langchain-openai

# Additional dependencies
pip install python-dotenv
```

## 🧪 Testing

Run the test suite:

```bash
# Test safety features
python testing/test_langchain_safety_features.py

# Test RAG system
python testing/test_advanced_rag.py

# Basic system test
python test.py
```

## 📊 Performance

The system is optimized for:
- **Fast Retrieval** - Sub-second search response times
- **Accurate Results** - High relevance scoring
- **Scalable Storage** - Pinecone vector database
- **Cost Effective** - GPT-3.5-turbo with LangChain

## 🔗 Related Documentation

- [Vector Database Setup](docs/README_VECTOR_DB.md)
- [Safety Features Testing](testing/test_langchain_safety_features.py)
- [Usage Examples](examples/example_vector_db_usage.py)

## 🤝 Contributing

When adding new features:
1. Place files in appropriate directories
2. Update this README
3. Add tests in the `testing/` directory
4. Update documentation in `docs/`
