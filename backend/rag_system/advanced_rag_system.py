#!/usr/bin/env python3
"""
Advanced Legal RAG System

Features:
1. Hybrid Search Implementation
   - Combine semantic search with keyword matching for statute numbers/case names
   - Implement relevance scoring that prioritizes current vs. superseded laws, state vs. federal jurisdiction, department-specific vs. general policies

2. Context Window Management
   - Design a system to handle related statutes and cross-references
   - Implement citation chain following (e.g., "see also § 940.01")
   - Manage context limits while preserving legal completeness

3. Query Enhancement
   - Build query expansion for legal synonyms and related terms
   - Handle common law enforcement abbreviations and terminology
   - Implement spell correction for legal terms
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import difflib

# Vector database imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from vector_db.vector_database import LegalVectorDatabase
from document_processing.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Enhanced search result with relevance scoring."""
    content: str
    score: float
    metadata: Dict[str, Any]
    relevance_factors: Dict[str, float]
    citation_chain: List[str]
    jurisdiction: str
    law_status: str  # 'current', 'superseded', 'pending'
    document_type: str

@dataclass
class QueryEnhancement:
    """Enhanced query with expansions and corrections."""
    original_query: str
    expanded_terms: List[str]
    legal_synonyms: List[str]
    corrected_terms: List[str]
    abbreviations: Dict[str, str]
    enhanced_query: str

class LegalQueryEnhancer:
    """Handles query enhancement for legal terminology."""
    
    def __init__(self):
        # Legal synonyms and related terms
        self.legal_synonyms = {
            'search': ['search', 'seizure', 'inspection', 'examination', 'investigation'],
            'warrant': ['warrant', 'court order', 'judicial authorization', 'search warrant'],
            'evidence': ['evidence', 'proof', 'testimony', 'documentation', 'exhibit'],
            'privacy': ['privacy', 'confidentiality', 'secrecy', 'protection', 'right to privacy'],
            'digital': ['digital', 'electronic', 'computer', 'online', 'cyber', 'virtual'],
            'amendment': ['amendment', 'constitutional right', 'bill of rights'],
            'statute': ['statute', 'law', 'code', 'regulation', 'ordinance'],
            'case': ['case', 'decision', 'ruling', 'opinion', 'precedent'],
            'court': ['court', 'tribunal', 'judiciary', 'bench'],
            'law enforcement': ['law enforcement', 'police', 'officer', 'detective', 'investigator'],
            'criminal': ['criminal', 'felony', 'misdemeanor', 'offense', 'crime'],
            'civil': ['civil', 'civilian', 'private', 'non-criminal'],
            'federal': ['federal', 'national', 'U.S.', 'United States'],
            'state': ['state', 'local', 'municipal', 'county'],
            'supreme court': ['supreme court', 'SCOTUS', 'U.S. Supreme Court'],
            'appeals court': ['appeals court', 'circuit court', 'appellate court'],
            'district court': ['district court', 'trial court', 'federal district court']
        }
        
        # Law enforcement abbreviations
        self.abbreviations = {
            'LEO': 'Law Enforcement Officer',
            'DOJ': 'Department of Justice',
            'FBI': 'Federal Bureau of Investigation',
            'DEA': 'Drug Enforcement Administration',
            'ATF': 'Bureau of Alcohol, Tobacco, Firearms and Explosives',
            'ICE': 'Immigration and Customs Enforcement',
            'DHS': 'Department of Homeland Security',
            'USC': 'United States Code',
            'CFR': 'Code of Federal Regulations',
            'SCOTUS': 'Supreme Court of the United States',
            'F.R.C.P.': 'Federal Rules of Civil Procedure',
            'F.R.Cr.P.': 'Federal Rules of Criminal Procedure',
            'F.R.E.': 'Federal Rules of Evidence',
            '4th Am.': 'Fourth Amendment',
            '5th Am.': 'Fifth Amendment',
            '6th Am.': 'Sixth Amendment',
            '8th Am.': 'Eighth Amendment',
            '14th Am.': 'Fourteenth Amendment',
            'v.': 'versus',
            'et al.': 'and others',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'cf.': 'compare',
            'see also': 'see also',
            'supra': 'above',
            'infra': 'below'
        }
        
        # Common legal misspellings
        self.spell_corrections = {
            'amendmant': 'amendment',
            'ammendment': 'amendment',
            'constititional': 'constitutional',
            'constituional': 'constitutional',
            'jurisdiciton': 'jurisdiction',
            'jurisdicition': 'jurisdiction',
            'statutue': 'statute',
            'statutte': 'statute',
            'warrrant': 'warrant',
            'warrantt': 'warrant',
            'evidance': 'evidence',
            'evidense': 'evidence',
            'privacey': 'privacy',
            'privicy': 'privacy',
            'digitial': 'digital',
            'digtial': 'digital',
            'enforcment': 'enforcement',
            'enforcemnt': 'enforcement',
            'investigation': 'investigation',
            'investigaton': 'investigation',
            'criminial': 'criminal',
            'crimnal': 'criminal',
            'federral': 'federal',
            'fedral': 'federal',
            'supreem': 'supreme',
            'supreme': 'supreme',
            'appelate': 'appellate',
            'appellate': 'appellate',
            'distric': 'district',
            'distrct': 'district'
        }
    
    def expand_query(self, query: str) -> QueryEnhancement:
        """Enhance query with legal synonyms, abbreviations, and corrections."""
        
        # Convert to lowercase for processing
        original_query = query
        query_lower = query.lower()
        
        # Expand abbreviations
        expanded_query = query
        abbreviations_found = {}
        for abbr, full_form in self.abbreviations.items():
            if abbr.lower() in query_lower:
                expanded_query = re.sub(rf'\b{re.escape(abbr)}\b', full_form, expanded_query, flags=re.IGNORECASE)
                abbreviations_found[abbr] = full_form
        
        # Correct common misspellings
        corrected_terms = []
        for misspelling, correction in self.spell_corrections.items():
            if misspelling in query_lower:
                expanded_query = re.sub(rf'\b{re.escape(misspelling)}\b', correction, expanded_query, flags=re.IGNORECASE)
                corrected_terms.append(f"{misspelling} -> {correction}")
        
        # Find legal synonyms
        legal_synonyms = []
        expanded_terms = []
        
        for term, synonyms in self.legal_synonyms.items():
            if term in query_lower:
                legal_synonyms.extend(synonyms)
                # Add synonyms to expanded query
                for synonym in synonyms[:2]:  # Limit to 2 synonyms per term
                    if synonym not in query_lower:
                        expanded_terms.append(synonym)
        
        # Create enhanced query
        enhanced_query = expanded_query
        if expanded_terms:
            enhanced_query += " " + " ".join(expanded_terms[:5])  # Limit to 5 additional terms
        
        return QueryEnhancement(
            original_query=original_query,
            expanded_terms=expanded_terms,
            legal_synonyms=legal_synonyms,
            corrected_terms=corrected_terms,
            abbreviations=abbreviations_found,
            enhanced_query=enhanced_query
        )

