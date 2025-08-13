#!/usr/bin/env python3
"""
Simple Streaming Example

Demonstrates how to use the streaming chatbot functionality.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))
from langchain_rag_chatbot import LangChainLegalRAGChatbot

def simple_streaming_example():
    """Simple streaming example."""
    
    print("📡 Streaming Chatbot Example")
    print("=" * 40)
    
    try:
        # Initialize streaming chatbot
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=600,
            temperature=0.3,
            streaming=True  # Enable streaming
        )
        
        # Test question
        question = "What does 18 U.S.C. 2703 say about digital evidence?"
        
        print(f"❓ Question: {question}")
        print("\n🤖 Streaming Response:")
        print("-" * 40)
        
        # Stream the response
        start_time = time.time()
        
        for chunk in chatbot.ask_streaming(question):
            if chunk['type'] == 'content':
                # Print each word as it comes
                print(chunk['content'], end='', flush=True)
                
            elif chunk['type'] == 'complete':
                end_time = time.time()
                print(f"\n\n⏱️ Total time: {end_time - start_time:.2f} seconds")
                print("✅ Streaming completed!")
                break
                
            elif chunk['type'] == 'error':
                print(f"\n❌ Error: {chunk['response']['answer']}")
                break
        
    except Exception as e:
        print(f"❌ Error: {e}")

def word_by_word_streaming():
    """Word-by-word streaming with delays for demonstration."""
    
    print("📝 Word-by-Word Streaming Demo")
    print("=" * 40)
    
    try:
        # Initialize streaming chatbot
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=400,
            temperature=0.3,
            streaming=True
        )
        
        question = "What are the Fourth Amendment protections?"
        
        print(f"❓ Question: {question}")
        print("\n🤖 Word-by-Word Response:")
        print("-" * 40)
        
        for chunk in chatbot.ask_streaming(question):
            if chunk['type'] == 'content':
                # Add a small delay to make streaming more visible
                content = chunk['content']
                print(content, end='', flush=True)
                time.sleep(0.05)  # 50ms delay
                
            elif chunk['type'] == 'complete':
                print("\n\n✅ Word-by-word streaming completed!")
                break
                
            elif chunk['type'] == 'error':
                print(f"\n❌ Error: {chunk['response']['answer']}")
                break
    
    except Exception as e:
        print(f"❌ Error: {e}")

def streaming_with_metadata():
    """Streaming with metadata display."""
    
    print("📊 Streaming with Metadata")
    print("=" * 40)
    
    try:
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.3,
            streaming=True
        )
        
        question = "What does Smith v. Maryland say about privacy?"
        
        print(f"❓ Question: {question}")
        print("\n🤖 Streaming Response with Metadata:")
        print("-" * 40)
        
        full_response = None
        
        for chunk in chatbot.ask_streaming(question, include_metadata=True):
            if chunk['type'] == 'content':
                print(chunk['content'], end='', flush=True)
                
            elif chunk['type'] == 'complete':
                full_response = chunk['response']
                print("\n\n" + "=" * 40)
                print("📊 Response Metadata:")
                print(f"   Confidence: {full_response['confidence_score']:.1%}")
                print(f"   Model: {full_response['model_used']}")
                print(f"   Prompt Type: {full_response['prompt_type']}")
                
                if 'metadata' in full_response:
                    metadata = full_response['metadata']
                    print(f"   Search Score: {metadata['search_quality']['top_score']:.3f}")
                    print(f"   Results Found: {metadata['search_quality']['total_results']}")
                
                print("✅ Streaming with metadata completed!")
                break
                
            elif chunk['type'] == 'error':
                print(f"\n❌ Error: {chunk['response']['answer']}")
                break
    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        example = sys.argv[1].lower()
        
        if example == "simple":
            simple_streaming_example()
        elif example == "word":
            word_by_word_streaming()
        elif example == "metadata":
            streaming_with_metadata()
        else:
            print("❌ Unknown example. Use: 'simple', 'word', or 'metadata'")
    else:
        # Run all examples
        print("Running all streaming examples...\n")
        
        simple_streaming_example()
        print("\n" + "="*60 + "\n")
        
        word_by_word_streaming()
        print("\n" + "="*60 + "\n")
        
        streaming_with_metadata()

if __name__ == "__main__":
    main()
