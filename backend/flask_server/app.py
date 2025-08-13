#!/usr/bin/env python3
"""
Flask Server for Legal RAG Chatbot

Provides API endpoints for:
1. Chatbot querying with streaming support
2. Document upload and vectorization for Pinecone
3. Document management and search
"""

import os
import sys
import json
import logging
import threading
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chatbot.langchain_rag_chatbot import LangChainLegalRAGChatbot
from document_processing.document_processor import DocumentProcessor
from vector_db.vector_database import LegalVectorDatabase

# Load environment variables from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'doc', 'html', 'md'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global instances
chatbot = None
document_processor = None
vector_db = None

# Background task tracking
background_tasks = {}

def initialize_components():
    """Initialize chatbot and document processing components."""
    global chatbot, document_processor, vector_db
    
    try:
        # Check if required environment variables are set
        required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
            logger.warning("Server will start but some features may not work properly")
            return False
        
        # Initialize vector database
        vector_db = LegalVectorDatabase()
        logger.info("✅ Vector database initialized")
        
        # Initialize document processor
        document_processor = DocumentProcessor(output_dir="processed_documents", use_vector_db=True)
        logger.info("✅ Document processor initialized")
        
        # Initialize chatbot
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3,
            streaming=False  # We'll handle streaming manually
        )
        logger.info("✅ Chatbot initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        return False

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_document_background(task_id: str, filepath: str, metadata: Dict[str, Any]):
    """Process document in background thread."""
    global background_tasks
    
    try:
        logger.info(f"🔄 Starting background processing for task {task_id}")
        
        # Update task status to processing
        background_tasks[task_id]['status'] = 'processing'
        background_tasks[task_id]['progress'] = 10
        background_tasks[task_id]['message'] = 'Starting document processing...'
        
        # Process the document
        result = document_processor.process_document(
            file_path=filepath,
            document_type=metadata.get('document_type', None)
        )
        
        # Check if processing was successful
        if result and 'chunk_count' in result:
            # Update task status to completed
            background_tasks[task_id]['status'] = 'completed'
            background_tasks[task_id]['progress'] = 100
            background_tasks[task_id]['message'] = 'Document processed successfully'
            background_tasks[task_id]['result'] = {
                'document_id': result.get('vector_db_id', result.get('file_hash', 'unknown')),
                'chunks_created': result.get('chunk_count', 0),
                'processing_time': 0,  # Could add timing if needed
                'file_name': result.get('file_name', 'unknown'),
                'document_type': result.get('document_type', 'unknown')
            }
            logger.info(f"✅ Background processing completed for task {task_id}")
        else:
            # Update task status to failed
            background_tasks[task_id]['status'] = 'failed'
            background_tasks[task_id]['progress'] = 0
            background_tasks[task_id]['message'] = f"Processing failed: Invalid result format"
            background_tasks[task_id]['error'] = "Invalid result format"
            logger.error(f"❌ Background processing failed for task {task_id}: Invalid result format")
            
    except Exception as e:
        # Update task status to failed
        background_tasks[task_id]['status'] = 'failed'
        background_tasks[task_id]['progress'] = 0
        background_tasks[task_id]['message'] = f'Processing error: {str(e)}'
        background_tasks[task_id]['error'] = str(e)
        logger.error(f"❌ Background processing error for task {task_id}: {e}")
    
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Cleaned up temporary file: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to clean up temporary file {filepath}: {e}")

def format_error_response(error: str, status_code: int = 400) -> Response:
    """Format error response."""
    return jsonify({
        'error': error,
        'timestamp': datetime.now().isoformat(),
        'status': 'error'
    }), status_code

def format_success_response(data: Dict[str, Any], message: str = "Success") -> Response:
    """Format success response."""
    return jsonify({
        'data': data,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'chatbot': chatbot is not None,
            'document_processor': document_processor is not None,
            'vector_db': vector_db is not None
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for non-streaming responses."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return format_error_response("Question is required")
        
        question = data['question']
        jurisdiction = data.get('jurisdiction', 'federal')
        include_metadata = data.get('include_metadata', True)
        
        # Get response from chatbot
        response = chatbot.ask(
            question=question,
            jurisdiction=jurisdiction,
            include_metadata=include_metadata
        )
        
        return format_success_response(response, "Chat response generated successfully")
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return format_error_response(f"Error processing chat request: {str(e)}", 500)

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return format_error_response("Question is required")
        
        question = data['question']
        jurisdiction = data.get('jurisdiction', 'federal')
        include_metadata = data.get('include_metadata', True)
        
        def generate_stream():
            """Generate streaming response."""
            try:
                for chunk in chatbot.ask_streaming(
                    question=question,
                    jurisdiction=jurisdiction,
                    include_metadata=include_metadata
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {
                    'type': 'error',
                    'response': {
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming chat endpoint: {e}")
        return format_error_response(f"Error processing streaming chat request: {str(e)}", 500)

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process document endpoint with background processing."""
    
    if not document_processor or not vector_db:
        return format_error_response("Document processor not initialized", 500)
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return format_error_response("No file provided")
        
        file = request.files['file']
        
        if file.filename == '':
            return format_error_response("No file selected")
        
        if not allowed_file(file.filename):
            return format_error_response(f"File type not allowed. Allowed types: {', '.join(app.config['ALLOWED_EXTENSIONS'])}")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Get metadata from form data
        metadata = {
            'file_name': secure_filename(file.filename),
            'document_type': request.form.get('document_type', 'Unknown'),
            'jurisdiction': request.form.get('jurisdiction', 'federal'),
            'law_status': request.form.get('law_status', 'current'),
            'upload_date': datetime.now().isoformat(),
            'uploaded_by': request.form.get('uploaded_by', 'unknown')
        }
        
        # Save file temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{metadata['file_name']}")
        file.save(filepath)
        
        # Initialize task tracking
        background_tasks[task_id] = {
            'status': 'uploaded',
            'progress': 0,
            'message': 'File uploaded, starting processing...',
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
            'file_name': metadata['file_name']
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_document_background,
            args=(task_id, filepath, metadata),
            daemon=True
        )
        thread.start()
        
        logger.info(f"📤 Document uploaded and background processing started: {metadata['file_name']} (Task ID: {task_id})")
        
        return format_success_response({
            'task_id': task_id,
            'status': 'uploaded',
            'message': 'Document uploaded successfully. Processing started in background.',
            'metadata': metadata
        }, f"Document '{metadata['file_name']}' uploaded and processing started")
        
    except Exception as e:
        logger.error(f"Error in document upload: {e}")
        return format_error_response(f"Error uploading document: {str(e)}", 500)

@app.route('/api/documents/search', methods=['POST'])
def search_documents():
    """Search documents endpoint."""
    
    if not vector_db:
        return format_error_response("Vector database not initialized", 500)
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return format_error_response("Search query is required")
        
        query = data['query']
        max_results = data.get('max_results', 10)
        jurisdiction = data.get('jurisdiction', None)
        document_type = data.get('document_type', None)
        
        # Perform search
        filter_metadata = {}
        if jurisdiction:
            filter_metadata['jurisdiction'] = jurisdiction
        if document_type:
            filter_metadata['chunk_type'] = document_type
            
        search_results = vector_db.search(
            query=query,
            top_k=max_results,
            filter_metadata=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for result in search_results:
            content = result.get('metadata', {}).get('content', '')
            if content is None:
                content = ''
            
            formatted_results.append({
                'id': result.get('id', 'unknown'),
                'score': result.get('score', 0.0),
                'content': content,
                'metadata': result.get('metadata', {})
            })
        
        return format_success_response({
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results)
        }, "Search completed successfully")
        
    except Exception as e:
        logger.error(f"Error in document search: {e}")
        return format_error_response(f"Error performing search: {str(e)}", 500)

@app.route('/api/documents/list', methods=['GET'])
def list_documents():
    """List all documents in the database."""
    
    if not vector_db:
        return format_error_response("Vector database not initialized", 500)
    
    try:
        # Get document list from vector database
        documents = vector_db.list_documents()
        
        return format_success_response({
            'documents': documents,
            'total_documents': len(documents)
        }, "Documents retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return format_error_response(f"Error retrieving documents: {str(e)}", 500)

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document from the database."""
    
    if not vector_db:
        return format_error_response("Vector database not initialized", 500)
    
    try:
        # Delete document from vector database
        success = vector_db.delete_document(document_id)
        
        if success:
            return format_success_response({
                'document_id': document_id
            }, f"Document {document_id} deleted successfully")
        else:
            return format_error_response(f"Document {document_id} not found")
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return format_error_response(f"Error deleting document: {str(e)}", 500)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of a background processing task."""
    
    if task_id not in background_tasks:
        return format_error_response(f"Task {task_id} not found", 404)
    
    task = background_tasks[task_id]
    
    return format_success_response({
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
        'message': task['message'],
        'metadata': task['metadata'],
        'created_at': task['created_at'],
        'file_name': task['file_name'],
        'result': task.get('result'),
        'error': task.get('error')
    }, f"Task status retrieved successfully")

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """List all background processing tasks."""
    
    task_list = []
    for task_id, task in background_tasks.items():
        task_list.append({
            'task_id': task_id,
            'status': task['status'],
            'progress': task['progress'],
            'message': task['message'],
            'file_name': task['file_name'],
            'created_at': task['created_at'],
            'result': task.get('result'),
            'error': task.get('error')
        })
    
    # Sort by creation time (newest first)
    task_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return format_success_response({
        'tasks': task_list,
        'total_tasks': len(task_list)
    }, "Tasks retrieved successfully")

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task from tracking (doesn't affect processed documents)."""
    
    if task_id not in background_tasks:
        return format_error_response(f"Task {task_id} not found", 404)
    
    # Remove task from tracking
    deleted_task = background_tasks.pop(task_id)
    
    return format_success_response({
        'task_id': task_id,
        'file_name': deleted_task['file_name']
    }, f"Task {task_id} deleted from tracking")

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        history = chatbot.get_conversation_history()
        
        return format_success_response({
            'history': history,
            'total_exchanges': len(history)
        }, "Chat history retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return format_error_response(f"Error retrieving chat history: {str(e)}", 500)

@app.route('/api/chat/history', methods=['DELETE'])
def clear_chat_history():
    """Clear chat history."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        chatbot.clear_history()
        
        return format_success_response({}, "Chat history cleared successfully")
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return format_error_response(f"Error clearing chat history: {str(e)}", 500)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics."""
    
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'chatbot': chatbot is not None,
                'document_processor': document_processor is not None,
                'vector_db': vector_db is not None
            }
        }
        
        if chatbot:
            stats['chatbot_stats'] = chatbot.get_usage_stats()
        
        if vector_db:
            try:
                stats['vector_db_stats'] = {
                    'total_documents': len(vector_db.list_documents())
                }
            except Exception as e:
                stats['vector_db_stats'] = {'error': f'Unable to retrieve stats: {str(e)}'}
        
        # Add task statistics
        stats['task_stats'] = {
            'total_tasks': len(background_tasks),
            'tasks_by_status': {
                'uploaded': len([t for t in background_tasks.values() if t['status'] == 'uploaded']),
                'processing': len([t for t in background_tasks.values() if t['status'] == 'processing']),
                'completed': len([t for t in background_tasks.values() if t['status'] == 'completed']),
                'failed': len([t for t in background_tasks.values() if t['status'] == 'failed'])
            }
        }
        
        return format_success_response(stats, "Statistics retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return format_error_response(f"Error retrieving statistics: {str(e)}", 500)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return format_error_response("File too large. Maximum size is 50MB", 413)

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return format_error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return format_error_response("Internal server error", 500)

# Initialize components when module is imported
try:
    initialize_components()
except Exception as e:
    logger.warning(f"⚠️ Component initialization failed: {e}")
    logger.warning("Server will start but some features may not work properly")

if __name__ == '__main__':
    # Initialize components
    if initialize_components():
        logger.info("🚀 Flask server starting...")
        logger.info("📡 Available endpoints:")
        logger.info("   POST /api/chat - Chat with chatbot")
        logger.info("   POST /api/chat/stream - Streaming chat")
        logger.info("   POST /api/documents/upload - Upload document (background processing)")
        logger.info("   GET  /api/tasks/<id> - Get task status")
        logger.info("   GET  /api/tasks - List all tasks")
        logger.info("   DELETE /api/tasks/<id> - Delete task from tracking")
        logger.info("   POST /api/documents/search - Search documents")
        logger.info("   GET  /api/documents/list - List documents")
        logger.info("   DELETE /api/documents/<id> - Delete document")
        logger.info("   GET  /api/chat/history - Get chat history")
        logger.info("   DELETE /api/chat/history - Clear chat history")
        logger.info("   GET  /api/stats - Get system stats")
        logger.info("   GET  /health - Health check")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    else:
        logger.error("❌ Failed to initialize components. Exiting.")
        sys.exit(1)
