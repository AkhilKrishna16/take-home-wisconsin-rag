#!/usr/bin/env python3
"""
Add Source Documents to Chatbot Responses

This script demonstrates how to manually add source documents information
to chatbot responses when the automatic integration isn't working.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))
from langchain_rag_chatbot import LangChainLegalRAGChatbot

def extract_source_documents_manual(rag_response):
    """Manually extract source documents from RAG response."""
    
    source_documents = []
    
    for i, result in enumerate(rag_response['search_results'][:5], 1):  # Top 5 results
        doc_info = {
            'source_number': i,
            'relevance_score': result.score,
            'document_type': getattr(result, 'document_type', 'Unknown'),
            'jurisdiction': getattr(result, 'jurisdiction', 'Unknown'),
            'law_status': getattr(result, 'law_status', 'Unknown'),
            'content_preview': result.content[:200] + "..." if len(result.content) > 200 else result.content,
            'citations': getattr(result, 'citation_chain', []),
            'dates': getattr(result, 'dates', []),
            'file_name': getattr(result, 'file_name', 'Unknown'),
            'section': getattr(result, 'section', 'Unknown')
        }
        source_documents.append(doc_info)
    
    return source_documents

def display_source_documents(source_documents):
    """Display source documents in a formatted way."""
    
    print("📄 **Source Documents Used:**")
    print("=" * 50)
    
    for doc in source_documents[:3]:
        print(f"📋 Source {doc['source_number']} (Score: {doc['relevance_score']:.3f}):")
        print(f"   Type: {doc['document_type']}")
        print(f"   Jurisdiction: {doc['jurisdiction']}")
        print(f"   Status: {doc['law_status']}")
        
        if doc['file_name'] != 'Unknown':
            print(f"   File: {doc['file_name']}")
        
        if doc['section'] != 'Unknown':
            print(f"   Section: {doc['section']}")
        
        if doc['citations']:
            print(f"   Citations: {', '.join(doc['citations'][:3])}")
        
        print(f"   Preview: {doc['content_preview']}")
        print("-" * 30)

def test_with_source_documents():
    """Test the chatbot with manual source document extraction."""
    
    print("🧪 Testing Chatbot with Source Documents")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=600,
            temperature=0.3,
            streaming=False
        )
        
        # Test question
        question = "What does 18 U.S.C. 2703 say about digital evidence?"
        
        print(f"❓ Question: {question}")
        print("\n🔍 Getting response...")
        
        # Get response
        response = chatbot.ask(question, include_metadata=True)
        
        # Display main answer
        print("\n🤖 **Answer:**")
        print(response['answer'])
        print("\n" + "=" * 50)
        
        # Manually extract and display source documents
        if 'metadata' in response:
            # Access the RAG system directly to get source documents
            rag_response = chatbot.rag_system.ask_question(question, max_results=5)
            source_documents = extract_source_documents_manual(rag_response)
            
            display_source_documents(source_documents)
            
            # Display other metadata
            metadata = response['metadata']
            print("\n📊 **Search Quality:**")
            print(f"   Top Score: {metadata['search_quality']['top_score']:.3f}")
            print(f"   Results Found: {metadata['search_quality']['total_results']}")
            
            if metadata['citations_found']:
                print("\n⚖️ **Legal Authorities Found:**")
                for citation in metadata['citations_found'][:5]:
                    print(f"   - {citation}")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def streaming_with_source_documents():
    """Test streaming with source documents."""
    
    print("📡 Streaming with Source Documents")
    print("=" * 50)
    
    try:
        # Initialize streaming chatbot
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.3,
            streaming=True
        )
        
        question = "What are the Fourth Amendment protections for digital privacy?"
        
        print(f"❓ Question: {question}")
        print("\n🤖 Streaming Response:")
        print("-" * 40)
        
        # Stream the response
        full_response = None
        for chunk in chatbot.ask_streaming(question, include_metadata=True):
            if chunk['type'] == 'content':
                print(chunk['content'], end='', flush=True)
            elif chunk['type'] == 'complete':
                full_response = chunk['response']
                break
            elif chunk['type'] == 'error':
                print(f"\n❌ Error: {chunk['response']['answer']}")
                return
        
        if full_response:
            print("\n\n" + "=" * 50)
            
            # Manually extract and display source documents
            rag_response = chatbot.rag_system.ask_question(question, max_results=5)
            source_documents = extract_source_documents_manual(rag_response)
            
            display_source_documents(source_documents)
            
            # Display confidence
            if 'confidence_score' in full_response:
                confidence = full_response['confidence_score']
                print(f"\n🎯 **Confidence:** {confidence:.1%}")
        
        print("\n✅ Streaming test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            test_with_source_documents()
        elif mode == "streaming":
            streaming_with_source_documents()
        else:
            print("❌ Unknown mode. Use: 'test' or 'streaming'")
    else:
        # Run both tests
        print("Running both tests...\n")
        
        test_with_source_documents()
        print("\n" + "="*60 + "\n")
        
        streaming_with_source_documents()

if __name__ == "__main__":
    main()
