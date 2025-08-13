#!/usr/bin/env python3
"""
LangChain Legal RAG Chatbot

A cost-effective RAG chatbot using LangChain with GPT-3.5-turbo for legal document Q&A.
Integrates with our advanced retrieval system for optimal performance.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import our advanced RAG system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag_system.advanced_rag_system import AdvancedLegalRAG
from vector_db.vector_database import LegalVectorDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangChainLegalRAGChatbot:
    """
    LangChain-based RAG chatbot for legal document Q&A.
    Uses GPT-3.5-turbo for cost efficiency and advanced retrieval system.
    
    Features:
    - Confidence scoring for responses
    - Outdated information flagging
    - Jurisdiction-specific warnings
    - Legal disclaimers
    - Use of force query handling
    - Source citations in all responses
    - Singleton pattern to prevent multiple initializations
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, **kwargs):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(LangChainLegalRAGChatbot, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 model: str = "gpt-3.5-turbo",
                 max_tokens: int = 1000,
                 temperature: float = 0.3,
                 streaming: bool = False):
        
        # Only initialize once
        if self._initialized:
            return
        """
        Initialize the LangChain RAG chatbot.
        
        Args:
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY in .env)
            model: OpenAI model to use (default: gpt-3.5-turbo for cost efficiency)
            max_tokens: Maximum tokens for response generation
            temperature: Response creativity (0.0 = focused, 1.0 = creative)
        """
        # Initialize OpenAI API key
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key,
            streaming=streaming
        )
        
        self.streaming = streaming
        
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize advanced RAG system
        try:
            vector_db = LegalVectorDatabase()
            self.rag_system = AdvancedLegalRAG(vector_db)
            logger.info("Advanced RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
        
        # Conversation history
        self.conversation_history = []
        
        # Safety and accuracy features
        self.confidence_threshold = 0.7
        self.use_of_force_keywords = [
            'use of force', 'deadly force', 'lethal force', 'shooting', 'firearm',
            'weapon', 'assault', 'battery', 'self-defense', 'defense of others',
            'reasonable force', 'excessive force', 'police shooting', 'officer involved'
        ]
        
        # Create LangChain prompt templates
        self.prompt_templates = self._create_prompt_templates()
        
        # Create LangChain chains
        self.chains = self._create_chains()
        
        # Mark as initialized
        self._initialized = True
    
    def _create_prompt_templates(self) -> Dict[str, ChatPromptTemplate]:
        """Create LangChain prompt templates for different use cases."""
        
        # Main legal Q&A prompt with safety features
        legal_qa_template = ChatPromptTemplate.from_messages([
            ("system", """You are a knowledgeable legal research assistant specializing in U.S. law, particularly digital evidence, privacy law, and criminal procedure.

Your task is to provide accurate, helpful answers based on the provided legal context. Follow these guidelines:

1. **Answer Accuracy**: Base your response primarily on the provided legal context
2. **Legal Citations**: Include relevant statute numbers, case names, and citations when mentioned
3. **Clarity**: Explain legal concepts in clear, understandable terms
4. **Completeness**: Provide comprehensive answers while staying within context
5. **Professional Tone**: Maintain a professional, authoritative tone appropriate for legal research
6. **Limitations**: If the context doesn't contain sufficient information, acknowledge this clearly

**SAFETY AND ACCURACY REQUIREMENTS:**
- **Source Citations**: Always include specific legal authorities and citations
- **Jurisdiction Warnings**: Flag if information is jurisdiction-specific
- **Outdated Information**: Warn if legal information may be outdated
- **Use of Force Care**: Handle use of force queries with extreme care and appropriate warnings

**RESPONSE FORMAT:**
1. Main answer with citations
2. Jurisdiction and currency warnings (if applicable)
3. Additional safety notes (if use of force related)

Legal Context:
{context}

Search Quality Metrics:
{search_metrics}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Citation-focused prompt with safety features
        citation_template = ChatPromptTemplate.from_messages([
            ("system", """You are a legal citation expert. Based on the provided legal context, identify and explain the key legal authorities, statutes, and cases.

Focus on:
1. **Statute Numbers**: Identify specific legal codes and sections
2. **Case Names**: Highlight relevant court decisions
3. **Legal Relationships**: Explain how different authorities relate to each other
4. **Jurisdiction**: Clarify federal vs. state authority where relevant

**SAFETY AND ACCURACY REQUIREMENTS:**
- **Source Citations**: Always include specific legal authorities and citations
- **Jurisdiction Warnings**: Flag if information is jurisdiction-specific
- **Outdated Information**: Warn if legal information may be outdated

**RESPONSE FORMAT:**
1. Citation analysis with specific authorities
2. Jurisdiction and currency warnings (if applicable)

Legal Context:
{context}

Search Quality Metrics:
{search_metrics}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Follow-up prompt with safety features
        follow_up_template = ChatPromptTemplate.from_messages([
            ("system", """You are continuing a legal research conversation. Consider the previous context and provide a coherent response that builds on earlier information.

**SAFETY AND ACCURACY REQUIREMENTS:**
- **Source Citations**: Always include specific legal authorities and citations
- **Jurisdiction Warnings**: Flag if information is jurisdiction-specific
- **Outdated Information**: Warn if legal information may be outdated

**RESPONSE FORMAT:**
1. Main answer with citations
2. Jurisdiction and currency warnings (if applicable)

Legal Context:
{context}

Search Quality Metrics:
{search_metrics}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        return {
            'legal_qa': legal_qa_template,
            'citation_summary': citation_template,
            'follow_up': follow_up_template
        }
    
    def _create_chains(self) -> Dict[str, Any]:
        """Create LangChain chains for different prompt types."""
        
        chains = {}
        
        for prompt_type, template in self.prompt_templates.items():
            chain = (
                {
                    "context": lambda x: x["context"],
                    "search_metrics": lambda x: x["search_metrics"],
                    "chat_history": lambda x: x["chat_history"],
                    "question": lambda x: x["question"]
                }
                | template
                | self.llm
                | StrOutputParser()
            )
            chains[prompt_type] = chain
        
        return chains
    
    def _determine_prompt_type(self, question: str) -> str:
        """Determine which prompt template to use based on the question."""
        question_lower = question.lower()
        
        # Citation-focused questions
        citation_keywords = ['cite', 'citation', 'statute', 'case', 'authority', 'legal basis', 'what law', 'which law']
        if any(keyword in question_lower for keyword in citation_keywords):
            return 'citation_summary'
        
        # Follow-up questions
        follow_up_keywords = ['also', 'additionally', 'furthermore', 'moreover', 'what about', 'how about', 'and', 'but']
        if any(keyword in question_lower for keyword in follow_up_keywords) and self.conversation_history:
            return 'follow_up'
        
        # Default to general legal Q&A
        return 'legal_qa'
    
    def _build_context_for_llm(self, rag_response: Dict[str, Any]) -> str:
        """Build optimized context for the LLM from RAG results."""
        
        context_parts = []
        
        # Add search results with relevance scores
        for i, result in enumerate(rag_response['search_results'][:3], 1):  # Top 3 results
            context_parts.append(f"Source {i} (Relevance: {result.score:.3f}):")
            context_parts.append(f"Document Type: {result.document_type}")
            context_parts.append(f"Jurisdiction: {result.jurisdiction}")
            context_parts.append(f"Law Status: {result.law_status}")
            context_parts.append(f"Content: {result.content}")
            
            if result.citation_chain:
                context_parts.append(f"Citations: {', '.join(result.citation_chain)}")
            context_parts.append("")  # Empty line for separation
        
        # Add citation chain summary
        if rag_response['citation_chain']:
            context_parts.append("Related Legal Authorities:")
            for citation in rag_response['citation_chain'][:5]:  # Top 5 citations
                context_parts.append(f"- {citation}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_search_metrics(self, rag_response: Dict[str, Any]) -> str:
        """Build search quality metrics for the LLM."""
        
        metrics_parts = []
        metrics_parts.append("Search Quality Metrics:")
        
        for factor, score in rag_response['relevance_breakdown'].items():
            metrics_parts.append(f"- {factor}: {score:.3f}")
        
        metrics_parts.append(f"- Top Score: {rag_response['top_score']:.3f}")
        metrics_parts.append(f"- Total Results: {rag_response['total_results']}")
        
        return "\n".join(metrics_parts)
    
    def _extract_source_documents(self, rag_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and format source documents information."""
        
        source_documents = []
        
        for i, result in enumerate(rag_response['search_results'][:5], 1):  # Top 5 results
            # Extract file name from metadata
            metadata = getattr(result, 'metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            
            # If file_name is still Unknown, try other metadata fields
            if file_name == 'Unknown':
                # Try different possible metadata fields for file name
                file_name = (
                    metadata.get('original_file_name') or
                    metadata.get('document_name') or
                    metadata.get('title') or
                    metadata.get('module_title') or
                    'Unknown'
                )
            
            # Extract section information with better detection
            section = 'Unknown'
            
            # First priority: Use section information from document processing
            if metadata.get('section_number'):
                section = metadata.get('section_number')
            elif metadata.get('section_title'):
                section = metadata.get('section_title')
            elif metadata.get('section_type'):
                section = metadata.get('section_type')
            else:
                # Fallback: Try to extract section from content
                content = result.content[:200]  # Look at first 200 chars for better coverage
                import re
                
                # Look for statute numbers like "1.04", "1.05", etc.
                # Find ALL statute numbers in the content
                statute_matches = re.findall(r'(\d+\.\d+[A-Z]*)', content)
                
                if statute_matches:
                    # If multiple statute numbers found, try to determine the most relevant one
                    if len(statute_matches) > 1:
                        # Look for the statute number that appears at the beginning of a sentence or line
                        # This is more likely to be the main section being discussed
                        for match in statute_matches:
                            # Check if this statute number appears at the start of a sentence or line
                            if re.search(rf'^\s*{re.escape(match)}|\.\s*{re.escape(match)}|\(\d+\)\s*{re.escape(match)}', content):
                                section = match
                                break
                        else:
                            # If no clear pattern, use the first one
                            section = statute_matches[0]
                    else:
                        # Only one statute number found
                        section = statute_matches[0]
                else:
                    # Fallback to chapter patterns
                    chapter_match = re.search(r'CHAPTER\s+(\d+[A-Z]*)', content, re.IGNORECASE)
                    section_match = re.search(r'SECTION\s+(\d+\.\d+)', content, re.IGNORECASE)
                    if chapter_match:
                        section = f"CHAPTER {chapter_match.group(1)}"
                    elif section_match:
                        section = f"Section {section_match.group(1)}"
            
            # Determine jurisdiction with better detection
            jurisdiction = getattr(result, 'jurisdiction', 'Unknown')
            if jurisdiction == 'Unknown' or jurisdiction == 'federal':
                # Check content for Wisconsin indicators
                content_lower = result.content.lower()
                if any(wisconsin_indicator in content_lower for wisconsin_indicator in [
                    'wisconsin', 'state of wisconsin', 'wi statutes', 'wisconsin statutes',
                    'state sovereignty', 'state jurisdiction'
                ]):
                    jurisdiction = 'state'
                elif any(federal_indicator in content_lower for federal_indicator in [
                    'united states', 'u.s.', 'federal', 'congress', 'supreme court'
                ]):
                    jurisdiction = 'federal'
            
            doc_info = {
                'source_number': i,
                'relevance_score': result.score,
                'document_type': getattr(result, 'document_type', 'Unknown'),
                'jurisdiction': jurisdiction,
                'law_status': getattr(result, 'law_status', 'Unknown'),
                'content_preview': result.content[:200] + "..." if len(result.content) > 200 else result.content,
                'citations': getattr(result, 'citation_chain', []),
                'dates': metadata.get('dates', []),
                'file_name': file_name,
                'original_file_name': metadata.get('original_file_name', file_name),  # Add original filename for download
                'module_title': metadata.get('module_title', 'Unknown'),
                'section': section
            }
            source_documents.append(doc_info)
        
        return source_documents
    
    def _build_chat_history(self) -> List[Any]:
        """Build chat history for LangChain."""
        
        history = []
        for exchange in self.conversation_history[-6:]:  # Last 6 exchanges
            history.append(HumanMessage(content=exchange['question']))
            history.append(AIMessage(content=exchange['answer']))
        
        return history
    
    def _detect_use_of_force_query(self, question: str) -> bool:
        """Detect if the question is related to use of force."""
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in self.use_of_force_keywords)
    
    def _calculate_confidence_score(self, rag_response: Dict[str, Any]) -> float:
        """Calculate confidence score based on search quality."""
        
        # Base confidence on top score
        base_confidence = min(rag_response['top_score'], 1.0)
        
        # Adjust based on number of results
        if rag_response['total_results'] >= 5:
            base_confidence *= 1.1  # Bonus for many results
        elif rag_response['total_results'] < 2:
            base_confidence *= 0.8  # Penalty for few results
        
        # Adjust based on relevance breakdown
        relevance_scores = rag_response['relevance_breakdown']
        
        # Bonus for high semantic similarity
        if relevance_scores.get('semantic_similarity', 0) > 0.8:
            base_confidence *= 1.05
        
        # Bonus for high keyword matching
        if relevance_scores.get('keyword_matching', 0) > 0.8:
            base_confidence *= 1.05
        
        # Penalty for low citation relevance
        if relevance_scores.get('citation_relevance', 0) < 0.5:
            base_confidence *= 0.9
        
        return min(base_confidence, 1.0)
    
    def _check_jurisdiction_specific(self, rag_response: Dict[str, Any]) -> bool:
        """Check if the response is jurisdiction-specific."""
        
        # Check if any results are state-specific
        for result in rag_response['search_results']:
            if result.jurisdiction and result.jurisdiction.lower() != 'federal':
                return True
        
        return False
    
    def _check_outdated_information(self, rag_response: Dict[str, Any]) -> bool:
        """Check if information might be outdated."""
        
        # Check for old dates in results
        current_year = datetime.now().year
        
        for result in rag_response['search_results']:
            if hasattr(result, 'dates') and result.dates:
                for date_str in result.dates:
                    try:
                        # Extract year from date string
                        if '-' in date_str:
                            year = int(date_str.split('-')[0])
                        else:
                            year = int(date_str)
                        
                        # Flag if older than 10 years
                        if current_year - year > 10:
                            return True
                    except (ValueError, IndexError):
                        continue
        
        return False
    
    def _generate_safety_warnings(self, 
                                 question: str, 
                                 rag_response: Dict[str, Any],
                                 confidence_score: float) -> Dict[str, Any]:
        """Generate safety warnings and disclaimers."""
        
        warnings = {
            'use_of_force_warning': False,
            'jurisdiction_warning': False,
            'outdated_warning': False,
            'low_confidence_warning': False,
            'legal_disclaimer': False  # Disabled for law enforcement use
        }
        
        # Check for use of force queries
        if self._detect_use_of_force_query(question):
            warnings['use_of_force_warning'] = True
        
        # Check for jurisdiction-specific information
        if self._check_jurisdiction_specific(rag_response):
            warnings['jurisdiction_warning'] = True
        
        # Check for outdated information
        if self._check_outdated_information(rag_response):
            warnings['outdated_warning'] = True
        
        # Check for low confidence
        if confidence_score < self.confidence_threshold:
            warnings['low_confidence_warning'] = True
        
        return warnings
    
    def ask(self, 
            question: str, 
            jurisdiction: str = "federal",
            include_metadata: bool = True) -> Dict[str, Any]:
        """
        Ask a question and get a comprehensive RAG response using LangChain.
        
        Args:
            question: The legal question to ask
            jurisdiction: Target jurisdiction (federal/state)
            include_metadata: Whether to include search metadata in response
            
        Returns:
            Dictionary containing the answer and metadata
        """
        
        try:
            # Step 1: Perform advanced RAG retrieval
            logger.info(f"Processing question: {question}")
            rag_response = self.rag_system.ask_question(
                question, 
                jurisdiction=jurisdiction, 
                max_results=5
            )
            
            # Step 2: Build context and metrics
            context = self._build_context_for_llm(rag_response)
            search_metrics = self._build_search_metrics(rag_response)
            chat_history = self._build_chat_history()
            
            # Step 3: Calculate confidence and safety features
            confidence_score = self._calculate_confidence_score(rag_response)
            safety_warnings = self._generate_safety_warnings(question, rag_response, confidence_score)
            
            # Step 4: Determine prompt type
            prompt_type = self._determine_prompt_type(question)
            
            # Step 5: Generate response using LangChain
            logger.info(f"Generating response using {self.model} with {prompt_type} prompt")
            logger.info(f"Confidence score: {confidence_score:.3f}")
            logger.info(f"Safety warnings: {safety_warnings}")
            
            chain = self.chains[prompt_type]
            answer = chain.invoke({
                "context": context,
                "search_metrics": search_metrics,
                "chat_history": chat_history,
                "question": question
            })
            
            # Step 6: Prepare response with safety features
            response = {
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'prompt_type': prompt_type,
                'confidence_score': confidence_score,
                'safety_warnings': safety_warnings
            }
            
            # Add metadata if requested
            if include_metadata:
                response['metadata'] = {
                    'search_quality': {
                        'top_score': rag_response['top_score'],
                        'total_results': rag_response['total_results'],
                        'relevance_breakdown': rag_response['relevance_breakdown']
                    },
                    'citations_found': rag_response['citation_chain'],
                    'context_length': len(context),
                    'jurisdiction': rag_response['jurisdiction'],
                    'langchain_components': {
                        'prompt_type': prompt_type,
                        'chat_history_length': len(chat_history)
                    },
                    'safety_features': {
                        'confidence_score': confidence_score,
                        'confidence_threshold': self.confidence_threshold,
                        'safety_warnings': safety_warnings,
                        'use_of_force_detected': safety_warnings['use_of_force_warning'],
                        'jurisdiction_specific': safety_warnings['jurisdiction_warning'],
                        'potentially_outdated': safety_warnings['outdated_warning'],
                        'low_confidence': safety_warnings['low_confidence_warning']
                    }
                }
            
            # Step 6: Update conversation history
            self.conversation_history.append({
                'question': question,
                'answer': answer,
                'context': context,
                'timestamp': response['timestamp']
            })
            
            # Keep only last 10 conversations to manage context
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            return {
                'question': question,
                'answer': f"I apologize, but I encountered an error while processing your question. Please try again. Error: {str(e)}",
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'prompt_type': 'error',
                'confidence_score': 0.0,
                'safety_warnings': {
                    'use_of_force_warning': False,
                    'jurisdiction_warning': False,
                    'outdated_warning': False,
                    'low_confidence_warning': True,
                    'legal_disclaimer': True
                }
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_conversations': len(self.conversation_history),
            'model_used': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'langchain_components': list(self.chains.keys())
        }
    
    def ask_streaming(self, 
                     question: str, 
                     jurisdiction: str = "federal",
                     include_metadata: bool = True):
        """
        Ask a question and get a streaming response.
        
        Args:
            question: The legal question to ask
            jurisdiction: Target jurisdiction (federal/state)
            include_metadata: Whether to include search metadata in response
            
        Yields:
            Streaming response chunks
        """
        
        try:
            # Step 1: Perform advanced RAG retrieval
            logger.info(f"Processing streaming question: {question}")
            rag_response = self.rag_system.ask_question(
                question, 
                jurisdiction=jurisdiction, 
                max_results=5
            )
            
            # Step 2: Build context and metrics
            context = self._build_context_for_llm(rag_response)
            search_metrics = self._build_search_metrics(rag_response)
            chat_history = self._build_chat_history()
            
            # Step 3: Calculate confidence and safety features
            confidence_score = self._calculate_confidence_score(rag_response)
            safety_warnings = self._generate_safety_warnings(question, rag_response, confidence_score)
            
            # Step 4: Determine prompt type
            prompt_type = self._determine_prompt_type(question)
            
            # Step 5: Generate streaming response using LangChain
            logger.info(f"Generating streaming response using {self.model} with {prompt_type} prompt")
            
            chain = self.chains[prompt_type]
            
            # Create streaming chain
            streaming_chain = (
                {
                    "context": lambda x: x["context"],
                    "search_metrics": lambda x: x["search_metrics"],
                    "chat_history": lambda x: x["chat_history"],
                    "question": lambda x: x["question"]
                }
                | self.prompt_templates[prompt_type]
                | self.llm
            )
            
            # Stream the response
            full_answer = ""
            for chunk in streaming_chain.stream({
                "context": context,
                "search_metrics": search_metrics,
                "chat_history": chat_history,
                "question": question
            }):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    full_answer += content
                    yield {
                        'type': 'content',
                        'content': content,
                        'full_answer': full_answer
                    }
            
            # Step 6: Prepare final response
            response = {
                'question': question,
                'answer': full_answer,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'prompt_type': prompt_type,
                'confidence_score': confidence_score,
                'safety_warnings': safety_warnings
            }
            
            # Add metadata if requested
            if include_metadata:
                # Extract source documents
                source_documents = self._extract_source_documents(rag_response)
                
                response['metadata'] = {
                    'search_quality': {
                        'top_score': rag_response['top_score'],
                        'total_results': rag_response['total_results'],
                        'relevance_breakdown': rag_response['relevance_breakdown']
                    },
                    'citations_found': rag_response['citation_chain'],
                    'context_length': len(context),
                    'jurisdiction': rag_response['jurisdiction'],
                    'source_documents': source_documents,  # Add source documents
                    'langchain_components': {
                        'prompt_type': prompt_type,
                        'chat_history_length': len(chat_history)
                    },
                    'safety_features': {
                        'confidence_score': confidence_score,
                        'confidence_threshold': self.confidence_threshold,
                        'safety_warnings': safety_warnings,
                        'use_of_force_detected': safety_warnings['use_of_force_warning'],
                        'jurisdiction_specific': safety_warnings['jurisdiction_warning'],
                        'potentially_outdated': safety_warnings['outdated_warning'],
                        'low_confidence': safety_warnings['low_confidence_warning']
                    }
                }
            
            # Step 7: Update conversation history
            self.conversation_history.append({
                'question': question,
                'answer': full_answer,
                'context': context,
                'timestamp': response['timestamp']
            })
            
            # Keep only last 10 conversations to manage context
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Yield final response
            yield {
                'type': 'complete',
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Error in streaming ask method: {e}")
            error_response = {
                'question': question,
                'answer': f"I apologize, but I encountered an error while processing your question. Please try again. Error: {str(e)}",
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'prompt_type': 'error',
                'confidence_score': 0.0,
                'safety_warnings': {
                    'use_of_force_warning': False,
                    'jurisdiction_warning': False,
                    'outdated_warning': False,
                    'low_confidence_warning': True,
                    'legal_disclaimer': True
                }
            }
            yield {
                'type': 'error',
                'response': error_response
            }

def format_langchain_response(response: Dict[str, Any]) -> str:
    """Format LangChain chatbot response for display."""
    
    output_parts = []
    
    # Main answer
    output_parts.append(f"🤖 **Answer:**")
    output_parts.append(response['answer'])
    output_parts.append("")
    
    # Safety and accuracy features
    if 'confidence_score' in response:
        confidence = response['confidence_score']
        output_parts.append("🎯 **Confidence Assessment:**")
        if confidence >= 0.8:
            output_parts.append(f"   ✅ High Confidence: {confidence:.1%}")
        elif confidence >= 0.6:
            output_parts.append(f"   ⚠️  Moderate Confidence: {confidence:.1%}")
        else:
            output_parts.append(f"   ❌ Low Confidence: {confidence:.1%}")
        output_parts.append("")
    
    # Safety warnings
    if 'safety_warnings' in response:
        warnings = response['safety_warnings']
        output_parts.append("⚠️ **Safety Warnings:**")
        
        if warnings.get('use_of_force_warning'):
            output_parts.append("   🔴 USE OF FORCE QUERY: This response involves use of force considerations.")
            output_parts.append("      Please consult with qualified legal counsel for specific guidance.")
        
        if warnings.get('jurisdiction_warning'):
            output_parts.append("   🟡 JURISDICTION-SPECIFIC: This information may be jurisdiction-specific.")
            output_parts.append("      Verify applicability to your jurisdiction.")
        
        if warnings.get('outdated_warning'):
            output_parts.append("   🟠 POTENTIALLY OUTDATED: This information may be outdated.")
            output_parts.append("      Verify current legal status.")
        
        if warnings.get('low_confidence_warning'):
            output_parts.append("   🔴 LOW CONFIDENCE: Limited information available.")
            output_parts.append("      Consider consulting additional sources.")
        
        if warnings.get('legal_disclaimer'):
            output_parts.append("   📋 LEGAL DISCLAIMER: This is informational only, not legal advice.")
            output_parts.append("      Consult qualified legal counsel for specific legal matters.")
        
        output_parts.append("")
    
    # Metadata if available
    if 'metadata' in response:
        metadata = response['metadata']
        
        output_parts.append("📊 **Search Quality:**")
        output_parts.append(f"   Top Score: {metadata['search_quality']['top_score']:.3f}")
        output_parts.append(f"   Results Found: {metadata['search_quality']['total_results']}")
        output_parts.append("")
        
        if metadata['citations_found']:
            output_parts.append("⚖️ **Legal Authorities Found:**")
            for citation in metadata['citations_found'][:5]:
                output_parts.append(f"   - {citation}")
            output_parts.append("")
        
        # Source documents
        if 'source_documents' in metadata and metadata['source_documents']:
            output_parts.append("📄 **Source Documents Used:**")
            for doc in metadata['source_documents'][:3]:  # Show top 3 documents
                output_parts.append(f"   📋 Source {doc['source_number']} (Score: {doc['relevance_score']:.3f}):")
                output_parts.append(f"      Type: {doc['document_type']}")
                output_parts.append(f"      Jurisdiction: {doc['jurisdiction']}")
                output_parts.append(f"      Status: {doc['law_status']}")
                if doc['file_name'] != 'Unknown':
                    output_parts.append(f"      File: {doc['file_name']}")
                if doc['section'] != 'Unknown':
                    output_parts.append(f"      Section: {doc['section']}")
                if doc['citations']:
                    output_parts.append(f"      Citations: {', '.join(doc['citations'][:3])}")
                output_parts.append(f"      Preview: {doc['content_preview']}")
                output_parts.append("")
            output_parts.append("")
        
        output_parts.append("📈 **Relevance Breakdown:**")
        for factor, score in metadata['search_quality']['relevance_breakdown'].items():
            output_parts.append(f"   {factor}: {score:.3f}")
        output_parts.append("")
        
        # LangChain specific info
        if 'langchain_components' in metadata:
            langchain_info = metadata['langchain_components']
            output_parts.append("🔗 **LangChain Info:**")
            output_parts.append(f"   Prompt Type: {langchain_info['prompt_type']}")
            output_parts.append(f"   Chat History Length: {langchain_info['chat_history_length']}")
            output_parts.append("")
        
        # Safety features info
        if 'safety_features' in metadata:
            safety_info = metadata['safety_features']
            output_parts.append("🛡️ **Safety Features:**")
            output_parts.append(f"   Confidence Score: {safety_info['confidence_score']:.3f}")
            output_parts.append(f"   Use of Force Detected: {'Yes' if safety_info['use_of_force_detected'] else 'No'}")
            output_parts.append(f"   Jurisdiction Specific: {'Yes' if safety_info['jurisdiction_specific'] else 'No'}")
            output_parts.append(f"   Potentially Outdated: {'Yes' if safety_info['potentially_outdated'] else 'No'}")
            output_parts.append(f"   Low Confidence: {'Yes' if safety_info['low_confidence'] else 'No'}")
            output_parts.append("")
    
    # Technical info
    output_parts.append("🔧 **Technical Info:**")
    output_parts.append(f"   Model: {response['model_used']}")
    output_parts.append(f"   Framework: LangChain")
    output_parts.append(f"   Timestamp: {response['timestamp']}")
    
    return "\n".join(output_parts)

# Example usage and testing
if __name__ == "__main__":
    # Test the LangChain chatbot
    try:
        print("🤖 Initializing LangChain Legal RAG Chatbot...")
        chatbot = LangChainLegalRAGChatbot(
            model="gpt-3.5-turbo",
            max_tokens=800,
            temperature=0.3
        )
        
        print("✅ LangChain chatbot initialized successfully!")
        print(f"📊 Model: {chatbot.model}")
        print(f"💰 Cost-effective: Using GPT-3.5-turbo with LangChain")
        print(f"🔗 LangChain Components: {list(chatbot.chains.keys())}")
        print("=" * 60)
        
        # Test questions including safety scenarios
        test_questions = [
            "What does 18 U.S.C. 2703 say about digital evidence?",
            "What are the Fourth Amendment protections for digital privacy?",
            "What does Smith v. Maryland say about privacy?",
            "What are the requirements for digital evidence collection?",
            "What are the legal requirements for use of force in self-defense?",
            "What training is available for digital forensics?",
            "What are the DOJ policies on evidence preservation?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            print("-" * 40)
            
            response = chatbot.ask(question, include_metadata=True)
            formatted_response = format_langchain_response(response)
            print(formatted_response)
            
            print("\n" + "=" * 60)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set OPENAI_API_KEY in your .env file")
