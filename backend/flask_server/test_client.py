#!/usr/bin/env python3
"""
Test Client for Flask Legal RAG Chatbot API

Demonstrates how to use the Flask API endpoints for:
1. Chatbot querying
2. Document upload and processing
3. Document search and management
"""

import requests
import json
import time
from typing import Dict, Any
import os

class LegalRAGAPIClient:
    """Client for the Legal RAG Flask API."""
    
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, question: str, jurisdiction: str = "federal", include_metadata: bool = True) -> Dict[str, Any]:
        """Send a chat message to the chatbot."""
        try:
            data = {
                "question": question,
                "jurisdiction": jurisdiction,
                "include_metadata": include_metadata
            }
            response = self.session.post(f"{self.base_url}/api/chat", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat_stream(self, question: str, jurisdiction: str = "federal", include_metadata: bool = True):
        """Stream a chat response from the chatbot."""
        try:
            data = {
                "question": question,
                "jurisdiction": jurisdiction,
                "include_metadata": include_metadata
            }
            response = self.session.post(f"{self.base_url}/api/chat/stream", json=data, stream=True)
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield {"type": "error", "response": {"error": str(e)}}
    
    def upload_document(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload and process a document."""
        try:
            if metadata is None:
                metadata = {}
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'document_type': metadata.get('document_type', 'Unknown'),
                    'jurisdiction': metadata.get('jurisdiction', 'federal'),
                    'law_status': metadata.get('law_status', 'current'),
                    'uploaded_by': metadata.get('uploaded_by', 'test_user')
                }
                
                response = self.session.post(f"{self.base_url}/api/documents/upload", files=files, data=data)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_documents(self, query: str, max_results: int = 10, jurisdiction: str = None, document_type: str = None) -> Dict[str, Any]:
        """Search documents in the database."""
        try:
            data = {
                "query": query,
                "max_results": max_results
            }
            if jurisdiction:
                data["jurisdiction"] = jurisdiction
            if document_type:
                data["document_type"] = document_type
            
            response = self.session.post(f"{self.base_url}/api/documents/search", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_documents(self) -> Dict[str, Any]:
        """List all documents in the database."""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/list")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the database."""
        try:
            response = self.session.delete(f"{self.base_url}/api/documents/{document_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_chat_history(self) -> Dict[str, Any]:
        """Get chat history."""
        try:
            response = self.session.get(f"{self.base_url}/api/chat/history")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_chat_history(self) -> Dict[str, Any]:
        """Clear chat history."""
        try:
            response = self.session.delete(f"{self.base_url}/api/chat/history")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a background processing task."""
        try:
            response = self.session.get(f"{self.base_url}/api/tasks/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_tasks(self) -> Dict[str, Any]:
        """List all background processing tasks."""
        try:
            response = self.session.get(f"{self.base_url}/api/tasks")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task from tracking."""
        try:
            response = self.session.delete(f"{self.base_url}/api/tasks/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_health_check(client: LegalRAGAPIClient):
    """Test health check endpoint."""
    print("🏥 Testing Health Check...")
    result = client.health_check()
    print(f"Health Check Result: {json.dumps(result, indent=2)}")
    print()

def test_chat(client: LegalRAGAPIClient):
    """Test chat endpoint."""
    print("💬 Testing Chat Endpoint...")
    
    questions = [
        "What does 18 U.S.C. 2703 say about digital evidence?",
        "What are the Fourth Amendment protections for digital privacy?",
        "What does Smith v. Maryland say about privacy?"
    ]
    
    for question in questions:
        print(f"❓ Question: {question}")
        result = client.chat(question)
        
        if result.get('status') == 'success':
            data = result['data']
            print(f"🤖 Answer: {data['answer'][:200]}...")
            print(f"🎯 Confidence: {data.get('confidence_score', 'N/A')}")
            print(f"📊 Model: {data.get('model_used', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        print("-" * 50)

def test_streaming_chat(client: LegalRAGAPIClient):
    """Test streaming chat endpoint."""
    print("📡 Testing Streaming Chat...")
    
    question = "What are the requirements for digital evidence collection?"
    print(f"❓ Question: {question}")
    print("🤖 Streaming Response:")
    
    full_response = ""
    for chunk in client.chat_stream(question):
        if chunk['type'] == 'content':
            content = chunk['content']
            print(content, end='', flush=True)
            full_response += content
        elif chunk['type'] == 'complete':
            print(f"\n\n✅ Streaming completed!")
            response_data = chunk['response']
            print(f"🎯 Confidence: {response_data.get('confidence_score', 'N/A')}")
            break
        elif chunk['type'] == 'error':
            print(f"\n❌ Error: {chunk['response'].get('error', 'Unknown error')}")
            break
    
    print("-" * 50)

def test_document_upload(client: LegalRAGAPIClient):
    """Test document upload endpoint with background processing."""
    print("📄 Testing Document Upload (Background Processing)...")
    
    # Create a sample text file for testing
    sample_content = """
    18 U.S.C. 2703 - Required disclosure of customer communications or records
    
    (a) Contents of wire or electronic communications in electronic storage
    
    A governmental entity may require the disclosure by a provider of electronic communication service of the contents of a wire or electronic communication, that is in electronic storage in an electronic communications system for one hundred and eighty days or less, only pursuant to a warrant issued using the procedures described in the Federal Rules of Criminal Procedure (or, in the case of a State court, issued using State warrant procedures) by a court of competent jurisdiction.
    
    (b) Contents of wire or electronic communications in a remote computing service
    
    A governmental entity may require a provider of remote computing service to disclose the contents of any wire or electronic communication to which this paragraph is made applicable by paragraph (2) of this subsection.
    """
    
    test_file_path = "test_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(sample_content)
    
    try:
        metadata = {
            'document_type': 'Federal Statute',
            'jurisdiction': 'federal',
            'law_status': 'current',
            'uploaded_by': 'test_user'
        }
        
        result = client.upload_document(test_file_path, metadata)
        
        if result.get('status') == 'success':
            data = result['data']
            task_id = data['task_id']
            print(f"✅ Document uploaded successfully!")
            print(f"📋 Task ID: {task_id}")
            print(f"📄 File: {data['metadata']['file_name']}")
            print(f"📊 Status: {data['status']}")
            print(f"💬 Message: {data['message']}")
            
            # Monitor task progress
            print("\n🔄 Monitoring task progress...")
            max_attempts = 30
            attempts = 0
            
            while attempts < max_attempts:
                time.sleep(1)
                attempts += 1
                
                task_result = client.get_task_status(task_id)
                if task_result.get('status') == 'success':
                    task_data = task_result['data']
                    print(f"   Progress: {task_data['progress']}% - {task_data['message']}")
                    
                    if task_data['status'] == 'completed':
                        print(f"✅ Processing completed!")
                        print(f"📊 Chunks created: {task_data['result']['chunks_created']}")
                        print(f"⏱️ Processing time: {task_data['result']['processing_time']} seconds")
                        break
                    elif task_data['status'] == 'failed':
                        print(f"❌ Processing failed: {task_data.get('error', 'Unknown error')}")
                        break
                else:
                    print(f"❌ Failed to get task status: {task_result.get('error')}")
                    break
        else:
            print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("-" * 50)

def test_document_search(client: LegalRAGAPIClient):
    """Test document search endpoint."""
    print("🔍 Testing Document Search...")
    
    queries = [
        "digital evidence",
        "privacy protection",
        "electronic communication"
    ]
    
    for query in queries:
        print(f"🔎 Search Query: {query}")
        result = client.search_documents(query, max_results=5)
        
        if result.get('status') == 'success':
            data = result['data']
            print(f"📊 Found {data['total_results']} results")
            
            for i, doc in enumerate(data['results'][:3], 1):
                print(f"   {i}. Score: {doc['score']:.3f}")
                print(f"      Content: {doc['content'][:100]}...")
                print(f"      Type: {doc['metadata'].get('document_type', 'Unknown')}")
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        print("-" * 30)

def test_document_management(client: LegalRAGAPIClient):
    """Test document management endpoints."""
    print("📚 Testing Document Management...")
    
    # List documents
    print("📋 Listing documents...")
    result = client.list_documents()
    
    if result.get('status') == 'success':
        data = result['data']
        print(f"📊 Total documents: {data['total_documents']}")
        
        for doc in data['documents'][:3]:
            print(f"   - {doc.get('file_name', 'Unknown')} ({doc.get('document_type', 'Unknown')})")
    else:
        print(f"❌ Failed to list documents: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)

def test_chat_history(client: LegalRAGAPIClient):
    """Test chat history endpoints."""
    print("💾 Testing Chat History...")
    
    # Get chat history
    result = client.get_chat_history()
    
    if result.get('status') == 'success':
        data = result['data']
        print(f"📊 Total exchanges: {data['total_exchanges']}")
        
        for i, exchange in enumerate(data['history'][:3], 1):
            print(f"   {i}. Q: {exchange['question'][:50]}...")
            print(f"      A: {exchange['answer'][:50]}...")
    else:
        print(f"❌ Failed to get history: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)

def test_system_stats(client: LegalRAGAPIClient):
    """Test system statistics endpoint."""
    print("📈 Testing System Statistics...")
    
    result = client.get_stats()
    
    if result.get('status') == 'success':
        data = result['data']
        print(f"🕒 Timestamp: {data['timestamp']}")
        print(f"🔧 Components:")
        for component, status in data['components'].items():
            print(f"   - {component}: {'✅' if status else '❌'}")
        
        if 'chatbot_stats' in data:
            chatbot_stats = data['chatbot_stats']
            print(f"🤖 Chatbot Stats:")
            print(f"   - Total conversations: {chatbot_stats.get('total_conversations', 0)}")
            print(f"   - Model: {chatbot_stats.get('model_used', 'N/A')}")
        
        if 'vector_db_stats' in data:
            vector_stats = data['vector_db_stats']
            if 'error' not in vector_stats:
                print(f"🗄️ Vector DB Stats:")
                print(f"   - Total documents: {vector_stats.get('total_documents', 0)}")
        
        if 'task_stats' in data:
            task_stats = data['task_stats']
            print(f"📋 Task Stats:")
            print(f"   - Total tasks: {task_stats.get('total_tasks', 0)}")
            for status, count in task_stats.get('tasks_by_status', {}).items():
                print(f"   - {status}: {count}")
    else:
        print(f"❌ Failed to get stats: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)

def test_task_management(client: LegalRAGAPIClient):
    """Test task management endpoints."""
    print("📋 Testing Task Management...")
    
    # List all tasks
    result = client.list_tasks()
    
    if result.get('status') == 'success':
        data = result['data']
        print(f"📊 Total tasks: {data['total_tasks']}")
        
        for task in data['tasks'][:3]:  # Show first 3 tasks
            print(f"   📋 Task {task['task_id'][:8]}...")
            print(f"      File: {task['file_name']}")
            print(f"      Status: {task['status']}")
            print(f"      Progress: {task['progress']}%")
            print(f"      Message: {task['message']}")
            print()
    else:
        print(f"❌ Failed to list tasks: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)

def main():
    """Run all tests."""
    import os
    
    print("🧪 Legal RAG API Test Client")
    print("=" * 50)
    
    # Initialize client
    client = LegalRAGAPIClient()
    
    # Run tests
    test_health_check(client)
    test_chat(client)
    test_streaming_chat(client)
    test_document_upload(client)
    test_task_management(client)
    test_document_search(client)
    test_document_management(client)
    test_chat_history(client)
    test_system_stats(client)
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
