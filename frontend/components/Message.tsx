'use client'

import React from 'react'
import { Message as MessageType } from '@/lib/store'
import { Bot, User, Loader2 } from 'lucide-react'
import VideoPlayer from './VideoPlayer'

interface MessageProps {
  message: MessageType
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex gap-4 p-6 ${isUser ? 'bg-gray-800' : 'bg-gray-900'} message-animation`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-blue-600' : 'bg-green-600'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>
      
      <div className="flex-1 space-y-2">
        <div className="text-sm text-gray-400">
          {isUser ? 'You' : 'Manim Agent'}
        </div>
        
        <div className="text-white whitespace-pre-wrap">
          {message.content}
        </div>
        
        {/* Show streaming content if available */}
        {message.streamingContent && message.status === 'processing' && (
          <div className="mt-2 p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-sm text-gray-400 mb-1">Live progress:</div>
            <div className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
              {message.streamingContent}
            </div>
          </div>
        )}
        
        {message.status === 'processing' && (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>
              {message.currentAgent ? `${message.currentAgent} is working...` : 'Processing...'}
            </span>
            {message.progress !== undefined && (
              <div className="ml-4 w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-600 transition-all duration-300"
                  style={{ width: `${message.progress * 100}%` }}
                />
              </div>
            )}
          </div>
        )}
        
        {message.videoUrl && (
          <div className="mt-4">
            <VideoPlayer src={message.videoUrl} />
          </div>
        )}
        
        {message.status === 'failed' && (
          <div className="mt-2 p-3 bg-red-900/20 text-red-400 border border-red-800 rounded-lg text-sm">
            An error occurred while generating your video. Please try again.
          </div>
        )}
      </div>
    </div>
  )
}