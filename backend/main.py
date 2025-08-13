#!/usr/bin/env python3
"""
Main Backend Entry Point for Wisconsin Statutes RAG Chatbot

This integrates the Flask server with streaming chatbot functionality
and provides a unified API for the frontend.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import Flask server components
from flask_server.app import app, initialize_components
from chatbot.streaming_chatbot import interactive_streaming_mode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the backend."""
    
    print("🚀 Starting Wisconsin Statutes RAG Chatbot Backend...")
    print("=" * 60)
    
    # Check if we should run in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        print("🎯 Running in interactive mode...")
        interactive_streaming_mode()
        return
    
    # Initialize Flask components
    print("🔧 Initializing Flask server components...")
    if initialize_components():
        print("✅ Components initialized successfully")
        
        print("\n📡 Starting Flask server...")
        print("🌐 Server will be available at: http://localhost:5001")
        print("📋 API Documentation:")
        print("   POST /api/chat/stream - Streaming chat endpoint")
        print("   POST /api/documents/upload - Upload documents")
        print("   GET  /api/documents/list - List documents")
        print("   GET  /health - Health check")
        print("\n💡 Use 'python main.py interactive' for command-line mode")
        print("=" * 60)
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            threaded=True
        )
    else:
        print("❌ Failed to initialize components")
        sys.exit(1)

if __name__ == "__main__":
    main()
