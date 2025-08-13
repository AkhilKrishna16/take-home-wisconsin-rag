#!/usr/bin/env python3
"""
Script to process PDF files and reindex them with improved metadata extraction.
This will ensure better section detection and content retrieval.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from document_processing.document_processor import DocumentProcessor
from vector_db.vector_database import LegalVectorDatabase
from chatbot.langchain_rag_chatbot import LangChainLegalRAGChatbot

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_files(pdfs_dir: str = "pdfs") -> None:
    """Process all PDF files in the specified directory and reindex them."""
    
    pdfs_path = Path(pdfs_dir)
    if not pdfs_path.exists():
        logger.error(f"PDFs directory {pdfs_dir} does not exist")
        return
    
    # Initialize components
    logger.info("Initializing document processor and vector database...")
    
    try:
        # Initialize document processor
        doc_processor = DocumentProcessor()
        
        # Initialize vector database
        vector_db = LegalVectorDatabase()
        
        # Initialize chatbot (this will also initialize the RAG system)
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3
        )
        
        logger.info("✅ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        return
    
    # Process each PDF file
    pdf_files = list(pdfs_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        logger.info(f"\n📄 Processing: {pdf_file.name}")
        
        try:
            # Process the document
            logger.info("  📝 Extracting content and metadata...")
            processed_doc = doc_processor.process_document(
                file_path=str(pdf_file),
                document_type="pdf"
            )
            
            if not processed_doc or not processed_doc.get('chunks'):
                logger.warning(f"  ⚠️  No content extracted from {pdf_file.name}")
                continue
            
            logger.info(f"  ✅ Extracted {len(processed_doc['chunks'])} chunks")
            
            # Add file metadata to each chunk
            for chunk in processed_doc['chunks']:
                chunk['metadata']['file_name'] = pdf_file.stem
                chunk['metadata']['original_file_name'] = pdf_file.name
                chunk['metadata']['file_path'] = str(pdf_file)
                chunk['metadata']['processed_at'] = datetime.now().isoformat()
                
                # Improve section detection
                if 'section' not in chunk['metadata'] or chunk['metadata']['section'] == 'Unknown':
                    # Try to extract section from content
                    content = chunk['content']
                    section = extract_section_from_content(content)
                    if section:
                        chunk['metadata']['section'] = section
                        chunk['metadata']['section_title'] = section
                
                # Improve jurisdiction detection
                if 'jurisdiction' not in chunk['metadata'] or chunk['metadata']['jurisdiction'] == 'Unknown':
                    chunk['metadata']['jurisdiction'] = 'state'  # Wisconsin is state jurisdiction
            
            # Index the document
            logger.info("  🔍 Indexing document in vector database...")
            document_id = f"{pdf_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            vector_db.index_document_chunks(processed_doc['chunks'], document_id)
            
            logger.info(f"  ✅ Successfully indexed {pdf_file.name}")
            
            # Save processed document for reference
            output_file = f"processed_documents/{pdf_file.stem}_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("processed_documents", exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(processed_doc, f, indent=2)
            
            logger.info(f"  💾 Saved processed document to {output_file}")
            
        except Exception as e:
            logger.error(f"  ❌ Error processing {pdf_file.name}: {e}")
            continue
    
    logger.info(f"\n🎉 Processing complete! Processed {len(pdf_files)} PDF files")
    
    # Test the indexing with a sample query
    logger.info("\n🧪 Testing the reindexed documents...")
    test_query = "how many counties are present within wisconsin?"
    
    try:
        response = chatbot.ask(test_query, jurisdiction="state", include_metadata=True)
        logger.info(f"Query: {test_query}")
        logger.info(f"Answer: {response['answer'][:200]}...")
        
        if response.get('metadata', {}).get('source_documents'):
            logger.info(f"Found {len(response['metadata']['source_documents'])} source documents")
            for i, doc in enumerate(response['metadata']['source_documents'][:3]):
                logger.info(f"  Source {i+1}: {doc.get('file_name', 'Unknown')} (Score: {doc.get('relevance_score', 0):.3f})")
                logger.info(f"    Section: {doc.get('section', 'Unknown')}")
        else:
            logger.warning("No source documents found")
            
    except Exception as e:
        logger.error(f"Error testing query: {e}")

def extract_section_from_content(content: str) -> str:
    """Extract section information from content using various patterns."""
    
    # Common section patterns
    patterns = [
        r'CHAPTER\s+(\d+[A-Z]*)',  # CHAPTER 1, CHAPTER 2A, etc.
        r'SECTION\s+(\d+\.\d+[A-Z]*)',  # SECTION 1.01, SECTION 2.05, etc.
        r'(\d+\.\d+[A-Z]*)',  # 1.01, 2.05, etc.
        r'Article\s+(\d+[A-Z]*)',  # Article 1, Article 2A, etc.
        r'Part\s+(\d+[A-Z]*)',  # Part 1, Part 2A, etc.
    ]
    
    import re
    
    for pattern in patterns:
        match = re.search(pattern, content[:500], re.IGNORECASE)  # Check first 500 chars
        if match:
            return match.group(0)
    
    # Look for numbered sections in the first few lines
    lines = content.split('\n')[:10]
    for line in lines:
        # Look for patterns like "1.01", "2.05", etc.
        match = re.search(r'^(\d+\.\d+[A-Z]*)', line.strip())
        if match:
            return match.group(1)
    
    return None

if __name__ == "__main__":
    logger.info("🚀 Starting PDF processing and reindexing...")
    process_pdf_files()
    logger.info("✅ PDF processing and reindexing complete!")
