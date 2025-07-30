'use client'

import React, { useState, useEffect } from 'react'
import { Message as MessageType } from '@/lib/store'
import { Bot, User, Loader2, ChevronDown, ChevronUp, Activity, Cpu, Eye, Code, CheckCircle } from 'lucide-react'
import VideoPlayer from './VideoPlayer'

interface MessageProps {
  message: MessageType
}

interface ActivityLogEntry {
  timestamp: Date
  agent: string
  action: string
  status: 'info' | 'success' | 'warning' | 'error' | 'processing'
  progress?: number
}

export default function MessageWithActivity({ message }: MessageProps) {
  const isUser = message.role === 'user'
  const [showActivity, setShowActivity] = useState(false)
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([])
  
  // Test data - remove this after testing
  useEffect(() => {
    if (!isUser && message.status === 'processing' && activityLog.length === 0) {
      setActivityLog([
        {
          timestamp: new Date(),
          agent: 'ContentAgent',
          action: 'Researching educational content...',
          status: 'processing',
          progress: 0.2
        }
      ])
    }
  }, [isUser, message.status])
  
  // Agent icons
  const agentIcons: Record<string, React.ReactNode> = {
    'ContentAgent': <Cpu className="w-3 h-3" />,
    'VisualDesignAgent': <Eye className="w-3 h-3" />,
    'ManimCodeAgent': <Code className="w-3 h-3" />,
    'Renderer': <CheckCircle className="w-3 h-3" />
  }
  
  // Track activity changes
  useEffect(() => {
    console.log('MessageWithActivity tracking:', {
      isUser,
      currentAgent: message.currentAgent,
      status: message.status,
      content: message.content
    })
    
    if (!isUser && message.currentAgent && message.status === 'processing') {
      // Add new activity entry when agent changes
      setActivityLog(prev => {
        const lastEntry = prev[prev.length - 1]
        if (!lastEntry || lastEntry.agent !== message.currentAgent) {
          return [...prev, {
            timestamp: new Date(),
            agent: message.currentAgent!,
            action: message.content,
            status: 'processing',
            progress: message.progress
          }]
        }
        // Update progress if same agent
        if (lastEntry && message.progress !== lastEntry.progress) {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...lastEntry,
            progress: message.progress,
            action: message.content
          }
          return updated
        }
        return prev
      })
    }
    
    // Mark completed when done
    if (!isUser && message.status === 'completed' && activityLog.length > 0) {
      setActivityLog(prev => {
        const updated = [...prev]
        if (updated.length > 0) {
          updated[updated.length - 1].status = 'success'
        }
        return updated
      })
    }
  }, [message.currentAgent, message.status, message.content, message.progress, isUser])
  
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
        
        {/* Activity Log Toggle */}
        {!isUser && (activityLog.length > 0 || message.status === 'processing' || message.status === 'completed') && (
          <button
            onClick={() => setShowActivity(!showActivity)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 transition-colors mt-2"
          >
            <Activity className="w-4 h-4" />
            <span>View agent activity</span>
            {showActivity ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        )}
        
        {/* Activity Log */}
        {showActivity && (
          <div className="mt-3 p-3 bg-gray-800 rounded-lg border border-gray-700 space-y-2">
            <div className="text-xs font-medium text-gray-400 mb-2">Agent Activity Timeline</div>
            {activityLog.map((log, index) => (
              <div key={index} className="flex items-start gap-2 text-xs">
                <div className="flex items-center gap-1 mt-0.5">
                  {agentIcons[log.agent] || <Activity className="w-3 h-3" />}
                  {log.status === 'processing' && (
                    <Loader2 className="w-3 h-3 animate-spin text-purple-400" />
                  )}
                  {log.status === 'success' && (
                    <CheckCircle className="w-3 h-3 text-green-400" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-medium ${
                      log.status === 'processing' ? 'text-purple-400' : 
                      log.status === 'success' ? 'text-green-400' : 'text-gray-400'
                    }`}>
                      {log.agent}
                    </span>
                    <span className="text-gray-500">
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                    {log.progress !== undefined && (
                      <span className="text-gray-500">
                        ({Math.round(log.progress * 100)}%)
                      </span>
                    )}
                  </div>
                  <div className="text-gray-300 mt-0.5">{log.action}</div>
                </div>
              </div>
            ))}
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