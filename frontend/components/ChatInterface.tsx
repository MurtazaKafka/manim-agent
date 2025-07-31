'use client'

import React, { useEffect, useRef } from 'react'
import { useChatStore } from '@/lib/store'
import { api } from '@/lib/api'
import MessageWithActivity from './MessageWithActivity'
import ChatInputWithOptions from './ChatInputWithOptions'
import { AlertCircle } from 'lucide-react'

export default function ChatInterface() {
  const { 
    messages, 
    isGenerating, 
    currentSessionId,
    addMessage, 
    updateMessage, 
    setGenerating, 
    setSessionId 
  } = useChatStore()
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  
  // Debug initial state
  useEffect(() => {
    console.log('ChatInterface mounted, isGenerating:', isGenerating)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (prompt: string, model: string = 'sonnet', duration: number = 3) => {
    console.log('handleSubmit called with:', prompt)
    console.log('isGenerating before:', isGenerating)
    
    try {
      // Add user message
      const userMessageId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      addMessage({
        id: userMessageId,
        role: 'user',
        content: prompt
      })

      // Add initial assistant message
      const assistantMessageId = `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      addMessage({
        id: assistantMessageId,
        role: 'assistant',
        content: 'I\'ll create a beautiful educational animation for you. Let me work on this...',
        status: 'processing',
        progress: 0
      })

      setGenerating(true)
      console.log('Set generating to true')

      // Build conversation history from messages
      const conversationHistory = messages
        .filter(msg => msg.id !== userMessageId && msg.id !== assistantMessageId) // Exclude current messages
        .map(msg => ({
          role: msg.role,
          content: msg.content,
          video_url: msg.videoUrl
        }))
      
      // Start generation with conversation history, model, and duration
      const { session_id } = await api.generateVideo(prompt, conversationHistory, model, duration)
      setSessionId(session_id)

      // Connect WebSocket for real-time updates
      if (wsRef.current) {
        wsRef.current.close()
      }

      // Small delay to ensure backend is ready
      await new Promise(resolve => setTimeout(resolve, 500))

      wsRef.current = api.connectWebSocket(session_id, (status) => {
        // Update assistant message with progress
        // Convert relative video URL to absolute URL
        const videoUrl = status.video_url 
          ? `${process.env.NEXT_PUBLIC_API_URL || ''}${status.video_url}`
          : undefined
          
        updateMessage(assistantMessageId, {
          content: status.message,
          status: status.status === 'completed' ? 'completed' : 
                  status.status === 'failed' ? 'failed' : 'processing',
          currentAgent: status.current_agent,
          progress: status.progress,
          videoUrl: videoUrl
        })

        if (status.status === 'completed' || status.status === 'failed') {
          setGenerating(false)
          if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
          }
        }
      })

    } catch (error) {
      console.error('Error generating video:', error)
      // Make sure to add an ID to the error message
      const errorMessageId = Date.now().toString()
      addMessage({
        id: errorMessageId,
        role: 'assistant',
        content: `I encountered an error while generating your video: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        status: 'failed'
      })
      setGenerating(false)
      console.log('Set generating to false after error')
      
      // Clean up WebSocket if it exists
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-white">
            Manim Agent
          </h1>
          <span className="text-sm text-gray-400">
            AI-Powered Educational Animations
          </span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
              <div className="mb-4 p-4 rounded-full bg-claude-secondary/10">
                <AlertCircle className="w-12 h-12 text-claude-secondary" />
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                Welcome to Manim Agent
              </h2>
              <p className="text-gray-300 max-w-md">
                Transform any educational concept into beautiful animations. 
                Just describe what you want to teach, and I'll create an engaging video for you.
              </p>
              <div className="mt-6 space-y-2 text-sm text-gray-400">
                <p>Try asking me to:</p>
                <ul className="space-y-1">
                  <li>"Explain the concept of derivatives"</li>
                  <li>"Show how bubble sort algorithm works"</li>
                  <li>"Visualize sine and cosine waves"</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageWithActivity key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input */}
      <ChatInputWithOptions onSubmit={handleSubmit} disabled={isGenerating} />
    </div>
  )
}