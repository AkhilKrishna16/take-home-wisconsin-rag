#!/usr/bin/env python3
"""
Test Advanced RAG System

This script demonstrates the advanced features:
1. Hybrid Search Implementation
2. Context Window Management  
3. Query Enhancement
"""

import sys
import os
from advanced_rag_system import AdvancedLegalRAG, LegalQueryEnhancer
from vector_database import LegalVectorDatabase

def test_query_enhancement():
    """Test query enhancement features."""
    print("🔍 Testing Query Enhancement")
    print("=" * 50)
    
    enhancer = LegalQueryEnhancer()
    
    test_queries = [
        "What does 18 U.S.C. 2703 say about digital evidence?",
        "4th Am. protections for privacy",
        "LEO requirements for evidence collection",
        "SCOTUS cases about digital privacy",
        "What are the DOJ policies on evidence preservation?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Original Query: {query}")
        enhancement = enhancer.expand_query(query)
        
        print(f"🔧 Enhanced Query: {enhancement.enhanced_query}")
        
        if enhancement.abbreviations:
            print(f"📚 Abbreviations Found: {enhancement.abbreviations}")
        
        if enhancement.corrected_terms:
            print(f"✅ Corrections: {enhancement.corrected_terms}")
        
        if enhancement.expanded_terms:
            print(f"📖 Expanded Terms: {enhancement.expanded_terms[:3]}...")

def test_hybrid_search():
    """Test hybrid search functionality."""
    print("\n\n🔍 Testing Hybrid Search")
    print("=" * 50)
    
    try:
        vector_db = LegalVectorDatabase()
        rag_system = AdvancedLegalRAG(vector_db)
        
        test_questions = [
            "What does 18 U.S.C. 2703 say about digital evidence?",
            "What are the Fourth Amendment protections for digital privacy?",
            "What does Smith v. Maryland say about privacy?",
            "What are the requirements for digital evidence collection?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            print("-" * 40)
            
            response = rag_system.ask_question(question, jurisdiction="federal", max_results=3)
            
            print(f"📊 Top Score: {response['top_score']:.3f}")
            print(f"📚 Total Results: {response['total_results']}")
            print(f"⚖️ Jurisdiction: {response['jurisdiction']}")
            
            if response['search_results']:
                top_result = response['search_results'][0]
                print(f"\n🏆 Top Result:")
                print(f"   📄 Type: {top_result.document_type}")
                print(f"   📍 Jurisdiction: {top_result.jurisdiction}")
                print(f"   📋 Law Status: {top_result.law_status}")
                print(f"   📖 Content: {top_result.content[:150]}...")
                
                if top_result.citation_chain:
                    print(f"   ⚖️ Citations: {', '.join(top_result.citation_chain[:2])}")
                
                print(f"\n📈 Relevance Factors:")
                for factor, score in top_result.relevance_factors.items():
                    print(f"   {factor}: {score:.3f}")
            
            if response['citation_chain']:
                print(f"\n🔗 Citation Chain: {', '.join(response['citation_chain'][:3])}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_context_management():
    """Test context window management."""
    print("\n\n📚 Testing Context Window Management")
    print("=" * 50)
    
    try:
        vector_db = LegalVectorDatabase()
        rag_system = AdvancedLegalRAG(vector_db)
        
        # Test with a complex question that should trigger context management
        question = "What are the legal requirements for digital evidence collection under 18 U.S.C. 2703 and related Fourth Amendment protections?"
        
        print(f"❓ Complex Question: {question}")
        print("-" * 40)
        
        response = rag_system.ask_question(question, jurisdiction="federal", max_results=5)
        
        print(f"📊 Context Window Length: {len(response['context_window'])} characters")
        print(f"📚 Results Used: {response['total_results']}")
        
        # Show context window preview
        context_preview = response['context_window'][:500] + "..." if len(response['context_window']) > 500 else response['context_window']
        print(f"\n📖 Context Window Preview:\n{context_preview}")
        
        # Show citation chain
        if response['citation_chain']:
            print(f"\n🔗 Citation Chain Found: {', '.join(response['citation_chain'])}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_test():
    """Interactive testing mode."""
    print("\n\n🤖 Interactive Advanced RAG Testing")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for examples")
    
    try:
        vector_db = LegalVectorDatabase()
        rag_system = AdvancedLegalRAG(vector_db)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == 'help':
                    print("\n💡 Example Questions:")
                    print("   - What does 18 U.S.C. 2703 say about digital evidence?")
                    print("   - What are the Fourth Amendment protections for digital privacy?")
                    print("   - What does Smith v. Maryland say about privacy?")
                    print("   - What are the DOJ policies on evidence collection?")
                    print("   - What training is available for digital forensics?")
                    continue
                
                if not question:
                    continue
                
                print(f"\n🔍 Processing: {question}")
                response = rag_system.ask_question(question, jurisdiction="federal", max_results=3)
                
                print(f"\n📊 Results Summary:")
                print(f"   Top Score: {response['top_score']:.3f}")
                print(f"   Total Results: {response['total_results']}")
                print(f"   Jurisdiction: {response['jurisdiction']}")
                
                if response['search_results']:
                    print(f"\n🏆 Top Result:")
                    top_result = response['search_results'][0]
                    print(f"   📄 Type: {top_result.document_type}")
                    print(f"   📍 Jurisdiction: {top_result.jurisdiction}")
                    print(f"   📋 Law Status: {top_result.law_status}")
                    print(f"   📖 Content: {top_result.content[:200]}...")
                    
                    if top_result.citation_chain:
                        print(f"   ⚖️ Citations: {', '.join(top_result.citation_chain[:2])}")
                
                if response['citation_chain']:
                    print(f"\n🔗 Related Citations: {', '.join(response['citation_chain'][:3])}")
                
                print(f"\n📈 Average Relevance Scores:")
                for factor, score in response['relevance_breakdown'].items():
                    print(f"   {factor}: {score:.3f}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")

def main():
    """Main test function."""
    print("🚀 Advanced Legal RAG System Testing")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "enhancement":
            test_query_enhancement()
        elif mode == "search":
            test_hybrid_search()
        elif mode == "context":
            test_context_management()
        elif mode == "interactive":
            interactive_test()
        else:
            print("❌ Unknown mode. Use: enhancement, search, context, or interactive")
    else:
        # Run all tests
        test_query_enhancement()
        test_hybrid_search()
        test_context_management()
        
        # Ask if user wants interactive mode
        try:
            choice = input("\n🤖 Would you like to try interactive mode? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_test()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
