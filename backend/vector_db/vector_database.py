#!/usr/bin/env python3
"""
Vector Database Handler for Legal Documents

This module provides Pinecone integration for storing and retrieving legal document chunks
with optimized embeddings and metadata filtering capabilities.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Pinecone imports
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Pinecone not available. Install with: pip install pinecone")

# Embeddings imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Sentence transformers not available. Install with: pip install sentence-transformers")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalVectorDatabase:
    """
    Pinecone vector database handler optimized for legal documents.
    
    Features:
    - Legal-optimized embeddings using sentence-transformers
    - Metadata filtering for legal references
    - Efficient indexing schema for legal documents
    - Batch operations for large document sets
    - Singleton pattern to prevent multiple initializations
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, index_name: str = "legal-documents"):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(LegalVectorDatabase, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, index_name: str = "legal-documents"):
        """
        Initialize the vector database.
        
        Args:
            index_name: Name of the Pinecone index
        """
        # Only initialize once
        if self._initialized:
            return
            
        self.index_name = index_name
        self.pc = None
        self.index = None
        self.embedding_model = None
        
        # Initialize Pinecone
        self._initialize_pinecone()
        
        # Initialize embedding model
        self._initialize_embeddings()
        
        # Create or connect to index
        self._setup_index()
        
        # Mark as initialized
        self._initialized = True
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client."""
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone client not available")
        
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        try:
            self.pc = Pinecone(api_key=api_key)
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def _initialize_embeddings(self):
        """Initialize the embedding model optimized for legal text."""
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError("Sentence transformers not available")
        
        try:
            # Use a model optimized for legal/semantic similarity
            # all-MiniLM-L6-v2 is good for legal text and fast
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def _setup_index(self):
        """Create or connect to Pinecone index with legal-optimized schema."""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                # Create new index with legal-optimized configuration
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Created new index: {self.index_name}")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup index: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for legal text chunks.
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise
    
    def index_document_chunks(self, chunks: List[Dict[str, Any]], document_id: str) -> bool:
        """
        Index document chunks with metadata for legal retrieval.
        
        Args:
            chunks: List of document chunks from DocumentChunker
            document_id: Unique identifier for the document
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            # Prepare vectors for indexing
            vectors = []
            
            for i, chunk in enumerate(chunks):
                # Create unique ID for this chunk
                chunk_id = f"{document_id}_chunk_{i}"
                
                # Create embedding for chunk content
                embedding = self.create_embeddings([chunk['content']])[0]
                
                # Prepare metadata for legal filtering
                metadata = {
                    'document_id': document_id,
                    'chunk_type': chunk.get('chunk_type', 'general'),
                    'content': chunk['content'][:1000],  # Truncate for metadata
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'start_line': chunk.get('start_line', 0),
                    'end_line': chunk.get('end_line', 0),
                    'processed_at': datetime.now().isoformat()
                }
                
                # Add file name from chunk metadata
                chunk_metadata = chunk.get('metadata', {})
                if 'file_name' in chunk_metadata:
                    metadata['file_name'] = chunk_metadata['file_name']
                if 'original_file_name' in chunk_metadata:
                    metadata['original_file_name'] = chunk_metadata['original_file_name']
                
                # Add section information from chunk metadata
                if 'section_number' in chunk_metadata:
                    metadata['section_number'] = chunk_metadata['section_number']
                if 'section_title' in chunk_metadata:
                    metadata['section_title'] = chunk_metadata['section_title']
                
                # Add section information from chunk's section object
                chunk_section = chunk.get('section', {})
                if isinstance(chunk_section, dict):
                    if 'number' in chunk_section:
                        metadata['section_number'] = chunk_section['number']
                    if 'title' in chunk_section:
                        metadata['section_title'] = chunk_section['title']
                
                # Add legal-specific metadata
                chunk_metadata = chunk.get('metadata', {})
                
                # Statute numbers
                if 'statute_numbers' in chunk_metadata and chunk_metadata['statute_numbers']:
                    metadata['statute_numbers'] = chunk_metadata['statute_numbers']
                
                # Case citations
                if 'case_citations' in chunk_metadata and chunk_metadata['case_citations']:
                    metadata['case_citations'] = chunk_metadata['case_citations']
                
                # Dates
                if 'dates' in chunk_metadata and chunk_metadata['dates']:
                    metadata['dates'] = chunk_metadata['dates']
                
                # Section information
                if 'section_type' in chunk_metadata:
                    metadata['section_type'] = chunk_metadata['section_type']
                
                if 'section_number' in chunk_metadata:
                    metadata['section_number'] = chunk_metadata['section_number']
                
                if 'section_title' in chunk_metadata:
                    metadata['section_title'] = chunk_metadata['section_title']
                
                # Policy numbers
                if 'policy_numbers' in chunk_metadata and chunk_metadata['policy_numbers']:
                    metadata['policy_numbers'] = chunk_metadata['policy_numbers']
                
                # Training metadata
                if 'module_title' in chunk_metadata:
                    metadata['module_title'] = chunk_metadata['module_title']
                
                if 'learning_objectives' in chunk_metadata and chunk_metadata['learning_objectives']:
                    metadata['learning_objectives'] = chunk_metadata['learning_objectives']
                
                if 'key_terms' in chunk_metadata and chunk_metadata['key_terms']:
                    metadata['key_terms'] = chunk_metadata['key_terms']
                
                vectors.append({
                    'id': chunk_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Indexed {len(vectors)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document chunks: {e}")
            return False
    
    def search_legal_documents(self, 
                             query: str, 
                             top_k: int = 10, 
                             filter_metadata: Optional[Dict[str, Any]] = None,
                             include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Search legal documents with metadata filtering.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters (e.g., {'statute_numbers': ['1.1A']})
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of search results with scores and metadata
        """
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            # Create embedding for query
            query_embedding = self.create_embeddings([query])[0]
            
            # Prepare filter
            filter_dict = None
            if filter_metadata:
                filter_dict = self._build_metadata_filter(filter_metadata)
            
            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    def _build_metadata_filter(self, filter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Pinecone metadata filter from user-specified filters.
        
        Args:
            filter_metadata: User-specified metadata filters
            
        Returns:
            Pinecone-compatible filter dictionary
        """
        filter_conditions = []
        
        for key, value in filter_metadata.items():
            if isinstance(value, list):
                # Handle list values (e.g., multiple statute numbers)
                for item in value:
                    filter_conditions.append({key: {"$eq": item}})
            else:
                # Handle single values
                filter_conditions.append({key: {"$eq": value}})
        
        if len(filter_conditions) == 1:
            return filter_conditions[0]
        elif len(filter_conditions) > 1:
            return {"$or": filter_conditions}
        else:
            return {}
    
    def search_by_statute(self, statute_number: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents containing specific statute references.
        
        Args:
            statute_number: Statute number to search for (e.g., "1.1A", "18 U.S.C. 2703")
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        return self.search_legal_documents(
            query=f"statute {statute_number}",
            top_k=top_k,
            filter_metadata={'statute_numbers': [statute_number]}
        )
    
    def search_by_case_citation(self, case_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents containing specific case citations.
        
        Args:
            case_name: Case name to search for (e.g., "Smith v. Maryland")
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        return self.search_legal_documents(
            query=f"case {case_name}",
            top_k=top_k,
            filter_metadata={'case_citations': [case_name]}
        )
    
    def search_by_document_type(self, document_type: str, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search within a specific document type.
        
        Args:
            document_type: Type of document (case_law, policy, training)
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        return self.search_legal_documents(
            query=query,
            top_k=top_k,
            filter_metadata={'chunk_type': document_type}
        )
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database index."""
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks for a specific document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            # Delete vectors with document_id in metadata
            self.index.delete(filter={'document_id': {'$eq': document_id}})
            logger.info(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the index.
        
        Returns:
            List of document metadata
        """
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            # Get all vectors with metadata
            results = self.index.query(
                vector=[0.0] * 384,  # Dummy vector for fetching all
                top_k=10000,  # Large number to get all documents
                include_metadata=True
            )
            
            # Extract unique document IDs
            documents = {}
            for match in results.matches:
                if 'document_id' in match.metadata:
                    doc_id = match.metadata['document_id']
                    if doc_id not in documents:
                        documents[doc_id] = {
                            'document_id': doc_id,
                            'document_type': match.metadata.get('chunk_type', 'unknown'),
                            'file_name': match.metadata.get('file_name', 'unknown'),
                            'chunk_count': 1
                        }
                    else:
                        documents[doc_id]['chunk_count'] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def search(self, query: str, top_k: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Alias for search_legal_documents for compatibility.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of search results
        """
        return self.search_legal_documents(query, top_k, filter_metadata)
    
    def clear_index(self) -> bool:
        """Clear all vectors from the index."""
        if not self.index:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared entire index")
            return True
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Test the vector database
    try:
        # Initialize vector database
        vdb = LegalVectorDatabase()
        
        # Get index stats
        stats = vdb.get_index_stats()
        print(f"Index stats: {stats}")
        
        # Example search
        results = vdb.search_legal_documents("Fourth Amendment digital privacy", top_k=5)
        print(f"Found {len(results)} results")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set PINECONE_API_KEY in your .env file")
