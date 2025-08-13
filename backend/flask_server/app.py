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
from pathlib import Path
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, Response, stream_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chatbot.langchain_rag_chatbot import LangChainLegalRAGChatbot
from document_processing.document_processor import DocumentProcessor
from vector_db.vector_database import LegalVectorDatabase
from cross_reference_system import CrossReferenceSystem

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

# Initialize cross-reference system
cross_ref_system = None

# Flag to track if components have been initialized
_components_initialized = False

def initialize_components():
    """Initialize all system components."""
    global chatbot, document_processor, vector_db, cross_ref_system, _components_initialized
    
    # Check if components are already initialized
    if _components_initialized:
        logger.info("🔄 Components already initialized, skipping...")
        return True
    
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
        
        # Initialize chatbot with streaming enabled
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3,
            streaming=True  # Enable streaming for real-time responses
        )
        logger.info("✅ Chatbot initialized")
        
        # Initialize cross-reference system
        cross_ref_system = CrossReferenceSystem()
        logger.info("✅ Cross-reference system initialized")
        
        # Mark components as initialized
        _components_initialized = True
        
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
            """Generate streaming response with slower typing animation."""
            import time
            
            try:
                for chunk in chatbot.ask_streaming(
                    question=question,
                    jurisdiction=jurisdiction,
                    include_metadata=include_metadata
                ):
                    if chunk['type'] == 'content':
                        # Add slower typing animation for content chunks
                        content = chunk['content']
                        for char in content:
                            char_chunk = {
                                'type': 'content',
                                'content': char,
                                'full_answer': chunk.get('full_answer', '')
                            }
                            yield f"data: {json.dumps(char_chunk)}\n\n"
                            time.sleep(0.03)  # 30ms delay between characters for slower typing
                    else:
                        # For non-content chunks (complete, error, etc.), send immediately
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
        
        # Also try to index the document immediately if vector_db is available
        try:
            if vector_db:
                logger.info(f"Attempting immediate indexing for {metadata['file_name']}")
                # This will be handled in the background thread, but we can log it
        except Exception as e:
            logger.warning(f"Immediate indexing not available: {e}")
        
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

