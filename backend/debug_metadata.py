#!/usr/bin/env python3
"""
Debug script to check metadata in the vector database.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from vector_db.vector_database import LegalVectorDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_metadata():
    """Debug metadata in the vector database."""
    
    try:
        # Initialize vector database
        vector_db = LegalVectorDatabase()
        
        # Search for any documents to see what metadata is available
        print("🔍 Searching for documents in vector database...")
        results = vector_db.search_legal_documents("wisconsin", top_k=5)
        
        if not results:
            print("❌ No documents found in the database")
            return
        
        print(f"✅ Found {len(results)} documents")
        print("\n" + "="*50)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Document {i}:")
            print(f"   Score: {result.score:.3f}")
            print(f"   Content preview: {result.metadata.get('content', '')[:100]}...")
            print(f"   Metadata keys: {list(result.metadata.keys())}")
            
            # Check for file name related fields
            file_name_fields = ['file_name', 'original_file_name', 'document_name', 'title', 'module_title']
            for field in file_name_fields:
                value = result.metadata.get(field, 'NOT_FOUND')
                print(f"   {field}: {value}")
            
            # Check for section related fields
            section_fields = ['section_title', 'section_type', 'section_number']
            for field in section_fields:
                value = result.metadata.get(field, 'NOT_FOUND')
                print(f"   {field}: {value}")
            
            print("-" * 30)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_metadata()
