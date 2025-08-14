import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiService } from '../lib/api'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('ApiService', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('healthCheck', () => {
    it('should return true when server is healthy', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      })

      const result = await apiService.healthCheck()
      
      expect(result).toBe(true)
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5001/health')
    })

    it('should return false when server is unhealthy', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      })

      const result = await apiService.healthCheck()
      
      expect(result).toBe(false)
    })

    it('should return false when fetch throws error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await apiService.healthCheck()
      
      expect(result).toBe(false)
    })
  })

  describe('listSavedChats', () => {
    it('should return list of chats when successful', async () => {
      const mockChats = [
        { filename: 'chat1.json', session_name: 'Test Chat 1' },
        { filename: 'chat2.json', session_name: 'Test Chat 2' }
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { chats: mockChats }
        })
      })

      const result = await apiService.listSavedChats()
      
      expect(result).toEqual(mockChats)
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5001/api/chat/list-saved')
    })

    it('should return empty array when API fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await apiService.listSavedChats()
      
      expect(result).toEqual([])
    })

    it('should return empty array when data structure is invalid', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      const result = await apiService.listSavedChats()
      
      expect(result).toEqual([])
    })
  })

  describe('saveChat', () => {
    it('should save chat successfully', async () => {
      const mockResponse = {
        success: true,
        data: { filename: 'test-chat.json' }
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => mockResponse
      })

      const messages = [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there!' }
      ]

      const result = await apiService.saveChat('Test Chat', messages)
      
      expect(result.success).toBe(true)
      expect(result.filename).toBe('test-chat.json')
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:5001/api/chat/save',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('Test Chat')
        })
      )
    })

    it('should handle save errors gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => ({ error: 'Save failed' })
      })

      const result = await apiService.saveChat('Test Chat', [])
      
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })
})
