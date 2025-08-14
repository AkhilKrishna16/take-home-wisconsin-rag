# Test Suite Organization

This directory contains all tests for the Legal RAG System, organized by type and scope.

## 📁 Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── document_unit_test.py      # Document processor tests
│   └── test_langchain_safety_features.py  # Safety features tests
├── integration/             # Integration tests for API endpoints
│   ├── test_flask_app.py          # Flask API endpoint tests
│   └── test_advanced_rag.py       # RAG system integration tests
├── performance/             # Performance and benchmarking tests
│   └── test_performance_metrics.py # Comprehensive performance evaluation
└── frontend/               # Frontend component tests
    ├── api.test.ts              # API service tests
    ├── ChatInput.test.tsx       # Chat input component tests
    ├── ChatMessage.test.tsx     # Chat message component tests
    └── setup.ts                 # Test setup configuration
```

## 🧪 Running Tests

### Backend Tests

```bash
# Run all backend tests
cd backend

# Unit tests
python3 tests/unit/document_unit_test.py
python3 tests/unit/test_langchain_safety_features.py

# Integration tests  
python3 tests/integration/test_flask_app.py
python3 tests/integration/test_advanced_rag.py

# Performance tests
python3 tests/performance/test_performance_metrics.py
```

### Frontend Tests

```bash
# Run all frontend tests
cd frontend

# All tests
npm run test:run

# Specific test files
npx vitest run src/test/api.test.ts
npx vitest run src/test/ChatMessage.test.tsx
npx vitest run src/test/ChatInput.test.tsx

# Watch mode for development
npm run test
```

## 📊 Test Coverage

### Backend Coverage
- **Unit Tests**: Document processing, safety features, utility functions
- **Integration Tests**: API endpoints, RAG system, chatbot functionality  
- **Performance Tests**: Response times, accuracy metrics, relevance scoring

### Frontend Coverage
- **Component Tests**: Chat interface, message display, user interactions
- **Service Tests**: API calls, error handling, data transformation
- **Integration Tests**: User workflows, state management

## 🎯 Test Types

### Unit Tests
- Test individual functions and classes in isolation
- Fast execution (<1s per test)
- No external dependencies (mocked)
- High coverage of edge cases

### Integration Tests
- Test component interactions and API endpoints
- Medium execution time (1-5s per test)
- May require database/external services
- Focus on data flow and error handling

### Performance Tests
- Measure response times and accuracy metrics
- Longer execution time (30s-2min)
- Require full system setup
- Generate detailed performance reports

## 📈 Performance Metrics

The performance test suite evaluates:

1. **Retrieval Accuracy**
   - Precision and recall metrics
   - Relevance scoring evaluation
   - Query-answer alignment

2. **Response Times**
   - End-to-end latency
   - Component-level timing
   - Percentile distributions

3. **System Health**
   - Resource utilization
   - Error rates
   - Scalability metrics

## 🔧 Test Configuration

### Environment Setup
```bash
# Backend tests require virtual environment
source venv/bin/activate  # or source ../venv/bin/activate

# Frontend tests require Node.js dependencies
npm install  # (in frontend directory)
```

### Required Environment Variables
```bash
# For integration and performance tests
PINECONE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
PINECONE_INDEX_NAME=legal-documents
```

## 📝 Adding New Tests

### Backend Test Template
```python
#!/usr/bin/env python3
"""Test description."""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_functionality(self):
        """Test specific functionality."""
        # Your test code here
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### Frontend Test Template
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { YourComponent } from '../path/to/component'

describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## 🎯 Best Practices

1. **Naming**: Use descriptive test names that explain what is being tested
2. **Isolation**: Each test should be independent and not rely on others
3. **Coverage**: Aim for high coverage of critical paths and edge cases
4. **Speed**: Keep unit tests fast, use mocks for external dependencies
5. **Maintainability**: Update tests when code changes, remove obsolete tests

## 📊 Test Reports

Performance tests generate detailed JSON reports:
- `performance_metrics_YYYYMMDD_HHMMSS.json` - Complete performance data
- Console output with summary statistics
- Graphs and visualizations (when available)
