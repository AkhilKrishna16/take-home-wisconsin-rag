#!/usr/bin/env python3
"""
Intelligent Document Chunking System for Legal Documents

This module provides intelligent document chunking that preserves legal context,
handles hierarchical document structures, and maintains metadata for RAG systems.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Text Processing
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available. Install with: pip install nltk")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentChunker:
    """
    Intelligent document chunking that preserves legal context and hierarchical structure.
    
    This chunker is specifically designed for legal documents and understands:
    - Legal document hierarchies (chapters, sections, subsections)
    - Legal metadata (statute numbers, case citations, dates)
    - Document type-specific chunking strategies
    - Context preservation across chunk boundaries
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Legal document structure patterns for hierarchy detection
        self.hierarchy_patterns = {
            'chapter': r'^CHAPTER\s+(\d+|[IVX]+)\.?\s*(.+)$',
            'section': r'^(\d+\.\d+)\s+(.+)$',
            'subsection': r'^(\d+\.\d+\.\d+)\s+(.+)$',
            'paragraph': r'^\(([a-z])\)\s+(.+)$',
            'subparagraph': r'^\((\d+)\)\s+(.+)$',
            'statute': r'^(\d+\.\d+)\s+(.+)$',
            'case_citation': r'^([A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+)',
            'court_opinion': r'^(OPINION|DISSENT|CONCURRENCE)',
            'legal_reference': r'^(See|Cf\.|But see|But cf\.)',
        }
        
        # Metadata extraction patterns for legal context
        self.metadata_patterns = {
            'statute_number': r'(\d+\.\d+[A-Z]*|\d+\s+U\.S\.C\.\s+\d+)',
            'case_citation': r'([A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+,\s+\d+[A-Z]+\s+\d+)',
            'date': r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})',
            'court': r'(Supreme Court|Court of Appeals|District Court|Circuit Court)',
            'docket_number': r'(Docket|Case)\s+No\.?\s*([A-Z0-9\-]+)',
        }
    
    def chunk_document(self, text_content: str, document_type: str) -> List[Dict[str, Any]]:
        """
        Intelligently chunk document while preserving legal context.
        
        Args:
            text_content: The full text content of the document
            document_type: Type of document ('case_law', 'policy', 'training', etc.)
            
        Returns:
            List of chunks with metadata and context information
        """
        # Parse document structure to understand hierarchy
        structure = self._parse_document_structure(text_content)
        
        # Create chunks based on document type using specialized strategies
        if document_type == 'case_law':
            chunks = self._chunk_case_law(text_content, structure)
        elif document_type == 'policy':
            chunks = self._chunk_policy(text_content, structure)
        elif document_type == 'training':
            chunks = self._chunk_training(text_content, structure)
        else:
            chunks = self._chunk_general(text_content, structure)
        
        return chunks
    
    def _parse_document_structure(self, text_content: str) -> Dict[str, Any]:
        """
        Parse hierarchical document structure to understand organization.
        
        This method identifies:
        - Chapters, sections, subsections
        - Legal references and citations
        - Metadata like statute numbers and dates
        - Document hierarchy relationships
        """
        lines = text_content.split('\n')
        structure = {
            'chapters': [],
            'sections': [],
            'subsections': [],
            'paragraphs': [],
            'metadata': {}
        }
        
        current_chapter = None
        current_section = None
        current_subsection = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Extract metadata from each line
            for meta_type, pattern in self.metadata_patterns.items():
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    if meta_type not in structure['metadata']:
                        structure['metadata'][meta_type] = []
                    structure['metadata'][meta_type].extend(matches)
            
            # Detect hierarchy levels using pattern matching
            for level, pattern in self.hierarchy_patterns.items():
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if level == 'chapter':
                        current_chapter = {
                            'number': match.group(1),
                            'title': match.group(2),
                            'start_line': i,
                            'content': line
                        }
                        structure['chapters'].append(current_chapter)
                        current_section = None
                        current_subsection = None
                    
                    elif level == 'section':
                        current_section = {
                            'number': match.group(1),
                            'title': match.group(2),
                            'start_line': i,
                            'content': line,
                            'chapter': current_chapter
                        }
                        structure['sections'].append(current_section)
                        current_subsection = None
                    
                    elif level == 'subsection':
                        current_subsection = {
                            'number': match.group(1),
                            'title': match.group(2),
                            'start_line': i,
                            'content': line,
                            'section': current_section,
                            'chapter': current_chapter
                        }
                        structure['subsections'].append(current_subsection)
                    
                    break
        
        return structure
    
    def _chunk_case_law(self, text_content: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk case law documents preserving legal context.
        
        Case law chunking strategy:
        - Break at major section boundaries (Opinion, Dissent, Concurrence)
        - Preserve legal citations and references within chunks
        - Maintain context of legal arguments
        - Include metadata about case citations and statute references
        """
        chunks = []
        lines = text_content.split('\n')
        
        current_chunk = ""
        current_metadata = {
            'section_type': '',
            'statute_numbers': [],
            'case_citations': [],
            'dates': []
        }
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for major section breaks (Opinion, Dissent, etc.)
            if re.match(self.hierarchy_patterns['court_opinion'], line, re.IGNORECASE):
                # Save current chunk if it exists
                if current_chunk.strip():
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': current_metadata.copy(),
                        'chunk_type': 'case_law_section',
                        'start_line': i - len(current_chunk.split('\n')),
                        'end_line': i - 1
                    })
                
                # Start new chunk with section context
                current_chunk = line + '\n'
                current_metadata = {
                    'section_type': line,
                    'statute_numbers': self._extract_statute_numbers(line),
                    'case_citations': self._extract_case_citations(line),
                    'dates': self._extract_dates(line)
                }
            
            else:
                current_chunk += line + '\n'
                
                # Update metadata with legal references
                current_metadata['statute_numbers'].extend(self._extract_statute_numbers(line))
                current_metadata['case_citations'].extend(self._extract_case_citations(line))
                current_metadata['dates'].extend(self._extract_dates(line))
                
                # Check if chunk is getting too large
                if len(current_chunk) > self.chunk_size:
                    # Try to break at sentence boundary to preserve context
                    sentences = current_chunk.split('. ')
                    if len(sentences) > 1:
                        # Keep last sentence for overlap to maintain context
                        overlap_text = sentences[-1] if len(sentences[-1]) < self.chunk_overlap else ""
                        
                        chunk_content = '. '.join(sentences[:-1]) + '.'
                        chunks.append({
                            'content': chunk_content.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'case_law_section',
                            'start_line': i - len(chunk_content.split('\n')),
                            'end_line': i - 1
                        })
                        
                        current_chunk = overlap_text + '\n' + line + '\n'
                    else:
                        # Force break if no good sentence boundary
                        chunks.append({
                            'content': current_chunk.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'case_law_section',
                            'start_line': i - len(current_chunk.split('\n')),
                            'end_line': i - 1
                        })
                        current_chunk = line + '\n'
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': current_metadata,
                'chunk_type': 'case_law_section',
                'start_line': len(lines) - len(current_chunk.split('\n')),
                'end_line': len(lines) - 1
            })
        
        return chunks
    
    def _chunk_policy(self, text_content: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk policy documents preserving hierarchical structure.
        
        Policy chunking strategy:
        - Break at section boundaries (1.1, 1.2, etc.)
        - Preserve policy numbers and effective dates
        - Maintain section context and relationships
        - Include metadata about policy scope and applicability
        """
        chunks = []
        lines = text_content.split('\n')
        
        current_chunk = ""
        current_metadata = {
            'section_number': '',
            'section_title': '',
            'policy_numbers': [],
            'dates': []
        }
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section breaks (1.1, 1.2, etc.)
            section_match = re.match(self.hierarchy_patterns['section'], line, re.IGNORECASE)
            if section_match:
                # Save current chunk if it exists
                if current_chunk.strip():
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': current_metadata.copy(),
                        'chunk_type': 'policy_section',
                        'section': current_section,
                        'start_line': i - len(current_chunk.split('\n')),
                        'end_line': i - 1
                    })
                
                # Start new chunk with section context
                current_chunk = line + '\n'
                current_section = {
                    'number': section_match.group(1),
                    'title': section_match.group(2)
                }
                current_metadata = {
                    'section_number': section_match.group(1),
                    'section_title': section_match.group(2),
                    'policy_numbers': self._extract_policy_numbers(line),
                    'dates': self._extract_dates(line)
                }
            
            else:
                current_chunk += line + '\n'
                
                # Update metadata
                current_metadata['policy_numbers'].extend(self._extract_policy_numbers(line))
                current_metadata['dates'].extend(self._extract_dates(line))
                
                # Check chunk size
                if len(current_chunk) > self.chunk_size:
                    # Break at paragraph boundary to preserve context
                    paragraphs = current_chunk.split('\n\n')
                    if len(paragraphs) > 1:
                        overlap_text = paragraphs[-1] if len(paragraphs[-1]) < self.chunk_overlap else ""
                        
                        chunk_content = '\n\n'.join(paragraphs[:-1])
                        chunks.append({
                            'content': chunk_content.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'policy_section',
                            'section': current_section,
                            'start_line': i - len(chunk_content.split('\n')),
                            'end_line': i - 1
                        })
                        
                        current_chunk = overlap_text + '\n\n' + line + '\n'
                    else:
                        chunks.append({
                            'content': current_chunk.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'policy_section',
                            'section': current_section,
                            'start_line': i - len(current_chunk.split('\n')),
                            'end_line': i - 1
                        })
                        current_chunk = line + '\n'
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': current_metadata,
                'chunk_type': 'policy_section',
                'section': current_section,
                'start_line': len(lines) - len(current_chunk.split('\n')),
                'end_line': len(lines) - 1
            })
        
        return chunks
    
    def _chunk_training(self, text_content: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk training materials preserving learning objectives.
        
        Training chunking strategy:
        - Break at module/topic boundaries
        - Preserve learning objectives and key terms
        - Maintain educational context and progression
        - Include metadata about learning outcomes
        """
        chunks = []
        lines = text_content.split('\n')
        
        current_chunk = ""
        current_metadata = {
            'module_title': '',
            'learning_objectives': [],
            'key_terms': []
        }
        current_module = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for module/topic breaks
            if re.search(r'^(Module|Topic|Chapter|Lesson)\s+\d+', line, re.IGNORECASE):
                # Save current chunk
                if current_chunk.strip():
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': current_metadata.copy(),
                        'chunk_type': 'training_module',
                        'module': current_module,
                        'start_line': i - len(current_chunk.split('\n')),
                        'end_line': i - 1
                    })
                
                # Start new chunk with module context
                current_chunk = line + '\n'
                current_module = line
                current_metadata = {
                    'module_title': line,
                    'learning_objectives': [],
                    'key_terms': []
                }
            
            else:
                current_chunk += line + '\n'
                
                # Extract learning objectives
                if re.search(r'objective|outcome|goal', line, re.IGNORECASE):
                    current_metadata['learning_objectives'].append(line)
                
                # Extract key terms (all caps lines)
                if re.search(r'^[A-Z][A-Z\s]+$', line):
                    current_metadata['key_terms'].append(line)
                
                # Check chunk size
                if len(current_chunk) > self.chunk_size:
                    # Break at natural boundaries
                    sentences = current_chunk.split('. ')
                    if len(sentences) > 1:
                        overlap_text = sentences[-1] if len(sentences[-1]) < self.chunk_overlap else ""
                        
                        chunk_content = '. '.join(sentences[:-1]) + '.'
                        chunks.append({
                            'content': chunk_content.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'training_module',
                            'module': current_module,
                            'start_line': i - len(chunk_content.split('\n')),
                            'end_line': i - 1
                        })
                        
                        current_chunk = overlap_text + '\n' + line + '\n'
                    else:
                        chunks.append({
                            'content': current_chunk.strip(),
                            'metadata': current_metadata.copy(),
                            'chunk_type': 'training_module',
                            'module': current_module,
                            'start_line': i - len(current_chunk.split('\n')),
                            'end_line': i - 1
                        })
                        current_chunk = line + '\n'
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': current_metadata,
                'chunk_type': 'training_module',
                'module': current_module,
                'start_line': len(lines) - len(current_chunk.split('\n')),
                'end_line': len(lines) - 1
            })
        
        return chunks
    
    def _chunk_general(self, text_content: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        General chunking for other document types.
        
        General chunking strategy:
        - Break at sentence boundaries
        - Maintain semantic coherence
        - Include basic metadata extraction
        - Preserve context through overlap
        """
        chunks = []
        sentences = sent_tokenize(text_content) if NLTK_AVAILABLE else text_content.split('. ')
        
        current_chunk = ""
        current_metadata = {
            'statute_numbers': [],
            'dates': []
        }
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk.strip():
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': current_metadata.copy(),
                        'chunk_type': 'general',
                        'start_line': 0,
                        'end_line': 0
                    })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk.split('. ')[-2:] if len(current_chunk.split('. ')) > 1 else []
                current_chunk = '. '.join(overlap_sentences) + '. ' + sentence + '. '
            else:
                current_chunk += sentence + '. '
            
            # Update metadata
            current_metadata['statute_numbers'] = self._extract_statute_numbers(sentence)
            current_metadata['dates'] = self._extract_dates(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': current_metadata,
                'chunk_type': 'general',
                'start_line': 0,
                'end_line': 0
            })
        
        return chunks
    
    def _extract_statute_numbers(self, text: str) -> List[str]:
        """Extract statute numbers from text."""
        return re.findall(self.metadata_patterns['statute_number'], text, re.IGNORECASE)
    
    def _extract_case_citations(self, text: str) -> List[str]:
        """Extract case citations from text."""
        return re.findall(self.metadata_patterns['case_citation'], text, re.IGNORECASE)
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        return re.findall(self.metadata_patterns['date'], text, re.IGNORECASE)
    
    def _extract_policy_numbers(self, text: str) -> List[str]:
        """Extract policy numbers from text."""
        return re.findall(r'Policy\s+No\.?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)


if __name__ == "__main__":
    # Example usage
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    
    sample_text = """
    SUPREME COURT OF THE UNITED STATES
    Case No. 21-1234
    
    JOHN DOE, PETITIONER
    v.
    JANE SMITH, RESPONDENT
    
    OPINION OF THE COURT
    
    This case presents the question of whether the Fourth Amendment's protection extends to digital communications under 18 U.S.C. 2703.
    
    The petitioner argues that his constitutional rights were violated when law enforcement accessed his email communications without a warrant, citing Smith v. Maryland, 442 U.S. 735 (1979).
    
    The court must consider the application of 42 U.S.C. 1983 in this context, as well as the precedent set by Carpenter v. United States, 585 U.S. 296 (2018).
    
    Filed: January 15, 2024
    
    DISSENT
    
    I respectfully dissent from the majority opinion. The interpretation of 18 U.S.C. 2703 is inconsistent with our precedent in United States v. Jones, 565 U.S. 400 (2012).
    
    The Fourth Amendment analysis should follow the framework established in Katz v. United States, 389 U.S. 347 (1967).
    """
    
    chunks = chunker.chunk_document(sample_text, "case_law")
    print(f"Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Type: {chunk['chunk_type']}")
        print(f"Content: {chunk['content'][:100]}...")
        print(f"Metadata: {chunk['metadata']}")