@app.route('/api/documents/download/<filename>', methods=['GET'])
def download_document(filename):
    """Download a document file."""
    
    try:
        # Security check: ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return format_error_response("Invalid filename", 400)
        
        # Get the backend directory (parent of flask_server)
        backend_dir = Path(__file__).parent.parent
        pdfs_dir = backend_dir / 'pdfs'
        
        # Create a mapping from processed filenames to actual files
        # This handles the case where the database contains processed filenames
        # but the actual files have different names
        filename_mapping = {
            # Map processed filenames to actual files
            '46F874E8-7C26-469A-AEDE-D944E5637B12_3.PDF': '1.pdf',
            '46F874E8-7C26-469A-AEDE-D944E5637B12_3.pdf': '1.pdf',
            'C74C1A87-8264-4600-B68C-906E1459C20D_2.PDF': '2.pdf',
            'C74C1A87-8264-4600-B68C-906E1459C20D_2.pdf': '2.pdf',
            'MIRANDAWARNINGFINAL.PDF': 'mirandawarningfinal.pdf',
            'MIRANDAWARNINGFINAL.pdf': 'mirandawarningfinal.pdf',
            # Add more mappings as needed
        }
        
        # Try to find the file by checking processed documents metadata
        try:
            processed_docs_dir = Path(__file__).parent.parent / 'processed_documents'
            for processed_file in processed_docs_dir.glob('*_processed.json'):
                try:
                    with open(processed_file, 'r') as f:
                        doc_data = json.load(f)
                        if doc_data.get('file_name', '').upper() == filename.upper():
                            # Found matching processed document, use its original file
                            original_file = doc_data.get('file_path', '').split('/')[-1]
                            if original_file and (pdfs_dir / original_file).exists():
                                actual_filename = original_file
                                break
                except Exception:
                    continue
        except Exception:
            pass  # Fall back to manual mapping
        
        # Create a comprehensive mapping from processed filenames to actual files
        # This handles the case where files were moved from uploads/ to pdfs/
        comprehensive_mapping = {
                     # Map processed filenames to actual files in pdfs/
                     '46F874E8-7C26-469A-AEDE-D944E5637B12_3.PDF': '1.pdf',
                     '46F874E8-7C26-469A-AEDE-D944E5637B12_3.pdf': '1.pdf',
                     'C74C1A87-8264-4600-B68C-906E1459C20D_2.PDF': '2.pdf',
                     'C74C1A87-8264-4600-B68C-906E1459C20D_2.pdf': '2.pdf',
                     'MIRANDAWARNINGFINAL.PDF': 'mirandawarningfinal.pdf',
                     'MIRANDAWARNINGFINAL.pdf': 'mirandawarningfinal.pdf',
                     # Add mappings for files that were in uploads/ but are now in pdfs/
                     '287EC2E6-CCBB-4512-ADAA-BEE90E424B46_MIRANDAWARNINGFINAL.PDF': 'mirandawarningfinal.pdf',
                     '287EC2E6-CCBB-4512-ADAA-BEE90E424B46_MIRANDAWARNINGFINAL.pdf': 'mirandawarningfinal.pdf',
                     # Handle the truncated filename case - map to existing Wisconsin Statutes file
                     'DAF-468E-B9C0-C1F_70.PDF': '1.pdf',
                     'DAF-468E-B9C0-C1F_70.pdf': '1.pdf',
                     '110D7158-F0AF-468E-B9C0-AADF25337C1F_70.PDF': '1.pdf',
                     '110D7158-F0AF-468E-B9C0-AADF25337C1F_70.pdf': '1.pdf',
                 }
        
        # Try to map the filename to an actual file using comprehensive mapping
        actual_filename = comprehensive_mapping.get(filename.upper(), filename)
        file_path = pdfs_dir / actual_filename
        
        # If the mapped file doesn't exist, try the original filename
        if not file_path.exists():
            file_path = pdfs_dir / filename
        
        if not file_path.exists():
            return format_error_response("Document not found", 404)
        
        # Check if file is within pdfs directory (security)
        try:
            file_path.resolve().relative_to(pdfs_dir.resolve())
        except ValueError:
            return format_error_response("Invalid file path", 400)
        
        # Return the file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=actual_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading document {filename}: {e}")
        return format_error_response(f"Error downloading document: {str(e)}", 500)

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

@app.route('/api/chat/save', methods=['POST'])
def save_chat():
    """Save current chat session."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        data = request.get_json()
        session_name = data.get('session_name', f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Get current conversation history
        history = chatbot.get_conversation_history()
        
        # Save to file
        chat_data = {
            'session_name': session_name,
            'created_at': datetime.now().isoformat(),
            'history': history,
            'total_exchanges': len(history)
        }
        
        # Create chats directory if it doesn't exist
        chats_dir = Path('saved_chats')
        chats_dir.mkdir(exist_ok=True)
        
        # Save to JSON file
        filename = f"{session_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = chats_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(chat_data, f, indent=2)
        
        logger.info(f"Chat saved: {filepath}")
        
        return format_success_response({
            'session_name': session_name,
            'filename': filename,
            'total_exchanges': len(history),
            'saved_at': datetime.now().isoformat()
        }, f"Chat session '{session_name}' saved successfully")
        
    except Exception as e:
        logger.error(f"Error saving chat: {e}")
        return format_error_response(f"Error saving chat: {str(e)}", 500)

@app.route('/api/chat/generate-name', methods=['POST'])
def generate_chat_name():
    """Generate an intelligent chat name using LLM based on the first query."""
    try:
        data = request.get_json()
        first_query = data.get('query', '')
        
        if not first_query.strip():
            return format_error_response("No query provided", 400)
        
        # Use the chatbot to generate a name
        try:
            if chatbot:
                # Create a simple prompt for name generation
                name_prompt = f"""Based on this legal question, generate a concise, professional title (3-5 words max) that captures the main topic:

Question: {first_query}

