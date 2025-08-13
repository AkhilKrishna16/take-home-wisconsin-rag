#!/usr/bin/env python3
"""
Interactive Legal Document Q&A

Ask questions about your legal documents and get relevant answers from the vector database.
"""

import os
import sys
from typing import List, Dict, Any
from vector_database import LegalVectorDatabase
from document_processor import DocumentProcessor
import nltk

nltk.download('stopwords')

def print_separator():
    """Print a nice separator."""
    print("\n" + "="*60)

def format_answer(results: List[Any], query: str) -> str:
    """Format search results into a readable answer."""
    if not results:
        return "❌ No relevant information found in the database."
    
    answer_parts = []
    answer_parts.append(f"🔍 **Query**: {query}")
    answer_parts.append(f"📊 **Found {len(results)} relevant results:**\n")
    
    for i, result in enumerate(results, 1):
        metadata = result.metadata
        content = metadata.get('content', '')
        score = result.score
        doc_type = metadata.get('chunk_type', 'unknown')
        doc_id = metadata.get('document_id', 'unknown')
        
        # Format the answer
        answer_parts.append(f"**{i}. {doc_type.upper()}** (Relevance: {score:.3f})")
        answer_parts.append(f"📄 Source: {doc_id}")
        
        # Add legal references if available
        legal_refs = []
        if metadata.get('statute_numbers'):
            legal_refs.extend(metadata['statute_numbers'])
        if metadata.get('case_citations'):
            legal_refs.extend(metadata['case_citations'])
        
        if legal_refs:
            answer_parts.append(f"⚖️ Legal References: {', '.join(legal_refs)}")
        
        answer_parts.append(f"📖 **Content:**\n{content}\n")
    
    return "\n".join(answer_parts)

def interactive_qa():
    """Interactive Q&A session."""
    
    print("🤖 Legal Document Q&A System")
    print("=" * 60)
    print("Ask questions about your legal documents!")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'help' for example questions.")
    print_separator()
    
    try:
        # Initialize the system
        print("🔧 Initializing...")
        processor = DocumentProcessor(use_vector_db=True)
        print("✅ Ready! You can now ask questions.\n")
        
        # Example questions
        example_questions = [
            "What does 18 U.S.C. 2703 say about digital evidence?",
            "What are the Fourth Amendment protections for digital privacy?",
            "What are the requirements for digital evidence collection?",
            "What training is available for digital forensics?",
            "What does Smith v. Maryland say about privacy?",
            "What are the policy procedures for evidence preservation?"
        ]
        
        while True:
            try:
                # Get user input
                query = input("\n❓ Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye! Thanks for using the Legal Q&A system.")
                    break
                
                if query.lower() == 'help':
                    print("\n💡 **Example Questions:**")
                    for i, example in enumerate(example_questions, 1):
                        print(f"   {i}. {example}")
                    print("\n💡 **Special Commands:**")
                    print("   - 'help': Show example questions")
                    print("   - 'quit' or 'exit': End session")
                    print("   - 'stats': Show database statistics")
                    continue
                
                if query.lower() == 'stats':
                    stats = processor.get_vector_db_stats()
                    print(f"\n📊 **Database Statistics:**")
                    print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
                    print(f"   Index dimension: {stats.get('dimension', 'N/A')}")
                    print(f"   Index fullness: {stats.get('index_fullness', 'N/A')}")
                    continue
                
                if not query:
                    print("❌ Please enter a question.")
                    continue
                
                # Search for answers
                print(f"\n🔍 Searching for: '{query}'")
                results = processor.search_documents(query, top_k=5)
                
                # Format and display the answer
                answer = format_answer(results, query)
                print_separator()
                print(answer)
                print_separator()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Legal Q&A system.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different question.")
    
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("Make sure your .env file is set up correctly.")

def quick_question(question: str):
    """Ask a single question and get an answer."""
    
    print(f"🤖 Legal Q&A - Quick Question")
    print("=" * 60)
    print(f"❓ Question: {question}")
    print_separator()
    
    try:
        processor = DocumentProcessor(use_vector_db=True)
        results = processor.search_documents(question, top_k=3)
        answer = format_answer(results, question)
        print(answer)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a question is provided as command line argument
        question = " ".join(sys.argv[1:])
        quick_question(question)
    else:
        # Interactive mode
        interactive_qa()