class CitationChainManager:
    """Manages citation chains and cross-references."""
    
    def __init__(self):
        # Patterns for finding citations
        self.citation_patterns = [
            r'see also § (\d+\.\d+)',  # "see also § 940.01"
            r'see § (\d+\.\d+)',       # "see § 940.01"
            r'cf\. § (\d+\.\d+)',      # "cf. § 940.01"
            r'(\d+\.\d+[A-Z]*)',       # Statute numbers like "1.1A"
            r'(\d+\s+U\.S\.C\.\s+\d+)', # "18 U.S.C. 2703"
            r'([A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+)', # Case names like "Smith v. Maryland"
        ]
        
        # Citation relationships (parent -> children)
        self.citation_relationships = {}
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract all citations from text."""
        citations = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        return list(set(citations))  # Remove duplicates
    
    def build_citation_chain(self, initial_citations: List[str], max_depth: int = 3) -> List[str]:
        """Build a chain of related citations."""
        chain = initial_citations.copy()
        visited = set(initial_citations)
        
        for depth in range(max_depth):
            new_citations = []
            for citation in chain:
                if citation in self.citation_relationships:
                    for related in self.citation_relationships[citation]:
                        if related not in visited:
                            new_citations.append(related)
                            visited.add(related)
            if new_citations:
                chain.extend(new_citations)
            else:
                break
        
        return chain
    
    def add_citation_relationship(self, parent: str, child: str):
        """Add a citation relationship."""
        if parent not in self.citation_relationships:
            self.citation_relationships[parent] = []
        if child not in self.citation_relationships[parent]:
            self.citation_relationships[parent].append(child)

class ContextWindowManager:
    """Manages context windows while preserving legal completeness."""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
        self.citation_manager = CitationChainManager()
    
    def build_context_window(self, 
                           primary_results: List[SearchResult], 
                           query: str) -> str:
        """Build a context window that preserves legal completeness."""
        
        # Start with primary results
        context_parts = []
        current_length = 0
        
        # Add primary results
        for result in primary_results:
            content = result.content
            if current_length + len(content) <= self.max_context_length:
                context_parts.append(content)
                current_length += len(content)
            else:
                # Truncate if needed
                remaining = self.max_context_length - current_length
                if remaining > 100:  # Only add if we have meaningful space
                    context_parts.append(content[:remaining] + "...")
                break
        
        # Add citation chain context
        all_citations = []
        for result in primary_results:
            all_citations.extend(result.citation_chain)
        
        if all_citations:
            citation_context = self._build_citation_context(all_citations)
            if current_length + len(citation_context) <= self.max_context_length:
                context_parts.append(f"\n\nRelated Citations:\n{citation_context}")
        
        return "\n\n".join(context_parts)
    
    def _build_citation_context(self, citations: List[str]) -> str:
        """Build context for related citations."""
        if not citations:
            return ""
        
        context_parts = []
        for citation in citations[:5]:  # Limit to 5 citations
            context_parts.append(f"- {citation}")
        
        return "\n".join(context_parts)

class HybridSearchEngine:
    """Combines semantic and keyword search with relevance scoring."""
    
    def __init__(self, vector_db: LegalVectorDatabase):
        self.vector_db = vector_db
        self.query_enhancer = LegalQueryEnhancer()
        self.context_manager = ContextWindowManager()
        
        # Relevance scoring weights
        self.relevance_weights = {
            'semantic_score': 0.4,
            'keyword_match': 0.3,
            'jurisdiction_relevance': 0.15,
            'law_status': 0.1,
            'document_type': 0.05
        }
    
    def search(self, 
              query: str, 
              jurisdiction: str = "federal",
              max_results: int = 10) -> List[SearchResult]:
        """Perform hybrid search with enhanced relevance scoring."""
        
        # Enhance query
        enhanced_query = self.query_enhancer.expand_query(query)
        logger.info(f"Enhanced query: {enhanced_query.enhanced_query}")
        
        # Perform semantic search
        semantic_results = self.vector_db.search_legal_documents(
            enhanced_query.enhanced_query, 
            top_k=max_results * 2,  # Get more results for filtering
            include_metadata=True
        )
        
        # Perform keyword search for specific terms
        keyword_results = self._keyword_search(query, enhanced_query)
        
        # Combine and score results
        combined_results = self._combine_results(semantic_results, keyword_results)
        
        # Apply relevance scoring
        scored_results = self._apply_relevance_scoring(
            combined_results, 
            query, 
            enhanced_query, 
            jurisdiction
        )
        
        # Sort by final score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        return scored_results[:max_results]
    
    def _keyword_search(self, query: str, enhanced_query: QueryEnhancement) -> List[Any]:
        """Perform keyword-based search for specific legal terms."""
        
        # Extract statute numbers and case names
        statute_pattern = r'\d+\.\d+[A-Z]*|\d+\s+U\.S\.C\.\s+\d+'
        case_pattern = r'[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+'
        
        statutes = re.findall(statute_pattern, query, re.IGNORECASE)
        cases = re.findall(case_pattern, query, re.IGNORECASE)
        
        keyword_results = []
        
        # Search for specific statutes
        for statute in statutes:
            results = self.vector_db.search_by_statute(statute, top_k=5)
            keyword_results.extend(results)
        
        # Search for specific cases
        for case in cases:
            results = self.vector_db.search_by_case_citation(case, top_k=5)
            keyword_results.extend(results)
        
        return keyword_results
    
    def _combine_results(self, semantic_results: List[Any], keyword_results: List[Any]) -> List[Any]:
        """Combine semantic and keyword results, removing duplicates."""
        
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            combined[result.id] = result
        
        # Add keyword results (may override semantic results with higher scores)
        for result in keyword_results:
            if result.id not in combined or result.score > combined[result.id].score:
                combined[result.id] = result
        
        return list(combined.values())
    
    def _apply_relevance_scoring(self, 
                                results: List[Any], 
                                query: str, 
                                enhanced_query: QueryEnhancement,
                                jurisdiction: str) -> List[SearchResult]:
        """Apply comprehensive relevance scoring."""
        
        scored_results = []
        
        for result in results:
            metadata = result.metadata
            
            # Calculate individual scores
            semantic_score = result.score
            
            # Keyword match score
            keyword_score = self._calculate_keyword_score(query, enhanced_query, metadata)
            
            # Jurisdiction relevance
            jurisdiction_score = self._calculate_jurisdiction_score(metadata, jurisdiction)
            
            # Law status score (current vs. superseded)
            law_status_score = self._calculate_law_status_score(metadata)
            
            # Document type score
            document_type_score = self._calculate_document_type_score(metadata)
            
            # Calculate final weighted score
            final_score = (
                semantic_score * self.relevance_weights['semantic_score'] +
                keyword_score * self.relevance_weights['keyword_match'] +
                jurisdiction_score * self.relevance_weights['jurisdiction_relevance'] +
                law_status_score * self.relevance_weights['law_status'] +
                document_type_score * self.relevance_weights['document_type']
            )
            
            # Extract citation chain
            citation_chain = self.context_manager.citation_manager.extract_citations(
                metadata.get('content', '')
            )
            
            # Determine jurisdiction and law status
            doc_jurisdiction = self._determine_jurisdiction(metadata)
            law_status = self._determine_law_status(metadata)
            
            # Create enhanced result
            enhanced_result = SearchResult(
                content=metadata.get('content', ''),
                score=final_score,
                metadata=metadata,
                relevance_factors={
                    'semantic_score': semantic_score,
                    'keyword_score': keyword_score,
                    'jurisdiction_score': jurisdiction_score,
                    'law_status_score': law_status_score,
                    'document_type_score': document_type_score
                },
                citation_chain=citation_chain,
                jurisdiction=doc_jurisdiction,
                law_status=law_status,
                document_type=metadata.get('chunk_type', 'unknown')
            )
            
            scored_results.append(enhanced_result)
        
        return scored_results
    
    def _calculate_keyword_score(self, query: str, enhanced_query: QueryEnhancement, metadata: Dict[str, Any]) -> float:
        """Calculate keyword match score."""
        content = metadata.get('content', '').lower()
        query_terms = query.lower().split()
        
        matches = 0
        for term in query_terms:
            if term in content:
                matches += 1
        
        # Check for enhanced terms
        for term in enhanced_query.expanded_terms:
            if term.lower() in content:
                matches += 0.5  # Bonus for expanded terms
        
        return min(matches / len(query_terms), 1.0)
    
    def _calculate_jurisdiction_score(self, metadata: Dict[str, Any], target_jurisdiction: str) -> float:
        """Calculate jurisdiction relevance score."""
        content = metadata.get('content', '').lower()
        
        if target_jurisdiction == 'federal':
            federal_indicators = ['federal', 'u.s.', 'united states', 'congress', 'supreme court']
            return max(0.5, sum(1 for indicator in federal_indicators if indicator in content) / len(federal_indicators))
        elif target_jurisdiction == 'state':
            state_indicators = ['state', 'local', 'municipal', 'county']
            return max(0.5, sum(1 for indicator in state_indicators if indicator in content) / len(state_indicators))
        
        return 0.5  # Neutral score
    
    def _calculate_law_status_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate law status score (current vs. superseded)."""
        content = metadata.get('content', '').lower()
        
        # Indicators of current law
        current_indicators = ['current', 'effective', 'active', 'valid']
        superseded_indicators = ['superseded', 'repealed', 'amended', 'replaced', 'obsolete']
        
        current_count = sum(1 for indicator in current_indicators if indicator in content)
        superseded_count = sum(1 for indicator in superseded_indicators if indicator in content)
        
        if superseded_count > current_count:
            return 0.3  # Penalty for superseded law
        elif current_count > superseded_count:
            return 1.0  # Bonus for current law
        
        return 0.7  # Neutral score
    
    def _calculate_document_type_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate document type relevance score."""
        doc_type = metadata.get('chunk_type', 'unknown')
        
        # Prioritize case law and statutes over training materials
        type_scores = {
            'case_law_section': 1.0,
            'policy_section': 0.8,
            'training_module': 0.6,
            'general': 0.5
        }
        
        return type_scores.get(doc_type, 0.5)
    
    def _determine_jurisdiction(self, metadata: Dict[str, Any]) -> str:
        """Determine the jurisdiction of a document."""
        content = metadata.get('content', '').lower()
        
        # Check for Wisconsin-specific indicators first
        wisconsin_indicators = [
            'wisconsin', 'state of wisconsin', 'wi statutes', 'wisconsin statutes',
            'state sovereignty', 'state jurisdiction', 'chapter 1 sovereignty'
        ]
        if any(indicator in content for indicator in wisconsin_indicators):
            return 'state'
        
        # Check for federal indicators
        federal_indicators = ['federal', 'u.s.', 'united states', 'congress', 'supreme court']
        if any(term in content for term in federal_indicators):
            return 'federal'
        
        # Check for general state indicators
        state_indicators = ['state', 'local', 'municipal', 'county']
        if any(term in content for term in state_indicators):
            return 'state'
        
        return 'unknown'
    
    def _determine_law_status(self, metadata: Dict[str, Any]) -> str:
        """Determine if a law is current, superseded, or pending."""
        content = metadata.get('content', '').lower()
        
        if any(term in content for term in ['superseded', 'repealed', 'amended']):
            return 'superseded'
        elif any(term in content for term in ['pending', 'proposed', 'draft']):
            return 'pending'
        else:
            return 'current'

class AdvancedLegalRAG:
    """Complete advanced RAG system for legal documents."""
    
    def __init__(self, vector_db: LegalVectorDatabase):
        self.vector_db = vector_db
        self.hybrid_search = HybridSearchEngine(vector_db)
        self.context_manager = ContextWindowManager()
    
    def ask_question(self, 
                    question: str, 
                    jurisdiction: str = "federal",
                    max_results: int = 5) -> Dict[str, Any]:
        """Ask a question and get comprehensive results."""
        
        # Perform hybrid search
        search_results = self.hybrid_search.search(question, jurisdiction, max_results)
        
        # Build context window
        context = self.context_manager.build_context_window(search_results, question)
        
        # Prepare response
        response = {
            'question': question,
            'jurisdiction': jurisdiction,
            'search_results': search_results,
            'context_window': context,
            'total_results': len(search_results),
            'top_score': search_results[0].score if search_results else 0.0,
            'citation_chain': self._extract_citation_chain(search_results),
            'relevance_breakdown': self._get_relevance_breakdown(search_results)
        }
        
        return response
    
    def _extract_citation_chain(self, results: List[SearchResult]) -> List[str]:
        """Extract all citations from search results."""
        citations = set()
        for result in results:
            citations.update(result.citation_chain)
        return list(citations)
    
    def _get_relevance_breakdown(self, results: List[SearchResult]) -> Dict[str, float]:
        """Get average relevance factors across all results."""
        if not results:
            return {}
        
        factors = defaultdict(list)
        for result in results:
            for factor, score in result.relevance_factors.items():
                factors[factor].append(score)
        
        return {factor: sum(scores) / len(scores) for factor, scores in factors.items()}

# Example usage
if __name__ == "__main__":
    # Initialize the advanced RAG system
    try:
        vector_db = LegalVectorDatabase()
        rag_system = AdvancedLegalRAG(vector_db)
        
        # Test questions
        test_questions = [
            "What does 18 U.S.C. 2703 say about digital evidence?",
            "What are the Fourth Amendment protections for digital privacy?",
            "What are the requirements for digital evidence collection?",
            "What does Smith v. Maryland say about privacy?"
        ]
        
        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"🤖 Question: {question}")
            print(f"{'='*60}")
            
            response = rag_system.ask_question(question)
            
            print(f"📊 Top Score: {response['top_score']:.3f}")
            print(f"📚 Total Results: {response['total_results']}")
            print(f"⚖️ Jurisdiction: {response['jurisdiction']}")
            
            if response['search_results']:
                top_result = response['search_results'][0]
                print(f"\n🏆 Top Result:")
                print(f"   📄 Type: {top_result.document_type}")
                print(f"   📍 Jurisdiction: {top_result.jurisdiction}")
                print(f"   📋 Law Status: {top_result.law_status}")
                print(f"   📖 Content: {top_result.content[:200]}...")
                
                if top_result.citation_chain:
                    print(f"   ⚖️ Citations: {', '.join(top_result.citation_chain[:3])}")
            
            print(f"\n📈 Relevance Breakdown:")
            for factor, score in response['relevance_breakdown'].items():
                print(f"   {factor}: {score:.3f}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your vector database is properly initialized.")
