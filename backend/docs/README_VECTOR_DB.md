# 🗄️ Vector Database Setup for Legal Documents

This guide explains how to set up and use the Pinecone vector database system for legal document storage and retrieval.

## 📋 Overview

The vector database system provides:
- **Legal-optimized embeddings** using sentence-transformers
- **Metadata filtering** for legal references (statutes, cases, dates)
- **Efficient indexing** with hierarchical document structure
- **Semantic search** capabilities for legal documents

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements_vector_db.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
# Copy the template
cp env_template.txt .env

# Edit with your Pinecone API key
nano .env
```

Add your Pinecone API key:
```
PINECONE_API_KEY=your_actual_api_key_here
```

### 3. Get Pinecone API Key

1. Sign up at [Pinecone Console](https://app.pinecone.io/)
2. Create a new project
3. Copy your API key from the project settings

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | Required |
| `PINECONE_INDEX_NAME` | Name of the Pinecone index | `legal-documents` |
| `PINECONE_CLOUD` | Cloud provider | `aws` |
| `PINECONE_REGION` | Region for the index | `us-east-1` |
| `CHUNK_SIZE` | Maximum chunk size in characters | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |

## 📚 Usage Examples

### Basic Document Processing

```python
from document_processor import DocumentProcessor

# Initialize with vector database
processor = DocumentProcessor(use_vector_db=True)

# Process a document
result = processor.process_document("case_law_document.pdf", "case_law")

# Check if indexed
if result.get('vector_db_indexed'):
    print(f"Document indexed as: {result['vector_db_id']}")
```

### Search Operations

```python
# General search
results = processor.search_documents("Fourth Amendment digital privacy", top_k=10)

# Search by statute
statute_results = processor.search_by_statute("18 U.S.C. 2703", top_k=5)

# Search by case citation
case_results = processor.search_by_case_citation("Smith v. Maryland", top_k=5)

# Search by document type
type_results = processor.search_by_document_type("case_law", "Fourth Amendment", top_k=5)

# Search with metadata filters
filtered_results = processor.search_documents(
    "digital evidence",
    filter_metadata={'chunk_type': 'policy_section', 'statute_numbers': ['18 U.S.C. 2703']}
)
```

### Batch Processing

```python
# Process entire directory
results = processor.process_directory("legal_documents/", file_types=['.pdf', '.docx', '.txt'])

# Get statistics
stats = processor.get_vector_db_stats()
print(f"Total vectors: {stats['total_vector_count']}")
```

## 🏗️ Architecture

### Document Flow

1. **Document Input** → PDF, DOCX, TXT files
2. **Text Extraction** → Extract text content
3. **Document Classification** → Auto-detect document type
4. **Intelligent Chunking** → Create context-aware chunks
5. **Metadata Extraction** → Extract legal references
6. **Embedding Generation** → Create vector embeddings
7. **Vector Storage** → Store in Pinecone with metadata

### Index Schema

Each vector in the database contains:

```python
{
    'id': 'document_id_chunk_0',
    'values': [0.1, 0.2, ...],  # 384-dimensional embedding
    'metadata': {
        'document_id': 'case_law_123',
        'chunk_type': 'case_law_section',
        'content': 'chunk text...',
        'statute_numbers': ['18 U.S.C. 2703'],
        'case_citations': ['Smith v. Maryland, 442 U.S. 735'],
        'dates': ['2024-01-15'],
        'section_type': 'OPINION',
        'section_number': '1.1',
        'section_title': 'Purpose and Scope'
    }
}
```

## 🔍 Search Capabilities

### Semantic Search
- **Natural language queries** → Find relevant legal content
- **Context-aware matching** → Understand legal terminology
- **Multi-language support** → Handle legal text variations

### Metadata Filtering
- **Statute numbers** → Find specific legal provisions
- **Case citations** → Locate case law references
- **Document types** → Filter by case law, policy, training
- **Date ranges** → Find documents by time period
- **Section types** → Filter by opinion, dissent, etc.

### Advanced Queries

```python
# Complex metadata filtering
results = processor.search_documents(
    "digital evidence collection",
    filter_metadata={
        'chunk_type': 'policy_section',
        'statute_numbers': ['18 U.S.C. 2703'],
        'section_number': '2.1'
    }
)

# Date-based filtering
results = processor.search_documents(
    "Fourth Amendment",
    filter_metadata={
        'dates': ['2024-01-15'],
        'chunk_type': 'case_law_section'
    }
)
```

## 📊 Performance Optimization

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: Fast inference
- **Quality**: Good for legal text similarity

### Batch Operations
- **Chunk size**: 1000 characters (configurable)
- **Overlap**: 200 characters (configurable)
- **Batch size**: 100 vectors per upsert

### Index Configuration
- **Metric**: Cosine similarity
- **Cloud**: AWS
- **Region**: us-east-1
- **Type**: Serverless

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ValueError: PINECONE_API_KEY not found in environment variables
   ```
   **Solution**: Check your `.env` file and API key

2. **Index Not Found**
   ```
   pinecone.exceptions.IndexNotFoundError
   ```
   **Solution**: The index will be created automatically on first use

3. **Embedding Model Download**
   ```
   OSError: Model not found
   ```
   **Solution**: The model downloads automatically on first use

4. **Memory Issues**
   ```
   RuntimeError: CUDA out of memory
   ```
   **Solution**: Use CPU for embeddings or reduce batch size

### Performance Tips

- **Use GPU** for faster embedding generation
- **Batch processing** for large document sets
- **Optimize chunk size** based on your use case
- **Monitor index usage** in Pinecone console

## 🔐 Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Data Privacy**: Ensure compliance with data protection regulations
- **Access Control**: Use Pinecone's access control features
- **Encryption**: Data is encrypted in transit and at rest

## 📈 Monitoring

### Vector Database Stats

```python
stats = processor.get_vector_db_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Index dimension: {stats['dimension']}")
print(f"Index fullness: {stats['index_fullness']}")
```

### Pinecone Console
- Monitor usage in [Pinecone Console](https://app.pinecone.io/)
- Track query performance
- Monitor index health

## 🧪 Testing

Run the example script to test the system:

```bash
python example_vector_db_usage.py
```

This will:
1. Create sample legal documents
2. Process and index them
3. Perform various search operations
4. Display results and statistics

## 📚 API Reference

### LegalVectorDatabase Class

#### Methods
- `__init__(index_name)`: Initialize the database
- `index_document_chunks(chunks, document_id)`: Index document chunks
- `search_legal_documents(query, top_k, filter_metadata)`: General search
- `search_by_statute(statute_number, top_k)`: Search by statute
- `search_by_case_citation(case_name, top_k)`: Search by case
- `get_index_stats()`: Get database statistics
- `delete_document(document_id)`: Delete a document
- `clear_index()`: Clear all data

### DocumentProcessor Integration

The `DocumentProcessor` class now includes vector database methods:
- `search_documents()`
- `search_by_statute()`
- `search_by_case_citation()`
- `search_by_document_type()`
- `get_vector_db_stats()`

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Pinecone documentation
3. Check the example scripts
4. Monitor logs for detailed error messages
