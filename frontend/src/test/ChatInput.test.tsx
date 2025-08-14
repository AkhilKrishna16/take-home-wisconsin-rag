import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from '../components/chat/ChatInput'

describe('ChatInput', () => {
  it('should render with placeholder text', () => {
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    expect(screen.getByPlaceholderText(/Ask anything… your knowledge base is RAG-augmented/)).toBeInTheDocument()
  })

  it('should show processing placeholder when disabled', () => {
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} disabled />)
    
    expect(screen.getByPlaceholderText('Processing...')).toBeInTheDocument()
  })

  it('should call onSend when send button is clicked with text', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    const textarea = screen.getByRole('textbox')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    await user.type(textarea, 'Hello world')
    await user.click(sendButton)
    
    expect(mockOnSend).toHaveBeenCalledWith('Hello world')
  })

  it('should call onSend when Enter is pressed', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    const textarea = screen.getByRole('textbox')
    
    await user.type(textarea, 'Hello world')
    await user.keyboard('{Enter}')
    
    expect(mockOnSend).toHaveBeenCalledWith('Hello world')
  })

  it('should not send message when text is empty or just whitespace', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    await user.click(sendButton)
    expect(mockOnSend).not.toHaveBeenCalled()
    
    const textarea = screen.getByRole('textbox')
    await user.type(textarea, '   ')
    await user.click(sendButton)
    expect(mockOnSend).not.toHaveBeenCalled()
  })

  it('should clear input after sending message', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    const textarea = screen.getByRole('textbox')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    await user.type(textarea, 'Test message')
    await user.click(sendButton)
    
    expect(textarea).toHaveValue('')
  })

  it('should show stop button when generating', () => {
    const mockOnSend = vi.fn()
    const mockOnStop = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} onStop={mockOnStop} isGenerating />)
    
    expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument()
  })

  it('should call onStop when stop button is clicked', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    const mockOnStop = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} onStop={mockOnStop} isGenerating />)
    
    const stopButton = screen.getByRole('button', { name: /stop/i })
    await user.click(stopButton)
    
    expect(mockOnStop).toHaveBeenCalled()
  })

  it('should prevent sending when disabled', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} disabled />)
    
    const textarea = screen.getByRole('textbox')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    await user.type(textarea, 'This should not send')
    await user.click(sendButton)
    
    expect(mockOnSend).not.toHaveBeenCalled()
  })

  it('should handle Shift+Enter for new lines without sending', async () => {
    const user = userEvent.setup()
    const mockOnSend = vi.fn()
    
    render(<ChatInput onSend={mockOnSend} />)
    
    const textarea = screen.getByRole('textbox')
    
    await user.type(textarea, 'Line 1')
    await user.keyboard('{Shift>}{Enter}{/Shift}')
    await user.type(textarea, 'Line 2')
    
    expect(mockOnSend).not.toHaveBeenCalled()
    expect(textarea).toHaveValue('Line 1\nLine 2')
  })
})