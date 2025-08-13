#!/usr/bin/env python3
"""
Interactive LangChain Legal RAG Chatbot Interface

A user-friendly interface for the LangChain-based legal RAG chatbot.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))
from langchain_rag_chatbot import LangChainLegalRAGChatbot, format_langchain_response

def print_banner():
    """Print the chatbot banner."""
    print("=" * 70)
    print("🤖 LANGCHAIN LEGAL RAG CHATBOT")
    print("=" * 70)
    print("💰 Cost-effective: GPT-3.5-turbo with LangChain")
    print("⚖️ Specialized: Legal document Q&A")
    print("🔍 Advanced: Hybrid search + intelligent generation")
    print("🔗 Framework: LangChain for optimal RAG performance")
    print("=" * 70)

def print_help():
    """Print help information."""
    print("\n💡 **Available Commands:**")
    print("   - Type your legal question to get an answer")
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
    print("\n💡 **LangChain Features:**")
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
    print(f"   LangChain Components: {', '.join(stats['langchain_components'])}")

def interactive_mode():
    """Run the interactive LangChain chatbot."""
    
    print_banner()
    
    try:
        # Initialize chatbot
        print("🔧 Initializing LangChain chatbot...")
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3
        )
        print("✅ LangChain chatbot ready!")
        print_help()
        
        while True:
            try:
                # Get user input
                print("\n" + "-" * 50)
                question = input("❓ Your legal question: ").strip()
                
                # Handle commands
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using the LangChain Legal RAG Chatbot!")
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
                
                # Process the question
                print(f"\n🔍 Processing: {question}")
                print("⏳ Generating response with LangChain...")
                
                response = chatbot.ask(question, include_metadata=True)
                formatted_response = format_langchain_response(response)
                
                print("\n" + "=" * 50)
                print(formatted_response)
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different question.")
    
    except Exception as e:
        print(f"❌ Failed to initialize LangChain chatbot: {e}")
        print("Make sure to set OPENAI_API_KEY in your .env file")

def quick_test():
    """Run a quick test of the LangChain chatbot."""
    
    print("🧪 Quick Test Mode - LangChain")
    print("=" * 40)
    
    try:
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=600,
            temperature=0.3
        )
        
        test_question = "What does 18 U.S.C. 2703 say about digital evidence?"
        print(f"❓ Test Question: {test_question}")
        print("-" * 40)
        
        response = chatbot.ask(test_question, include_metadata=True)
        formatted_response = format_langchain_response(response)
        print(formatted_response)
        
        print("\n✅ LangChain test completed successfully!")
        
    except Exception as e:
        print(f"❌ LangChain test failed: {e}")

def test_langchain_features():
    """Test specific LangChain features."""
    
    print("🔗 LangChain Features Test")
    print("=" * 40)
    
    try:
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=600,
            temperature=0.3
        )
        
        # Test different prompt types
        test_questions = [
            "What does 18 U.S.C. 2703 say about digital evidence?",  # General Q&A
            "What legal authorities support digital evidence collection?",  # Citation-focused
            "And what about Fourth Amendment protections?",  # Follow-up
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Testing: {question}")
            print("-" * 30)
            
            response = chatbot.ask(question, include_metadata=True)
            
            # Show LangChain-specific info
            if 'metadata' in response and 'langchain_components' in response['metadata']:
                langchain_info = response['metadata']['langchain_components']
                print(f"   Prompt Type: {langchain_info['prompt_type']}")
                print(f"   Chat History Length: {langchain_info['chat_history_length']}")
            
            print(f"   Answer Preview: {response['answer'][:100]}...")
        
        print("\n✅ LangChain features test completed!")
        
    except Exception as e:
        print(f"❌ LangChain features test failed: {e}")

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            quick_test()
        elif mode == "features":
            test_langchain_features()
        elif mode == "interactive":
            interactive_mode()
        else:
            print("❌ Unknown mode. Use: 'test', 'features', or 'interactive'")
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
