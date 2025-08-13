#!/usr/bin/env python3
"""
Startup script for the Wisconsin Statutes RAG Chatbot Backend

This script initializes the backend server with proper error handling
and environment validation.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
load_dotenv(backend_dir / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY', 
        'PINECONE_ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please create a .env file in the backend directory with:")
        for var in missing_vars:
            logger.error(f"   {var}=your_value_here")
        return False
    
    logger.info("✅ Environment variables validated")
    return True

def check_dependencies():
    """Check if required Python packages are installed."""
    try:
        import flask
        import openai
        import langchain
        import pinecone
        logger.info("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main startup function."""
    print("🚀 Wisconsin Statutes RAG Chatbot Backend")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the main application
    try:
        from main import main as run_main
        run_main()
    except KeyboardInterrupt:
        logger.info("👋 Backend stopped by user")
    except Exception as e:
        logger.error(f"❌ Backend failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
