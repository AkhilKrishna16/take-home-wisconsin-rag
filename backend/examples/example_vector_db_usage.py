#!/usr/bin/env python3
"""
Example: Vector Database Usage for Legal Documents

This script demonstrates how to use the integrated vector database system
for processing and searching legal documents.
"""

import os
import tempfile
from pathlib import Path
from document_processor import DocumentProcessor
from vector_database import LegalVectorDatabase

def create_sample_documents():
    """Create sample legal documents for testing."""
    
    # Sample case law document
    case_law_content = """
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
    
    # Sample policy document
    policy_content = """
    DEPARTMENT OF JUSTICE
    Policy No. DOJ-2024-001
    
    STANDARD OPERATING PROCEDURE
    Digital Evidence Collection and Preservation
    
    Effective Date: February 1, 2024
    
    1.1 PURPOSE
    This policy establishes procedures for the collection, preservation, and handling of digital evidence in criminal investigations.
    
    1.2 SCOPE
    This policy applies to all law enforcement personnel within the Department of Justice.
    
    1.3 DEFINITIONS
    (a) "Digital Evidence" means any information stored or transmitted in digital form.
    (b) "Chain of Custody" means the chronological documentation of evidence handling.
    
    2.1 COLLECTION PROCEDURES
    All digital evidence must be collected in accordance with 18 U.S.C. 2703 and relevant case law.
    
    2.2 PRESERVATION REQUIREMENTS
    Digital evidence must be preserved using forensic tools and techniques.
    """
    
    # Sample training document
    training_content = """
    TRAINING MODULE 1
    Introduction to Digital Forensics
    
    Course Objective:
    This module provides an overview of digital forensics principles and methodologies used in criminal investigations.
    
    Learning Outcomes:
    Upon completion of this module, participants will be able to:
    1. Define digital forensics and its role in criminal investigations
    2. Identify different types of digital evidence
    3. Understand basic forensic principles and methodologies
    
    KEY TERMS:
    DIGITAL FORENSICS
    EVIDENCE PRESERVATION
    CHAIN OF CUSTODY
    FORENSIC TOOLS
    """
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp()
    
    case_law_file = Path(temp_dir) / "sample_case_law.txt"
    policy_file = Path(temp_dir) / "sample_policy.txt"
    training_file = Path(temp_dir) / "sample_training.txt"
    
    case_law_file.write_text(case_law_content)
    policy_file.write_text(policy_content)
    training_file.write_text(training_content)
    
    return temp_dir, [case_law_file, policy_file, training_file]

def main():
    """Main example function."""
    
    print("🚀 Legal Document Vector Database Example")
    print("=" * 50)
    
    # Check if environment is set up
    if not os.getenv('PINECONE_API_KEY'):
        print("❌ PINECONE_API_KEY not found in environment variables")
        print("Please set up your .env file with your Pinecone API key")
        print("See env_template.txt for reference")
        return
    
    try:
        # Create sample documents
        print("\n📄 Creating sample documents...")
        temp_dir, sample_files = create_sample_documents()
        
        # Initialize document processor with vector database
        print("\n🔧 Initializing document processor...")
        processor = DocumentProcessor(use_vector_db=True)
        
        # Process documents
        print("\n📚 Processing documents...")
        processed_docs = []
        
        for file_path in sample_files:
            print(f"Processing: {file_path.name}")
            try:
                result = processor.process_document(str(file_path))
                processed_docs.append(result)
                print(f"✅ Processed {file_path.name} - {result['chunk_count']} chunks created")
                
                if result.get('vector_db_indexed'):
                    print(f"   📊 Indexed in vector database as: {result['vector_db_id']}")
                else:
                    print(f"   ⚠️  Failed to index in vector database")
                    
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
        
        # Get vector database stats
        print("\n📊 Vector Database Statistics:")
        stats = processor.get_vector_db_stats()
        print(f"Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"Index dimension: {stats.get('dimension', 'N/A')}")
        
        # Perform searches
        print("\n🔍 Performing searches...")
        
        # Search by statute
        print("\n1. Searching for statute '18 U.S.C. 2703':")
        statute_results = processor.search_by_statute("18 U.S.C. 2703", top_k=3)
        for i, result in enumerate(statute_results, 1):
            print(f"   {i}. Score: {result.score:.3f} - {result.metadata.get('content', '')[:100]}...")
        
        # Search by case citation
        print("\n2. Searching for case 'Smith v. Maryland':")
        case_results = processor.search_by_case_citation("Smith v. Maryland", top_k=3)
        for i, result in enumerate(case_results, 1):
            print(f"   {i}. Score: {result.score:.3f} - {result.metadata.get('content', '')[:100]}...")
        
        # Search by document type
        print("\n3. Searching case law documents for 'Fourth Amendment':")
        type_results = processor.search_by_document_type("case_law", "Fourth Amendment", top_k=3)
        for i, result in enumerate(type_results, 1):
            print(f"   {i}. Score: {result.score:.3f} - {result.metadata.get('content', '')[:100]}...")
        
        # General search with metadata filtering
        print("\n4. General search for 'digital evidence' with metadata filter:")
        filter_results = processor.search_documents(
            "digital evidence",
            top_k=3,
            filter_metadata={'chunk_type': 'policy_section'}
        )
        for i, result in enumerate(filter_results, 1):
            print(f"   {i}. Score: {result.score:.3f} - {result.metadata.get('content', '')[:100]}...")
        
        print("\n✅ Example completed successfully!")
        print(f"📁 Temporary files created in: {temp_dir}")
        print("   (Clean up manually when done)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have:")
        print("1. Set PINECONE_API_KEY in your .env file")
        print("2. Installed required dependencies: pip install -r requirements_vector_db.txt")
        print("3. Created a Pinecone account and index")

if __name__ == "__main__":
    main()