Generate only the title, nothing else:"""
                
                # Get a quick response for naming
                response = chatbot.ask(name_prompt)
                
                # Clean up the response to get just the title
                title = response.strip()
                # Remove quotes if present
                if title.startswith('"') and title.endswith('"'):
                    title = title[1:-1]
                # Remove any extra text after the title
                title = title.split('\n')[0].strip()
                
                # Ensure it's not too long
                if len(title) > 50:
                    words = title.split()[:5]
                    title = ' '.join(words)
                
                # Fallback if response is empty or too short
                if not title or len(title) < 3:
                    title = "Legal Inquiry"
                
                logger.info(f"Generated LLM chat name: {title} for query: {first_query}")
                return format_success_response({
                    'name': title
                }, f"Generated chat name: {title}")
            else:
                logger.warning("Chatbot not available, using fallback naming")
                raise Exception("Chatbot not available")
                
        except Exception as e:
            logger.error(f"Error generating chat name with LLM: {e}")
            # Fallback to simple keyword extraction
            words = first_query.split()
            meaningful_words = [w for w in words if len(w) > 3 and w.lower() not in ['what', 'how', 'when', 'where', 'why', 'tell', 'about', 'explain']]
            if meaningful_words:
                title = ' '.join(meaningful_words[:3]).title()
            else:
                title = "Legal Inquiry"
            
            return format_success_response({
                'name': title
            }, f"Generated chat name: {title}")
        
    except Exception as e:
        logger.error(f"Error generating chat name: {e}")
        return format_error_response(f"Error generating chat name: {str(e)}", 500)

@app.route('/api/chat/export', methods=['POST'])
def export_chat():
    """Export chat as report."""
    
    if not chatbot:
        return format_error_response("Chatbot not initialized", 500)
    
    try:
        data = request.get_json()
        export_format = data.get('format', 'pdf')  # pdf, docx, txt
        include_sources = data.get('include_sources', True)
        
        # Get current conversation history
        history = chatbot.get_conversation_history()
        
        if not history:
            return format_error_response("No chat history to export", 400)
        
        # Generate report content
        report_content = generate_report_content(history, include_sources)
        
        # Create exports directory if it doesn't exist
        exports_dir = Path('exports')
        exports_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = f"Chat_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if export_format == 'txt':
            filepath = exports_dir / f"{filename}.txt"
            with open(filepath, 'w') as f:
                f.write(report_content)
        elif export_format == 'json':
            filepath = exports_dir / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'format': export_format,
                    'include_sources': include_sources,
                    'content': report_content,
                    'history': history
                }, f, indent=2)
        else:
            # For PDF/DOCX, return the content for frontend to handle
            filepath = None
        
        return format_success_response({
            'filename': filepath.name if filepath else f"{filename}.{export_format}",
            'content': report_content,  # Always return content for frontend to handle
            'format': export_format,
            'exported_at': datetime.now().isoformat()
        }, f"Chat exported successfully as {export_format.upper()}")
        
    except Exception as e:
        logger.error(f"Error exporting chat: {e}")
        return format_error_response(f"Error exporting chat: {str(e)}", 500)

@app.route('/api/chat/list-saved', methods=['GET'])
def list_saved_chats():
    """List all saved chat sessions."""
    
    try:
        chats_dir = Path('saved_chats')
        if not chats_dir.exists():
            return format_success_response({
                'chats': [],
                'total_chats': 0
            }, "No saved chats found")
        
        chats = []
        for file_path in chats_dir.glob('*.json'):
            try:
                with open(file_path, 'r') as f:
                    chat_data = json.load(f)
                    chats.append({
                        'session_name': chat_data.get('session_name', 'Unnamed Session'),
                        'created_at': chat_data.get('created_at', ''),
                        'total_exchanges': chat_data.get('total_exchanges', 0),
                        'filename': file_path.name
                    })
            except Exception as e:
                logger.error(f"Error reading chat file {file_path}: {e}")
                continue
        
        # Sort by creation date (newest first)
        chats.sort(key=lambda x: x['created_at'], reverse=True)
        
        return format_success_response({
            'chats': chats,
            'total_chats': len(chats)
        }, f"Found {len(chats)} saved chat sessions")
        
    except Exception as e:
        logger.error(f"Error listing saved chats: {e}")
        return format_error_response(f"Error listing saved chats: {str(e)}", 500)

@app.route('/api/chat/load/<filename>', methods=['GET'])
def load_saved_chat(filename):
    """Load a specific saved chat session."""
    
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename:
            return format_error_response("Invalid filename", 400)
        
        file_path = Path('saved_chats') / filename
        if not file_path.exists():
            return format_error_response("Chat session not found", 404)
        
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
        
        return format_success_response(chat_data, f"Chat session '{chat_data.get('session_name', 'Unnamed')}' loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading saved chat {filename}: {e}")
        return format_error_response(f"Error loading saved chat: {str(e)}", 500)

@app.route('/api/chat/delete/<filename>', methods=['DELETE'])
def delete_saved_chat(filename):
    """Delete a specific saved chat session."""
    
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename:
            return format_error_response("Invalid filename", 400)
        
        file_path = Path('saved_chats') / filename
        if not file_path.exists():
            return format_error_response("Chat session not found", 404)
        
        # Load chat data for response
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
        
        # Delete the file
        file_path.unlink()
        
        return format_success_response({
            'deleted_filename': filename,
            'session_name': chat_data.get('session_name', 'Unnamed Session')
        }, f"Chat session '{chat_data.get('session_name', 'Unnamed')}' deleted successfully")
        
    except Exception as e:
        logger.error(f"Error deleting saved chat {filename}: {e}")
        return format_error_response(f"Error deleting saved chat: {str(e)}", 500)

@app.route('/api/chat/quick-queries', methods=['GET'])
def get_quick_queries():
    """Get predefined quick queries."""
    
    quick_queries = [
        {
            'id': 'miranda_rights',
            'title': 'Miranda Rights',
            'question': 'What are Miranda rights and when must they be read?',
            'category': 'Criminal Law',
            'icon': 'shield'
        },
        {
            'id': 'traffic_stops',
            'title': 'Traffic Stops',
            'question': 'What are the legal requirements for traffic stops in Wisconsin?',
            'category': 'Traffic Law',
            'icon': 'car'
        },
        {
            'id': 'search_warrants',
            'title': 'Search Warrants',
            'question': 'What are the requirements for obtaining and executing search warrants?',
            'category': 'Criminal Law',
            'icon': 'search'
        },
        {
            'id': 'use_of_force',
            'title': 'Use of Force',
            'question': 'What are the legal standards for use of force by law enforcement?',
            'category': 'Law Enforcement',
            'icon': 'alert-triangle'
        },
        {
            'id': 'evidence_admissibility',
            'title': 'Evidence Admissibility',
            'question': 'What are the rules for evidence admissibility in Wisconsin courts?',
            'category': 'Criminal Law',
            'icon': 'file-text'
        },
        {
            'id': 'juvenile_law',
            'title': 'Juvenile Law',
            'question': 'What are the special procedures for juvenile cases in Wisconsin?',
            'category': 'Juvenile Law',
            'icon': 'users'
        }
    ]
    
    return format_success_response({
        'queries': quick_queries,
        'total_queries': len(quick_queries)
    }, "Quick queries retrieved successfully")

def generate_report_content(history, include_sources=True):
    """Generate report content from chat history."""
    
    report_lines = []
    report_lines.append("WISCONSIN STATUTES CHAT REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    for i, exchange in enumerate(history, 1):
        report_lines.append(f"Exchange {i}:")
        report_lines.append(f"Question: {exchange.get('question', 'N/A')}")
        report_lines.append(f"Answer: {exchange.get('answer', 'N/A')}")
        
        if include_sources and 'sources' in exchange:
            report_lines.append("Sources:")
            for source in exchange['sources']:
                report_lines.append(f"  - {source.get('title', 'Unknown')} (Section: {source.get('section', 'Unknown')})")
        
        report_lines.append("")
    
    return "\n".join(report_lines)

@app.route('/api/chat/sources', methods=['POST'])
def get_chat_sources():
    """Get source documents for a specific question."""
    
    if not chatbot or not vector_db:
        return format_error_response("Chatbot or vector database not initialized", 500)
    
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return format_error_response("Question is required")
        
        question = data['question']
        jurisdiction = data.get('jurisdiction', 'federal')
        max_results = data.get('max_results', 5)
        
        # Use the RAG system to get relevant sources
        rag_response = chatbot.rag_system.ask_question(
            question=question,
            jurisdiction=jurisdiction,
            max_results=max_results
        )
        
        # Format source documents
        sources = []
        if 'source_documents' in rag_response:
            for i, doc in enumerate(rag_response['source_documents'], 1):
                source = {
                    'id': doc.get('id', f'source_{i}'),
                    'title': doc.get('file_name', 'Unknown Document'),
                    'type': doc.get('document_type', 'Unknown'),
                    'jurisdiction': doc.get('jurisdiction', 'Unknown'),
                    'status': doc.get('law_status', 'Unknown'),
                    'score': doc.get('relevance_score', 0.0),
                    'section': doc.get('section', 'Unknown'),
                    'citations': doc.get('citations', []),
                    'content_preview': doc.get('content_preview', ''),
                    'url': doc.get('url', '#'),
                    'source_number': i
                }
                sources.append(source)
        
        return format_success_response({
            'question': question,
            'sources': sources,
            'total_sources': len(sources),
            'search_quality': rag_response.get('search_quality', {})
        }, "Source documents retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting chat sources: {e}")
        return format_error_response(f"Error retrieving source documents: {str(e)}", 500)

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

@app.route('/api/cross-reference/find', methods=['POST'])
def find_cross_references():
    """Find cross-references for a document or query."""
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        content = data.get('content')
        query = data.get('query')
        threshold = data.get('threshold', 0.3)
        
        if not content and not query:
            return jsonify({'error': 'Either content or query must be provided'}), 400
        
        if content:
            # Find cross-references for document content
            cross_refs = cross_ref_system.find_cross_references(document_id, content, threshold)
        else:
            # Find suggestions based on query
            cross_refs = cross_ref_system.suggest_related_content(query, document_id)
        
        return jsonify({
            'success': True,
            'cross_references': cross_refs,
            'count': len(cross_refs)
        })
        
    except Exception as e:
        logger.error(f"Error finding cross-references: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cross-reference/related/<document_id>', methods=['GET'])
def get_related_documents(document_id):
    """Get related documents for a specific document."""
    try:
        max_results = request.args.get('max_results', 10, type=int)
        related_docs = cross_ref_system.get_related_documents(document_id, max_results)
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'related_documents': related_docs,
            'count': len(related_docs)
        })
        
    except Exception as e:
        logger.error(f"Error getting related documents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cross-reference/patterns', methods=['GET'])
def analyze_patterns():
    """Analyze patterns across all documents."""
    try:
        document_ids = request.args.get('document_ids')
        if document_ids:
            document_ids = document_ids.split(',')
        
        patterns = cross_ref_system.analyze_patterns(document_ids)
        
        return jsonify({
            'success': True,
            'patterns': patterns
        })
        
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cross-reference/relationship-map/<document_id>', methods=['GET'])
def generate_relationship_map(document_id):
    """Generate a relationship map for a document."""
    try:
        depth = request.args.get('depth', 2, type=int)
        relationship_map = cross_ref_system.generate_relationship_map(document_id, depth)
        
        return jsonify({
            'success': True,
            'relationship_map': relationship_map
        })
        
    except Exception as e:
        logger.error(f"Error generating relationship map: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cross-reference/suggestions', methods=['POST'])
def get_suggestions():
    """Get intelligent suggestions for related content."""
    try:
        data = request.get_json()
        query = data.get('query')
        document_id = data.get('document_id')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        suggestions = cross_ref_system.suggest_related_content(query, document_id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cross-reference/update', methods=['POST'])
def update_cross_references():
    """Update all cross-references in the system."""
    try:
        cross_ref_system.update_cross_references()
        
        return jsonify({
            'success': True,
            'message': 'Cross-references updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating cross-references: {e}")
        return jsonify({'error': str(e)}), 500

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
            debug=True,  # Keep debug mode for development
            threaded=True
        )
    else:
        logger.error("❌ Failed to initialize components. Exiting.")
        sys.exit(1)
