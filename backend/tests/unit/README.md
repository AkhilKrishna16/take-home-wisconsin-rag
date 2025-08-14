# Unit Tests

Unit tests for individual components and functions.

## 📋 Test Files

### `document_unit_test.py`
Tests for the DocumentProcessor class:
- Document initialization and configuration
- File type detection (PDF, DOCX, TXT)
- Document type classification (case law, policy, training)
- Text extraction from various file formats
- Summary generation and key entity extraction
- Tag generation and metadata processing
- Error handling for invalid files

**Coverage:**
- ✅ Document processor initialization
- ✅ File type detection
- ✅ Content extraction
- ✅ Metadata generation
- ✅ Error conditions

### `test_langchain_safety_features.py`
Tests for LangChain safety and accuracy features:
- Confidence scoring functionality
- Safety warning generation
- Legal disclaimer inclusion
- Jurisdiction-specific warnings
- Use of force query handling
- Outdated information flagging

**Coverage:**
- ✅ Confidence score calculation
- ✅ Safety warning triggers
- ✅ Legal disclaimers
- ✅ Query classification
- ✅ Edge case handling

## 🏃 Running Unit Tests

```bash
# Run all unit tests
cd backend
python3 tests/unit/document_unit_test.py
python3 tests/unit/test_langchain_safety_features.py

# Run with verbose output
python3 -m unittest tests.unit.document_unit_test -v
python3 -m unittest tests.unit.test_langchain_safety_features -v
```

## 📊 Expected Results

### Document Unit Tests
- **Expected**: 8-10 tests passing
- **Runtime**: ~3-5 seconds
- **Dependencies**: Document processing modules, NLTK data

### Safety Features Tests  
- **Expected**: 5-8 tests passing
- **Runtime**: ~2-4 seconds  
- **Dependencies**: LangChain, OpenAI API (for full tests)

## 🔧 Test Configuration

Tests are designed to work with minimal dependencies:
- Document tests use temporary files and mock data
- Safety tests can run with simulated responses
- No external API calls required for basic functionality
