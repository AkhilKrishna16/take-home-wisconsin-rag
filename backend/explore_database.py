#!/usr/bin/env python3
"""
Explore Vector Database Contents

This script shows you what's actually stored in your Pinecone vector database,
including all documents, chunks, metadata, and search capabilities.
"""

import os
import json
from typing import Dict, List, Any
from vector_database import LegalVectorDatabase
from document_processor import DocumentProcessor

def print_separator(title: str):
    """Print a nice separator with title."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def explore_database():
    """Explore the vector database contents."""
    
    print("🗄️  Vector Database Explorer")
    print("=" * 60)
    
    # Initialize vector database
    try:
        vdb = LegalVectorDatabase()
        print("✅ Connected to Pinecone vector database")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Get database statistics
    print_separator("DATABASE STATISTICS")
    stats = vdb.get_index_stats()
    print(f"📊 Total vectors: {stats.get('total_vector_count', 0)}")
    print(f"🔢 Index dimension: {stats.get('dimension', 'N/A')}")
    print(f"📈 Index fullness: {stats.get('index_fullness', 'N/A')}")
    print(f"📁 Namespaces: {list(stats.get('namespaces', {}).keys())}")
    
    # Get all vectors (we'll fetch them in batches)
    print_separator("ALL STORED VECTORS")
    
    try:
        # Fetch all vectors from the index
        # Note: This is a simplified approach - in production you'd use proper pagination
        all_vectors = vdb.index.query(
            vector=[0.0] * 384,  # Dummy vector to get all results
            top_k=1000,  # Get up to 1000 vectors
            include_metadata=True
        )
        
        if not all_vectors.matches:
            print("📭 No vectors found in the database")
            return
        
        print(f"📚 Found {len(all_vectors.matches)} vectors in the database")
        
        # Group by document
        documents = {}
        for match in all_vectors.matches:
            doc_id = match.metadata.get('document_id', 'unknown')
            if doc_id not in documents:
                documents[doc_id] = []
            documents[doc_id].append(match)
        
        # Display each document
        for doc_id, chunks in documents.items():
            print(f"\n📄 Document: {doc_id}")
            print(f"   📊 Chunks: {len(chunks)}")
            
            # Show first chunk details
            if chunks:
                first_chunk = chunks[0]
                metadata = first_chunk.metadata
                print(f"   📝 Document type: {metadata.get('chunk_type', 'unknown')}")
                print(f"   📅 Processed: {metadata.get('processed_at', 'unknown')}")
                
                # Show legal metadata
                legal_metadata = []
                if metadata.get('statute_numbers'):
                    legal_metadata.append(f"Statutes: {metadata['statute_numbers']}")
                if metadata.get('case_citations'):
                    legal_metadata.append(f"Cases: {metadata['case_citations']}")
                if metadata.get('dates'):
                    legal_metadata.append(f"Dates: {metadata['dates']}")
                
                if legal_metadata:
                    print(f"   ⚖️  Legal references: {'; '.join(legal_metadata)}")
                
                # Show content preview
                content = metadata.get('content', '')[:200]
                print(f"   📖 Content preview: {content}...")
        
        # Show detailed chunk information
        print_separator("DETAILED CHUNK ANALYSIS")
        
        for i, match in enumerate(all_vectors.matches[:5]):  # Show first 5 chunks
            print(f"\n🔍 Chunk {i+1}:")
            metadata = match.metadata
            
            print(f"   🆔 ID: {match.id}")
            print(f"   📊 Score: {match.score:.4f}")
            print(f"   📄 Document: {metadata.get('document_id', 'unknown')}")
            print(f"   🏷️  Type: {metadata.get('chunk_type', 'unknown')}")
            print(f"   📍 Position: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
            
            # Show section information
            if metadata.get('section_type'):
                print(f"   📋 Section: {metadata.get('section_type')}")
            if metadata.get('section_number'):
                print(f"   🔢 Section #: {metadata.get('section_number')}")
            if metadata.get('section_title'):
                print(f"   📝 Section Title: {metadata.get('section_title')}")
            
            # Show legal references
            legal_refs = []
            if metadata.get('statute_numbers'):
                legal_refs.extend(metadata['statute_numbers'])
            if metadata.get('case_citations'):
                legal_refs.extend(metadata['case_citations'])
            if metadata.get('policy_numbers'):
                legal_refs.extend(metadata['policy_numbers'])
            
            if legal_refs:
                print(f"   ⚖️  Legal References: {', '.join(legal_refs)}")
            
            # Show content
            content = metadata.get('content', '')
            print(f"   📖 Content: {content[:150]}...")
        
        # Test search capabilities
        print_separator("SEARCH CAPABILITIES DEMO")
        
        # Test different search types
        search_tests = [
            ("General search", "Fourth Amendment", None),
            ("Statute search", "18 U.S.C. 2703", None),
            ("Case search", "Smith v. Maryland", None),
            ("Document type search", "digital evidence", {"chunk_type": "policy_section"}),
        ]
        
        for test_name, query, filter_metadata in search_tests:
            print(f"\n🔍 {test_name}: '{query}'")
            try:
                results = vdb.search_legal_documents(query, top_k=3, filter_metadata=filter_metadata)
                print(f"   📊 Found {len(results)} results")
                
                for j, result in enumerate(results[:2]):  # Show top 2 results
                    content_preview = result.metadata.get('content', '')[:100]
                    print(f"   {j+1}. Score: {result.score:.3f} | {content_preview}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Show metadata schema
        print_separator("METADATA SCHEMA")
        if all_vectors.matches:
            sample_metadata = all_vectors.matches[0].metadata
            print("📋 Available metadata fields:")
            for key, value in sample_metadata.items():
                value_type = type(value).__name__
                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"   🔑 {key} ({value_type}): {value_preview}")
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")

def test_search_functionality():
    """Test various search functionalities."""
    
    print_separator("ADVANCED SEARCH TESTING")
    
    try:
        processor = DocumentProcessor(use_vector_db=True)
        
        # Test different search scenarios
        search_scenarios = [
            {
                "name": "Fourth Amendment Protection",
                "query": "Fourth Amendment protection against unreasonable searches",
                "description": "Finding constitutional protections"
            },
            {
                "name": "Digital Evidence Statute",
                "query": "18 U.S.C. 2703",
                "description": "Finding specific statute references"
            },
            {
                "name": "Case Law Search",
                "query": "Smith v. Maryland",
                "description": "Finding case citations"
            },
            {
                "name": "Policy Documents",
                "query": "digital evidence collection procedures",
                "description": "Finding policy information"
            }
        ]
        
        for scenario in search_scenarios:
            print(f"\n🔍 {scenario['name']}")
            print(f"   📝 Query: {scenario['query']}")
            print(f"   📋 Description: {scenario['description']}")
            
            try:
                results = processor.search_documents(scenario['query'], top_k=3)
                print(f"   📊 Results: {len(results)} found")
                
                for i, result in enumerate(results):
                    doc_type = result.metadata.get('chunk_type', 'unknown')
                    content = result.metadata.get('content', '')[:80]
                    print(f"   {i+1}. [{doc_type}] Score: {result.score:.3f} | {content}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error testing search: {e}")

if __name__ == "__main__":
    # Explore the database contents
    explore_database()
    
    # Test search functionality
    test_search_functionality()
    
    print(f"\n{'='*60}")
    print("🎉 Database exploration complete!")
    print("💡 You can now see exactly what's stored in your vector database")
    print("🔍 Try running different searches to explore the capabilities")
    print(f"{'='*60}")
