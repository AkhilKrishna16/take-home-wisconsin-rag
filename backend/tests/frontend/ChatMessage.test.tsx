import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChatMessage } from '../components/chat/ChatMessage'

describe('ChatMessage', () => {
  it('should render user message correctly', () => {
    render(
      <ChatMessage role="user">
        Hello, this is a user message
      </ChatMessage>
    )

    expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'User message')
    expect(screen.getByText('Hello, this is a user message')).toBeInTheDocument()
  })

  it('should render assistant message correctly', () => {
    render(
      <ChatMessage role="assistant">
        Hello, this is an assistant message
      </ChatMessage>
    )

    expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'Assistant message')
    expect(screen.getByText('Hello, this is an assistant message')).toBeInTheDocument()
  })

  it('should display confidence score for assistant messages', () => {
    const metadata = {
      confidence_score: 0.85
    }

    render(
      <ChatMessage role="assistant" metadata={metadata}>
        This is a high-confidence response
      </ChatMessage>
    )

    expect(screen.getByText(/Match Score: 85%/)).toBeInTheDocument()
  })

  it('should display different confidence indicators based on score', () => {
    const lowConfidenceMetadata = { confidence_score: 0.5 }
    const mediumConfidenceMetadata = { confidence_score: 0.7 }
    const highConfidenceMetadata = { confidence_score: 0.9 }

    const { rerender } = render(
      <ChatMessage role="assistant" metadata={lowConfidenceMetadata}>
        Low confidence
      </ChatMessage>
    )
    expect(screen.getByText(/Match Score: 50%/)).toBeInTheDocument()

    rerender(
      <ChatMessage role="assistant" metadata={mediumConfidenceMetadata}>
        Medium confidence
      </ChatMessage>
    )
    expect(screen.getByText(/Match Score: 70%/)).toBeInTheDocument()

    rerender(
      <ChatMessage role="assistant" metadata={highConfidenceMetadata}>
        High confidence
      </ChatMessage>
    )
    expect(screen.getByText(/Match Score: 90%/)).toBeInTheDocument()
  })

  it('should render source documents when provided', () => {
    const sources = [
      { title: 'Wisconsin Statute 123', url: 'https://example.com/statute-123' },
      { title: 'Case Law ABC', url: 'https://example.com/case-abc' }
    ]

    render(
      <ChatMessage role="assistant" sources={sources}>
        Response with sources
      </ChatMessage>
    )

    expect(screen.getByText('Source 1: Wisconsin Statute 123')).toBeInTheDocument()
    expect(screen.getByText('Source 2: Case Law ABC')).toBeInTheDocument()
  })

  it('should apply correct styling classes for user vs assistant messages', () => {
    const { rerender } = render(
      <ChatMessage role="user">User message</ChatMessage>
    )

    let messageContainer = screen.getByRole('article').firstChild as HTMLElement
    expect(messageContainer).toHaveClass('bg-primary/10', 'border-primary/20')

    rerender(
      <ChatMessage role="assistant">Assistant message</ChatMessage>
    )

    messageContainer = screen.getByRole('article').firstChild as HTMLElement
    expect(messageContainer).toHaveClass('bg-card', 'border-border')
  })

  it('should not display confidence score for user messages', () => {
    const metadata = { confidence_score: 0.85 }

    render(
      <ChatMessage role="user" metadata={metadata}>
        User message with metadata
      </ChatMessage>
    )

    expect(screen.queryByText(/Match Score/)).not.toBeInTheDocument()
  })
})
