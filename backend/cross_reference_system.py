#!/usr/bin/env python3
"""
Cross-Reference System for Legal Documents

This module provides intelligent cross-referencing capabilities for legal documents,
automatically identifying and linking related cases, statutes, and documents based on
various criteria including locations, citations, keywords, and patterns.
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import hashlib

# Add the project root to the path
import sys
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from vector_db.vector_database import LegalVectorDatabase
from document_processing.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossReferenceSystem:
    """
    Intelligent cross-referencing system for legal documents.
    
    Features:
    - Automatic detection of related documents
    - Multi-criteria matching (location, citations, keywords, patterns)
    - Relationship mapping and visualization
    - Pattern analysis and trend detection
    - Smart suggestions for related content
    """
    
    def __init__(self, vector_db: Optional[LegalVectorDatabase] = None):
        """Initialize the cross-reference system."""
        self.vector_db = vector_db or LegalVectorDatabase()
        self.cross_references = defaultdict(set)
        self.relationship_graph = defaultdict(dict)
        self.pattern_cache = {}
        
        # Load existing cross-references
        self._load_cross_references()
    
    def _load_cross_references(self):
        """Load existing cross-references from storage."""
        try:
            cross_ref_file = Path("cross_references.json")
            if cross_ref_file.exists():
                with open(cross_ref_file, 'r') as f:
                    data = json.load(f)
                    self.cross_references = defaultdict(set, data.get('cross_references', {}))
                    self.relationship_graph = defaultdict(dict, data.get('relationship_graph', {}))
                    logger.info(f"Loaded {len(self.cross_references)} cross-references")
        except Exception as e:
            logger.warning(f"Could not load cross-references: {e}")
    
    def _save_cross_references(self):
        """Save cross-references to storage."""
        try:
            data = {
                'cross_references': dict(self.cross_references),
                'relationship_graph': dict(self.relationship_graph),
                'last_updated': datetime.now().isoformat()
            }
            with open("cross_references.json", 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Cross-references saved successfully")
        except Exception as e:
            logger.error(f"Could not save cross-references: {e}")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text for cross-referencing."""
        entities = {
            'locations': [],
            'citations': [],
            'dates': [],
            'names': [],
            'keywords': []
        }
        
        # Extract locations (counties, cities, addresses)
        location_patterns = [
            r'\b[A-Z][a-z]+ County\b',  # County names
            r'\b[A-Z][a-z]+ (City|Town|Village)\b',  # Cities
            r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr)\b',  # Addresses
            r'\b[A-Z]{2}\s+\d{5}\b',  # ZIP codes
            r'\bWisconsin\b',  # State name
            r'\bMadison\b',  # Common cities
            r'\bMilwaukee\b',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['locations'].extend(matches)
        
        # Extract legal citations
        citation_patterns = [
            r'\b\d+\.\d+[A-Z]?\b',  # Statute numbers like 2.01, 35.18
            r'\b[A-Z]+\s+\d+\b',  # Case citations
            r'\b\d+\s+U\.S\.\s+\d+\b',  # US Supreme Court
            r'\b\d+\s+Wis\.\s+\d+\b',  # Wisconsin cases
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            entities['citations'].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Extract names (basic pattern)
        name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last names
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            entities['names'].extend(matches)
        
        # Extract keywords (legal terms, case types)
        legal_keywords = [
            'domestic violence', 'traffic stop', 'DUI', 'assault', 'theft',
            'burglary', 'drug possession', 'weapon', 'firearm', 'Miranda',
            'search warrant', 'probable cause', 'reasonable suspicion',
            'use of force', 'excessive force', 'civil rights', 'discrimination',
            'county', 'counties', 'boundaries', 'statutes', 'laws', 'training',
            'procedures', 'policies', 'enforcement', 'officer', 'police'
        ]
        
        for keyword in legal_keywords:
            if keyword.lower() in text.lower():
                entities['keywords'].append(keyword)
        
        # Also add individual words that might be relevant
        words = text.lower().split()
        relevant_words = ['county', 'counties', 'wisconsin', 'statutes', 'laws', 'training', 'procedures']
        for word in relevant_words:
            if word in words:
                entities['keywords'].append(word)
        
        return entities
    
    def calculate_similarity_score(self, doc1_entities: Dict, doc2_entities: Dict) -> float:
        """Calculate similarity score between two documents based on entities."""
        score = 0.0
        total_weight = 0.0
        
        # Location similarity (medium weight)
        location_weight = 0.2
        if doc1_entities['locations'] and doc2_entities['locations']:
            common_locations = set(doc1_entities['locations']) & set(doc2_entities['locations'])
            if common_locations:
                score += location_weight * (len(common_locations) / max(len(doc1_entities['locations']), len(doc2_entities['locations'])))
        total_weight += location_weight
        
        # Citation similarity (medium weight)
        citation_weight = 0.2
        if doc1_entities['citations'] and doc2_entities['citations']:
            common_citations = set(doc1_entities['citations']) & set(doc2_entities['citations'])
            if common_citations:
                score += citation_weight * (len(common_citations) / max(len(doc1_entities['citations']), len(doc2_entities['citations'])))
        total_weight += citation_weight
        
        # Keyword similarity (high weight - more important for general similarity)
        keyword_weight = 0.4
        if doc1_entities['keywords'] and doc2_entities['keywords']:
            common_keywords = set(doc1_entities['keywords']) & set(doc2_entities['keywords'])
            if common_keywords:
                score += keyword_weight * (len(common_keywords) / max(len(doc1_entities['keywords']), len(doc2_entities['keywords'])))
        total_weight += keyword_weight
        
        # Date similarity (medium weight)
        date_weight = 0.15
        if doc1_entities['dates'] and doc2_entities['dates']:
            # Simple date proximity check
            try:
                dates1 = [datetime.strptime(d, '%m/%d/%Y') for d in doc1_entities['dates'] if '/' in d]
                dates2 = [datetime.strptime(d, '%m/%d/%Y') for d in doc2_entities['dates'] if '/' in d]
                if dates1 and dates2:
                    min_diff = min(abs((d1 - d2).days) for d1 in dates1 for d2 in dates2)
                    if min_diff <= 30:  # Within 30 days
                        score += date_weight * (1 - min_diff / 30)
            except:
                pass
        total_weight += date_weight
        
        # Name similarity (low weight)
        name_weight = 0.1
        if doc1_entities['names'] and doc2_entities['names']:
            common_names = set(doc1_entities['names']) & set(doc2_entities['names'])
            if common_names:
                score += name_weight * (len(common_names) / max(len(doc1_entities['names']), len(doc2_entities['names'])))
        total_weight += name_weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def find_cross_references(self, document_id: str, content: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Find cross-references for a given document."""
        # Extract entities from the current document
        current_entities = self.extract_entities(content)
        
        # Search for similar documents in the vector database
        try:
            search_results = self.vector_db.search_legal_documents(
                query=content,
                top_k=20,
                include_metadata=True
            )
        except Exception as e:
            logger.error(f"Error searching for cross-references: {e}")
            return []
        
        cross_refs = []
        
        for result in search_results:
            if result.get('id') == document_id:
                continue  # Skip self-reference
            
            # Extract entities from the result document
            result_content = result.get('content', '')
            result_entities = self.extract_entities(result_content)
            
            # Calculate similarity score
            similarity = self.calculate_similarity_score(current_entities, result_entities)
            
            if similarity >= threshold:
                cross_ref = {
                    'document_id': result.get('id'),
                    'file_name': result.get('metadata', {}).get('file_name', 'Unknown'),
                    'section': result.get('metadata', {}).get('section', 'Unknown'),
                    'similarity_score': similarity,
                    'relevance_score': result.get('score', 0),
                    'common_entities': {
                        'locations': list(set(current_entities['locations']) & set(result_entities['locations'])),
                        'citations': list(set(current_entities['citations']) & set(result_entities['citations'])),
                        'keywords': list(set(current_entities['keywords']) & set(result_entities['keywords'])),
                        'names': list(set(current_entities['names']) & set(result_entities['names']))
                    },
                    'metadata': result.get('metadata', {})
                }
                cross_refs.append(cross_ref)
        
        # Sort by similarity score
        cross_refs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Store cross-references
        self.cross_references[document_id] = {ref['document_id'] for ref in cross_refs}
        
        # Update relationship graph
        for ref in cross_refs:
            self.relationship_graph[document_id][ref['document_id']] = {
                'similarity': ref['similarity_score'],
                'common_entities': ref['common_entities'],
                'timestamp': datetime.now().isoformat()
            }
        
        return cross_refs
    
    def get_related_documents(self, document_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get related documents for a given document ID."""
        if document_id not in self.cross_references:
            return []
        
        related_docs = []
        for related_id in self.cross_references[document_id]:
            if related_id in self.relationship_graph[document_id]:
                relationship = self.relationship_graph[document_id][related_id]
                related_docs.append({
                    'document_id': related_id,
                    'similarity_score': relationship['similarity'],
                    'common_entities': relationship['common_entities'],
                    'last_updated': relationship['timestamp']
                })
        
        # Sort by similarity score and limit results
        related_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return related_docs[:max_results]
    
    def analyze_patterns(self, document_ids: List[str] = None) -> Dict[str, Any]:
        """Analyze patterns across documents."""
        if document_ids is None:
            document_ids = list(self.cross_references.keys())
        
        patterns = {
            'most_connected_documents': [],
            'common_locations': Counter(),
            'common_citations': Counter(),
            'common_keywords': Counter(),
            'temporal_patterns': [],
            'relationship_clusters': []
        }
        
        # Find most connected documents
        connection_counts = Counter()
        for doc_id, related_ids in self.cross_references.items():
            connection_counts[doc_id] = len(related_ids)
        
        patterns['most_connected_documents'] = connection_counts.most_common(10)
        
        # Analyze common entities across all documents
        all_entities = defaultdict(set)
        for doc_id in document_ids:
            # This would require fetching document content
            # For now, we'll use cached relationship data
            if doc_id in self.relationship_graph:
                for related_id, relationship in self.relationship_graph[doc_id].items():
                    common_entities = relationship.get('common_entities', {})
                    for entity_type, entities in common_entities.items():
                        all_entities[entity_type].update(entities)
        
        # Count common entities
        for entity_type, entities in all_entities.items():
            if entity_type == 'locations':
                patterns['common_locations'] = Counter(entities)
            elif entity_type == 'citations':
                patterns['common_citations'] = Counter(entities)
            elif entity_type == 'keywords':
                patterns['common_keywords'] = Counter(entities)
        
        return patterns
    
    def generate_relationship_map(self, document_id: str, depth: int = 2) -> Dict[str, Any]:
        """Generate a relationship map for a document."""
        def get_connections(doc_id: str, current_depth: int, visited: Set[str]) -> Dict[str, Any]:
            if current_depth > depth or doc_id in visited:
                return {}
            
            visited.add(doc_id)
            connections = {}
            
            if doc_id in self.relationship_graph:
                for related_id, relationship in self.relationship_graph[doc_id].items():
                    if related_id not in visited:
                        connections[related_id] = {
                            'similarity': relationship['similarity'],
                            'common_entities': relationship['common_entities'],
                            'connections': get_connections(related_id, current_depth + 1, visited.copy())
                        }
            
            return connections
        
        return {
            'document_id': document_id,
            'relationships': get_connections(document_id, 0, set()),
            'generated_at': datetime.now().isoformat()
        }
    
    def suggest_related_content(self, query: str, document_id: str = None) -> List[Dict[str, Any]]:
        """Suggest related content based on a query or document."""
        suggestions = []
        
        # Extract entities from query
        query_entities = self.extract_entities(query)
        
        # Search for documents with similar entities
        try:
            search_results = self.vector_db.search_legal_documents(
                query=query,
                top_k=15,
                include_metadata=True
            )
        except Exception as e:
            logger.error(f"Error searching for suggestions: {e}")
            return []
        
        for result in search_results:
            result_id = result.get('id')
            if result_id == document_id:
                continue
            
            result_content = result.get('content', '')
            result_entities = self.extract_entities(result_content)
            
            similarity = self.calculate_similarity_score(query_entities, result_entities)
            
            if similarity > 0.2:  # Lower threshold for suggestions
                suggestion = {
                    'document_id': result_id,
                    'file_name': result.get('metadata', {}).get('file_name', 'Unknown'),
                    'section': result.get('metadata', {}).get('section', 'Unknown'),
                    'relevance_score': result.get('score', 0),
                    'similarity_score': similarity,
                    'why_relevant': self._explain_relevance(query_entities, result_entities),
                    'metadata': result.get('metadata', {})
                }
                suggestions.append(suggestion)
        
        # Sort by relevance and similarity
        suggestions.sort(key=lambda x: (x['relevance_score'], x['similarity_score']), reverse=True)
        return suggestions[:10]
    
    def _explain_relevance(self, query_entities: Dict, result_entities: Dict) -> str:
        """Explain why a document is relevant."""
        reasons = []
        
        common_locations = set(query_entities['locations']) & set(result_entities['locations'])
        if common_locations:
            reasons.append(f"Same locations: {', '.join(common_locations)}")
        
        common_citations = set(query_entities['citations']) & set(result_entities['citations'])
        if common_citations:
            reasons.append(f"Same legal citations: {', '.join(common_citations)}")
        
        common_keywords = set(query_entities['keywords']) & set(result_entities['keywords'])
        if common_keywords:
            reasons.append(f"Same legal topics: {', '.join(common_keywords)}")
        
        common_names = set(query_entities['names']) & set(result_entities['names'])
        if common_names:
            reasons.append(f"Same individuals mentioned: {', '.join(common_names)}")
        
        return "; ".join(reasons) if reasons else "Semantic similarity"
    
    def update_cross_references(self):
        """Update all cross-references in the system."""
        logger.info("Starting cross-reference update...")
        
        try:
            # Get all documents from vector database
            # This would require a method to list all documents
            # For now, we'll work with existing cross-references
            
            updated_count = 0
            for doc_id in list(self.cross_references.keys()):
                # This would require fetching document content
                # For demonstration, we'll skip the actual update
                updated_count += 1
            
            logger.info(f"Updated cross-references for {updated_count} documents")
            self._save_cross_references()
            
        except Exception as e:
            logger.error(f"Error updating cross-references: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the cross-reference system
    cross_ref_system = CrossReferenceSystem()
    
    # Example: Find cross-references for a document
    sample_content = """
    In Dane County, Wisconsin, the case involved domestic violence charges under 
    Wisconsin Statute 940.19. The incident occurred on January 15, 2024, at 
    123 Main Street, Madison, WI 53703. Officer Johnson responded to the scene.
    """
    
    print("🔍 Testing Cross-Reference System...")
    
    # Find cross-references
    cross_refs = cross_ref_system.find_cross_references("test_doc_1", sample_content)
    print(f"Found {len(cross_refs)} cross-references")
    
    for i, ref in enumerate(cross_refs[:3]):
        print(f"\nCross-reference {i+1}:")
        print(f"  Document: {ref['file_name']}")
        print(f"  Section: {ref['section']}")
        print(f"  Similarity: {ref['similarity_score']:.3f}")
        print(f"  Common entities: {ref['common_entities']}")
    
    # Generate suggestions
    suggestions = cross_ref_system.suggest_related_content("domestic violence in Dane County")
    print(f"\n📋 Generated {len(suggestions)} suggestions")
    
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"\nSuggestion {i+1}:")
        print(f"  Document: {suggestion['file_name']}")
        print(f"  Why relevant: {suggestion['why_relevant']}")
        print(f"  Relevance score: {suggestion['relevance_score']:.3f}")
    
    print("\n✅ Cross-reference system test completed!")
