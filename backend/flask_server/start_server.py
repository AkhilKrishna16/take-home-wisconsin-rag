#!/usr/bin/env python3
"""
Startup Script for Flask Legal RAG Chatbot Server

This script provides an easy way to start the Flask server with proper
configuration and error handling.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    # Load .env file from backend directory
    from dotenv import load_dotenv
    import os
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT',
        'PINECONE_INDEX_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    print("✅ Environment variables check passed")
    return True

def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = [
        'flask',
        'flask_cors',
        'openai',
        'pinecone',  # Updated package name
        'langchain',
        'langchain_openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Dependencies check passed")
    return True

def create_upload_directory():
    """Create upload directory if it doesn't exist."""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    print(f"✅ Upload directory ready: {upload_dir.absolute()}")

def start_server():
    """Start the Flask server."""
    print("🚀 Starting Flask Legal RAG Chatbot Server...")
    print("=" * 60)
    
    # Check prerequisites
    if not check_environment():
        return False
    
    if not check_dependencies():
        return False
    
    create_upload_directory()
    
    print("\n📡 Server Configuration:")
    print("   Host: 0.0.0.0")
    print("   Port: 5002")
    print("   Debug: True")
    print("   Threaded: True")
    
    print("\n🔗 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /api/chat - Chat with chatbot")
    print("   POST /api/chat/stream - Streaming chat")
    print("   POST /api/documents/upload - Upload document (background processing)")
    print("   GET  /api/tasks/<id> - Get task status")
    print("   GET  /api/tasks - List all tasks")
    print("   DELETE /api/tasks/<id> - Delete task from tracking")
    print("   POST /api/documents/search - Search documents")
    print("   GET  /api/documents/list - List documents")
    print("   DELETE /api/documents/<id> - Delete document")
    print("   GET  /api/chat/history - Get chat history")
    print("   DELETE /api/chat/history - Clear chat history")
    print("   GET  /api/stats - Get system stats")
    
    print("\n🌐 Server will be available at:")
    print("   http://localhost:5002")
    print("   http://127.0.0.1:5002")
    
    print("\n" + "=" * 60)
    print("🚀 Starting server... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    try:
        # Start the Flask app
        from app import app
        
        app.run(
            host='0.0.0.0',
            port=5002,
            debug=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False

def main():
    """Main function."""
    print("🤖 Flask Legal RAG Chatbot Server")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found in current directory")
        print("Please run this script from the flask_server directory")
        return False
    
    # Start the server
    return start_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
