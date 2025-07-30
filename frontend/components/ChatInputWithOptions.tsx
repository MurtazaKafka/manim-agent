'use client'

import React, { useState, useRef, KeyboardEvent } from 'react'
import { Send, Loader2, Settings2, Clock, Sparkles } from 'lucide-react'

interface ChatInputProps {
  onSubmit: (prompt: string, model: string, duration: number) => void
  disabled?: boolean
}

export default function ChatInputWithOptions({ onSubmit, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('')
  const [model, setModel] = useState<'sonnet' | 'opus'>('sonnet')
  const [duration, setDuration] = useState(3) // minutes
  const [showOptions, setShowOptions] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (input.trim() && !disabled) {
      onSubmit(input.trim(), model, duration)
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
        {/* Options Panel */}
        <div className={`mb-3 overflow-hidden transition-all duration-300 ${showOptions ? 'max-h-40' : 'max-h-0'}`}>
          <div className="bg-gray-700 rounded-lg p-4 flex flex-wrap gap-4 items-center">
            {/* Model Selection */}
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300">Model:</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setModel('sonnet')}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    model === 'sonnet' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                >
                  Sonnet (Fast)
                </button>
                <button
                  onClick={() => setModel('opus')}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    model === 'opus' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                >
                  Opus 4 (Quality)
                </button>
              </div>
            </div>

            {/* Duration Selection */}
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300">Duration:</span>
              <input
                type="range"
                min="1"
                max="15"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-24"
              />
              <span className="text-sm text-white font-medium w-12">{duration}m</span>
            </div>

            {/* Presets */}
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => { setModel('sonnet'); setDuration(2); }}
                className="px-3 py-1 text-xs bg-gray-600 text-gray-300 rounded-md hover:bg-gray-500"
              >
                Quick Demo
              </button>
              <button
                onClick={() => { setModel('opus'); setDuration(10); }}
                className="px-3 py-1 text-xs bg-gray-600 text-gray-300 rounded-md hover:bg-gray-500"
              >
                Full Lesson
              </button>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="flex gap-3 items-end">
          <button
            onClick={() => setShowOptions(!showOptions)}
            className="rounded-lg bg-gray-700 text-gray-300 p-3 hover:bg-gray-600 transition-colors"
            title="Toggle options"
          >
            <Settings2 className="w-5 h-5" />
          </button>

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
        
        <div className="mt-2 text-xs text-gray-400 flex justify-between">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>
            {model === 'opus' ? '🎨 High Quality Mode' : '⚡ Fast Mode'} • 
            {duration < 5 ? ' Quick ' : duration < 10 ? ' Standard ' : ' Comprehensive '}
            {duration}m video
          </span>
        </div>
      </div>
    </div>
  )
}