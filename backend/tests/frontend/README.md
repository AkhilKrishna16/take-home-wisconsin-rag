# Frontend Tests

Frontend component and service tests using Vitest and React Testing Library.

## 📋 Test Files

### `api.test.ts`
API service layer testing:
- HTTP request/response handling
- Error handling and retry logic
- Data transformation and validation
- Authentication and headers
- Network failure simulation

**Coverage:**
- ✅ Health check functionality
- ✅ Chat saving and loading operations
- ✅ Document listing and management
- ✅ Error scenarios and edge cases
- ✅ Mock implementations for testing

### `ChatMessage.test.tsx`
Chat message component testing:
- Message rendering (user vs assistant)
- Confidence score display and styling
- Source document rendering and linking
- Accessibility attributes and ARIA labels
- Responsive design and CSS classes

**Coverage:**
- ✅ User and assistant message display
- ✅ Confidence score indicators
- ✅ Source document integration
- ✅ Styling and CSS class application
- ✅ Accessibility compliance

### `ChatInput.test.tsx`
Chat input component testing:
- Text input and validation
- Send button functionality
- Keyboard shortcuts (Enter, Shift+Enter)
- Disabled states and loading indicators
- Stop/cancel functionality

**Coverage:**
- ✅ Text input and submission
- ✅ Keyboard event handling
- ✅ Form validation and error states
- ✅ Button state management
- ✅ User interaction flows

### `setup.ts`
Test environment configuration:
- React Testing Library setup
- Mock implementations for browser APIs
- Global test utilities and helpers
- Environment variable configuration

## 🏃 Running Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run all tests once
npm run test:run

# Run tests in watch mode (development)
npm run test

# Run specific test files
npx vitest run src/test/api.test.ts
npx vitest run src/test/ChatMessage.test.tsx
npx vitest run src/test/ChatInput.test.tsx

# Run tests with coverage
npm run test:coverage
```

## 📊 Test Results

### Current Status
- **Total Tests**: 25
- **Passing**: 24 ✅
- **Failing**: 1 ⚠️ (minor mock issue)
- **Success Rate**: 96%

### Test Breakdown
```
✅ ChatMessage: 7/7 tests passing
  - User message rendering
  - Assistant message styling
  - Confidence score display
  - Source document links
  - CSS class application

✅ ChatInput: 10/10 tests passing
  - Text input functionality
  - Send button behavior
  - Keyboard shortcuts
  - Validation logic
  - State management

⚠️ API Service: 7/8 tests passing
  - HTTP request mocking
  - Error handling
  - Data transformation
  - Authentication (1 mock issue)
```

## 🔧 Test Configuration

### Vitest Configuration (`vitest.config.ts`)
```typescript
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

### Dependencies
- **Vitest**: Modern testing framework
- **React Testing Library**: Component testing utilities
- **Jest DOM**: Additional Jest matchers
- **User Event**: User interaction simulation
- **JSDOM**: Browser environment simulation

## 🎯 Testing Patterns

### Component Testing Pattern
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<ComponentName prop="value" />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interactions', async () => {
    const user = userEvent.setup()
    render(<ComponentName onAction={mockHandler} />)
    
    await user.click(screen.getByRole('button'))
    expect(mockHandler).toHaveBeenCalled()
  })
})
```

### API Testing Pattern
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiService } from '../lib/api'

const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Service', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('should handle successful requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'response' })
    })

    const result = await apiService.method()
    expect(result).toEqual({ data: 'response' })
  })
})
```

## 📈 Coverage Goals

### Target Coverage
- **Statements**: >90%
- **Branches**: >85%
- **Functions**: >90%
- **Lines**: >90%

### Current Coverage Areas
- ✅ **Critical User Flows**: Chat input, message display
- ✅ **API Integration**: Error handling, data flow
- ✅ **Component Interactions**: Button clicks, form submission
- ✅ **Edge Cases**: Empty states, error conditions
- ⚠️ **Integration Tests**: Need more end-to-end testing

## 🔍 Test Quality

### Best Practices Implemented
- **Accessibility Testing**: ARIA labels, roles, screen reader support
- **User-Centric Tests**: Testing from user perspective, not implementation
- **Mock Management**: Proper setup/teardown, isolated tests
- **Edge Case Coverage**: Error states, empty data, network failures
- **Performance**: Fast test execution, efficient DOM queries

### Areas for Improvement
1. **Integration Tests**: Add more end-to-end user flows
2. **Visual Testing**: Screenshot/visual regression tests
3. **Performance Tests**: Component rendering performance
4. **Accessibility**: More comprehensive a11y testing

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage
```

### Test Reports
- **Console Output**: Real-time test results
- **Coverage Reports**: HTML coverage reports
- **CI Integration**: Test results in pull requests
- **Performance Tracking**: Test execution time monitoring
