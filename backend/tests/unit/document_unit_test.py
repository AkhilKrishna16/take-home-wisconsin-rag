#!/usr/bin/env python3
"""
Simple unit tests for the DocumentProcessor class.
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from document_processing.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    """Basic test cases for DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = DocumentProcessor(output_dir=self.temp_dir)
        
        # Test document content
        self.case_law_content = """
        SUPREME COURT OF THE UNITED STATES
        Case No. 21-1234
        
        JOHN DOE, PETITIONER
        v.
        JANE SMITH, RESPONDENT
        
        Filed: January 15, 2024
        
        This case presents the question of whether the Fourth Amendment's protection extends to digital communications.
        """
        
        self.policy_content = """
        DEPARTMENT OF JUSTICE
        Policy No. DOJ-2024-001
        
        Effective Date: February 1, 2024
        
        This policy establishes procedures for digital evidence collection.
        """
    
    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor(output_dir="test_output")
        self.assertEqual(processor.output_dir, Path("test_output"))
        self.assertTrue(processor.output_dir.exists())
    
    def test_get_file_type(self):
        """Test file type detection."""
        self.assertEqual(self.processor._get_file_type(Path("test.pdf")), "pdf")
        self.assertEqual(self.processor._get_file_type(Path("test.docx")), "docx")
        self.assertEqual(self.processor._get_file_type(Path("test.txt")), "text")
        self.assertEqual(self.processor._get_file_type(Path("test.xyz")), "unknown")
    
    def test_detect_document_type(self):
        """Test document type detection."""
        case_law_type = self.processor._detect_document_type(self.case_law_content)
        self.assertEqual(case_law_type, "case_law")
        
        policy_type = self.processor._detect_document_type(self.policy_content)
        self.assertEqual(policy_type, "policy")
    
    def test_extract_text_file(self):
        """Test text file extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.case_law_content)
            temp_file = f.name
        
        try:
            text = self.processor._extract_text_file(Path(temp_file))
            self.assertIn("SUPREME COURT", text)
            self.assertIn("Case No. 21-1234", text)
        finally:
            os.unlink(temp_file)
    
    def test_generate_summary(self):
        """Test summary generation."""
        summary = self.processor._generate_summary(self.case_law_content, "case_law")
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
    
    def test_extract_key_entities(self):
        """Test key entity extraction."""
        entities = self.processor._extract_key_entities(self.case_law_content, "case_law")
        
        self.assertIn('dates', entities)
        self.assertIn('references', entities)
        self.assertIn('January 15, 2024', entities['dates'])
        self.assertIn('Case No. 21-1234', entities['references'])
    
    def test_generate_tags(self):
        """Test tag generation."""
        tags = self.processor._generate_tags(self.case_law_content, "case_law")
        self.assertIn('case_law', tags)
        self.assertIn('legal', tags)
        self.assertIn('court', tags)
    
    def test_process_document(self):
        """Test complete document processing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.case_law_content)
            temp_file = f.name
        
        try:
            result = self.processor.process_document(temp_file, document_type="case_law")
            
            # Check basic structure
            self.assertIn('file_path', result)
            self.assertIn('file_name', result)
            self.assertIn('document_type', result)
            self.assertIn('content', result)
            self.assertIn('summary', result)
            self.assertIn('tags', result)
            
            # Check specific values
            self.assertEqual(result['document_type'], 'case_law')
            self.assertEqual(result['file_type'], 'text')
            self.assertIn('case_law', result['tags'])
            
        finally:
            os.unlink(temp_file)
    
    def test_process_document_file_not_found(self):
        """Test processing non-existent document."""
        with self.assertRaises(FileNotFoundError):
            self.processor.process_document("non_existent_file.txt")
    
    def test_get_processing_stats(self):
        """Test processing statistics."""
        stats = self.processor.get_processing_stats()
        
        self.assertEqual(stats['total_processed'], 0)
        self.assertEqual(stats['document_types'], {})
        self.assertEqual(stats['file_types'], {})
        self.assertEqual(stats['total_size'], 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
