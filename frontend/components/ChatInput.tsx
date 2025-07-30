'use client'

import React, { useState, useRef, KeyboardEvent } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSubmit: (prompt: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSubmit, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (input.trim() && !disabled) {
      onSubmit(input.trim())
      setInput('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  return (
    <div className="border-t border-gray-700 bg-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Describe what educational animation you'd like to create..."
            className="flex-1 resize-none rounded-lg border border-gray-600 bg-gray-700 text-white placeholder-gray-400 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed min-h-[56px] max-h-[200px]"
            rows={1}
          />
          
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            className="rounded-lg bg-blue-600 text-white p-3 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send message"
          >
            {disabled ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-400">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}