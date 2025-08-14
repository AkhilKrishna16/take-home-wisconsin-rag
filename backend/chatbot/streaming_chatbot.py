#!/usr/bin/env python3
"""
Streaming LangChain Legal RAG Chatbot Interface

A user-friendly streaming interface for the LangChain-based legal RAG chatbot.
Words and letters appear sequentially for a more engaging experience.
"""

import sys
import os
import time
from typing import Generator

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))
from langchain_rag_chatbot import LangChainLegalRAGChatbot, format_langchain_response

def print_banner():
    """Print the chatbot banner."""
    print("=" * 70)
    print("🤖 STREAMING LANGCHAIN LEGAL RAG CHATBOT")
    print("=" * 70)
    print("💰 Cost-effective: GPT-3.5-turbo with LangChain")
    print("⚖️ Specialized: Legal document Q&A")
    print("🔍 Advanced: Hybrid search + intelligent generation")
    print("🔗 Framework: LangChain for optimal RAG performance")
    print("📡 Streaming: Real-time response generation")
    print("=" * 70)

def print_help():
    """Print help information."""
    print("\n💡 **Available Commands:**")
    print("   - Type your legal question to get a streaming answer")
    print("   - 'help': Show this help message")
    print("   - 'history': Show conversation history")
    print("   - 'clear': Clear conversation history")
    print("   - 'stats': Show usage statistics")
    print("   - 'quit' or 'exit': End the session")
    print("\n💡 **Example Questions:**")
    print("   - What does 18 U.S.C. 2703 say about digital evidence?")
    print("   - What are the Fourth Amendment protections for digital privacy?")
    print("   - What does Smith v. Maryland say about privacy?")
    print("   - What are the requirements for digital evidence collection?")
    print("   - What training is available for digital forensics?")
    print("   - What are the DOJ policies on evidence preservation?")
    print("   - What legal authorities support digital evidence collection?")
    print("\n💡 **Streaming Features:**")
    print("   - Real-time word-by-word response generation")
    print("   - Intelligent prompt selection based on question type")
    print("   - Conversation memory and context management")
    print("   - Advanced retrieval with relevance scoring")
    print("   - Cost-effective GPT-3.5-turbo integration")

def print_history(chatbot):
    """Print conversation history."""
    history = chatbot.get_conversation_history()
    
    if not history:
        print("📭 No conversation history yet.")
        return
    
    print(f"\n📚 **Conversation History ({len(history)} exchanges):**")
    print("=" * 50)
    
    for i, exchange in enumerate(history, 1):
        print(f"\n{i}. **Question:** {exchange['question']}")
        print(f"   **Answer:** {exchange['answer'][:200]}...")
        print(f"   **Time:** {exchange['timestamp']}")
        print("-" * 30)

def print_stats(chatbot):
    """Print usage statistics."""
    stats = chatbot.get_usage_stats()
    
    print(f"\n📊 **Usage Statistics:**")
    print("=" * 30)
    print(f"   Total Conversations: {stats['total_conversations']}")
    print(f"   Model Used: {stats['model_used']}")
    print(f"   Max Tokens: {stats['max_tokens']}")
    print(f"   Temperature: {stats['temperature']}")
    print(f"   Streaming Enabled: {chatbot.streaming}")
    print(f"   LangChain Components: {', '.join(stats['langchain_components'])}")

