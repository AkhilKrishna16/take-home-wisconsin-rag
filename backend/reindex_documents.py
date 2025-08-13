#!/usr/bin/env python3
"""
Script to reindex existing documents with proper file names and metadata.
"""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from vector_db.vector_database import LegalVectorDatabase
from document_processing.document_processor import DocumentProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reindex_documents():
    """Reindex existing documents with proper file names and metadata."""
    
    try:
        print("🔄 Starting document reindexing process...")
        
        # Initialize components
        vector_db = LegalVectorDatabase()
        document_processor = DocumentProcessor(output_dir="processed_documents", use_vector_db=True)
        
        # Get list of processed documents
        processed_dir = Path("processed_documents")
        if not processed_dir.exists():
            print("❌ No processed documents directory found")
            return
        
        processed_files = list(processed_dir.glob("*.json"))
        if not processed_files:
            print("❌ No processed document files found")
            return
        
        print(f"📁 Found {len(processed_files)} processed document files")
        
        # Reindex each document
        for i, json_file in enumerate(processed_files, 1):
            print(f"\n📄 Processing {i}/{len(processed_files)}: {json_file.name}")
            
            try:
                # Load processed document data
                with open(json_file, 'r') as f:
                    processed_data = json.load(f)
                
                # Get original file path
                original_file_path = processed_data.get('file_path')
                if not original_file_path or not Path(original_file_path).exists():
                    print(f"   ⚠️ Original file not found: {original_file_path}")
                    continue
                
                print(f"   📂 Original file: {Path(original_file_path).name}")
                
                # Reprocess document with new metadata
                chunks = processed_data.get('chunks', [])
                if chunks:
                    # Add file name to each chunk's metadata
                    for chunk in chunks:
                        if 'metadata' not in chunk:
                            chunk['metadata'] = {}
                        chunk['metadata']['file_name'] = Path(original_file_path).name
                        chunk['metadata']['original_file_name'] = Path(original_file_path).name
                    
                    # Reindex in vector database
                    document_id = processed_data.get('vector_db_id', f"reindexed_{json_file.stem}")
                    success = vector_db.index_document_chunks(chunks, document_id)
                    
                    if success:
                        print(f"   ✅ Successfully reindexed with file name: {Path(original_file_path).name}")
                    else:
                        print(f"   ❌ Failed to reindex document")
                else:
                    print(f"   ⚠️ No chunks found in processed data")
            
            except Exception as e:
                print(f"   ❌ Error processing {json_file.name}: {e}")
        
        print(f"\n✅ Reindexing complete! Processed {len(processed_files)} documents.")
        print("🔄 New documents uploaded will now have proper file names.")
    
    except Exception as e:
        print(f"❌ Error during reindexing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reindex_documents()