def stream_response(chatbot, question: str) -> Generator[dict, None, None]:
    """Stream the chatbot response."""
    
    print(f"\n🔍 Processing: {question}")
    print("⏳ Generating streaming response...")
    print("\n" + "=" * 50)
    
    # Start streaming
    print("🤖 **Answer:**")
    
    full_response = None
    for chunk in chatbot.ask_streaming(question, include_metadata=True):
        if chunk['type'] == 'content':
            # Print content as it streams
            content = chunk['content']
            print(content, end='', flush=True)
            
        elif chunk['type'] == 'complete':
            # Store the complete response
            full_response = chunk['response']
            print("\n\n" + "=" * 50)
            
            # Display safety features
            if 'confidence_score' in full_response:
                confidence = full_response['confidence_score']
                print("🎯 **Confidence Assessment:**")
                if confidence >= 0.8:
                    print(f"   ✅ High Confidence: {confidence:.1%}")
                elif confidence >= 0.6:
                    print(f"   ⚠️  Moderate Confidence: {confidence:.1%}")
                else:
                    print(f"   ❌ Low Confidence: {confidence:.1%}")
                print("")
            
            # Display safety warnings
            if 'safety_warnings' in full_response:
                warnings = full_response['safety_warnings']
                print("⚠️ **Safety Warnings:**")
                
                if warnings.get('use_of_force_warning'):
                    print("   🔴 USE OF FORCE QUERY: This response involves use of force considerations.")
                    print("      Please consult with qualified legal counsel for specific guidance.")
                
                if warnings.get('jurisdiction_warning'):
                    print("   🟡 JURISDICTION-SPECIFIC: This information may be jurisdiction-specific.")
                    print("      Verify applicability to your jurisdiction.")
                
                if warnings.get('outdated_warning'):
                    print("   🟠 POTENTIALLY OUTDATED: This information may be outdated.")
                    print("      Verify current legal status.")
                
                if warnings.get('low_confidence_warning'):
                    print("   🔴 LOW CONFIDENCE: Limited information available.")
                    print("      Consider consulting additional sources.")
                
                if warnings.get('legal_disclaimer'):
                    print("   📋 LEGAL DISCLAIMER: This is informational only, not legal advice.")
                    print("      Consult qualified legal counsel for specific legal matters.")
                
                print("")
            
            # Display metadata if available
            if 'metadata' in full_response:
                metadata = full_response['metadata']
                
                print("📊 **Search Quality:**")
                print(f"   Top Score: {metadata['search_quality']['top_score']:.3f}")
                print(f"   Results Found: {metadata['search_quality']['total_results']}")
                print("")
                
                if metadata['citations_found']:
                    print("⚖️ **Legal Authorities Found:**")
                    for citation in metadata['citations_found'][:5]:
                        print(f"   - {citation}")
                    print("")
                
                # Display source documents if available
                if 'source_documents' in metadata and metadata['source_documents']:
                    print("📄 **Source Documents Used:**")
                    for doc in metadata['source_documents'][:3]:  # Show top 3 documents
                        print(f"   📋 Source {doc['source_number']} (Score: {doc['relevance_score']:.3f}):")
                        print(f"      Type: {doc['document_type']}")
                        print(f"      Jurisdiction: {doc['jurisdiction']}")
                        print(f"      Status: {doc['law_status']}")
                        if doc['file_name'] != 'Unknown':
                            print(f"      File: {doc['file_name']}")
                        if doc['section'] != 'Unknown':
                            print(f"      Section: {doc['section']}")
                        if doc['citations']:
                            print(f"      Citations: {', '.join(doc['citations'][:3])}")
                        print(f"      Preview: {doc['content_preview']}")
                        print("")
                    print("")
                
                print("📈 **Relevance Breakdown:**")
                for factor, score in metadata['search_quality']['relevance_breakdown'].items():
                    print(f"   {factor}: {score:.3f}")
                print("")
                
                # LangChain specific info
                if 'langchain_components' in metadata:
                    langchain_info = metadata['langchain_components']
                    print("🔗 **LangChain Info:**")
                    print(f"   Prompt Type: {langchain_info['prompt_type']}")
                    print(f"   Chat History Length: {langchain_info['chat_history_length']}")
                    print("")
                
                # Safety features info
                if 'safety_features' in metadata:
                    safety_info = metadata['safety_features']
                    print("🛡️ **Safety Features:**")
                    print(f"   Confidence Score: {safety_info['confidence_score']:.3f}")
                    print(f"   Use of Force Detected: {'Yes' if safety_info['use_of_force_detected'] else 'No'}")
                    print(f"   Jurisdiction Specific: {'Yes' if safety_info['jurisdiction_specific'] else 'No'}")
                    print(f"   Potentially Outdated: {'Yes' if safety_info['potentially_outdated'] else 'No'}")
                    print(f"   Low Confidence: {'Yes' if safety_info['low_confidence'] else 'No'}")
                    print("")
            
            # Technical info
            print("🔧 **Technical Info:**")
            print(f"   Model: {full_response['model_used']}")
            print(f"   Framework: LangChain (Streaming)")
            print(f"   Timestamp: {full_response['timestamp']}")
            print("=" * 50)
            
        elif chunk['type'] == 'error':
            # Handle error
            error_response = chunk['response']
            print(f"\n❌ Error: {error_response['answer']}")
            print("=" * 50)
    
    return full_response

def interactive_streaming_mode():
    """Run the interactive streaming LangChain chatbot."""
    
    print_banner()
    
    try:
        # Initialize streaming chatbot
        print("🔧 Initializing streaming LangChain chatbot...")
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3,
            streaming=True
        )
        print("✅ Streaming LangChain chatbot ready!")
        print_help()
        
        while True:
            try:
                # Get user input
                print("\n" + "-" * 50)
                question = input("❓ Your legal question: ").strip()
                
                # Handle commands
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using the Streaming LangChain Legal RAG Chatbot!")
                    break
                
                elif question.lower() == 'help':
                    print_help()
                    continue
                
                elif question.lower() == 'history':
                    print_history(chatbot)
                    continue
                
                elif question.lower() == 'clear':
                    chatbot.clear_history()
                    print("🗑️ Conversation history cleared.")
                    continue
                
                elif question.lower() == 'stats':
                    print_stats(chatbot)
                    continue
                
                elif not question:
                    print("❌ Please enter a question.")
                    continue
                
                # Process the question with streaming
                start_time = time.time()
                response = stream_response(chatbot, question)
                end_time = time.time()
                
                if response:
                    print(f"\n⏱️ Response time: {end_time - start_time:.2f} seconds")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different question.")
    
    except Exception as e:
        print(f"❌ Failed to initialize streaming LangChain chatbot: {e}")
        print("Make sure to set OPENAI_API_KEY in your .env file")

def quick_streaming_test():
    """Run a quick streaming test."""
    
    print("🧪 Quick Streaming Test")
    print("=" * 40)
    
    try:
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=600,
            temperature=0.3,
            streaming=True
        )
        
        test_question = "What does 18 U.S.C. 2703 say about digital evidence?"
        print(f"❓ Test Question: {test_question}")
        print("-" * 40)
        
        # Stream the response
        for chunk in chatbot.ask_streaming(test_question, include_metadata=True):
            if chunk['type'] == 'content':
                print(chunk['content'], end='', flush=True)
            elif chunk['type'] == 'complete':
                print("\n\n✅ Streaming test completed successfully!")
                break
            elif chunk['type'] == 'error':
                print(f"\n❌ Streaming test failed: {chunk['response']['answer']}")
                break
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            quick_streaming_test()
        elif mode == "interactive":
            interactive_streaming_mode()
        else:
            print("❌ Unknown mode. Use: 'test' or 'interactive'")
    else:
        # Default to interactive mode
        interactive_streaming_mode()

if __name__ == "__main__":
    main()
