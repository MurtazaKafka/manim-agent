'use client'

import React, { useState, useEffect, useRef } from 'react'
import { ChevronUp, ChevronDown, Activity, Cpu, Eye, Code, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { useChatStore } from '@/lib/store'

interface LogEntry {
  timestamp: Date
  agent: string
  action: string
  status: 'info' | 'success' | 'warning' | 'error' | 'processing'
  details?: string
}

export default function ActivityLog() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const logsEndRef = useRef<HTMLDivElement>(null)
  const { currentSessionId } = useChatStore()
  
  // Agent icons
  const agentIcons: Record<string, React.ReactNode> = {
    'ContentAgent': <Cpu className="w-4 h-4" />,
    'VisualDesignAgent': <Eye className="w-4 h-4" />,
    'ManimCodeAgent': <Code className="w-4 h-4" />,
    'Orchestrator': <Activity className="w-4 h-4" />,
    'Renderer': <CheckCircle className="w-4 h-4" />
  }
  
  // Status colors
  const statusColors = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
    processing: 'text-purple-400'
  }
  
  // Subscribe to store changes for WebSocket messages
  useEffect(() => {
    // Get the current generating message to track status updates
    const generatingMessage = useChatStore.getState().messages.find(
      msg => msg.status === 'processing'
    )
    
    if (!generatingMessage) return
    
    // Watch for status updates from the WebSocket
    const unsubscribe = useChatStore.subscribe((state, prevState) => {
      const currentMsg = state.messages.find(msg => msg.id === generatingMessage.id)
      const prevMsg = prevState.messages.find(msg => msg.id === generatingMessage.id)
      
      if (currentMsg && prevMsg && (
        currentMsg.currentAgent !== prevMsg.currentAgent ||
        currentMsg.content !== prevMsg.content ||
        currentMsg.status !== prevMsg.status
      )) {
        // Log the activity
        if (currentMsg.currentAgent) {
          addLog({
            agent: currentMsg.currentAgent,
            action: currentMsg.content,
            status: currentMsg.status === 'completed' ? 'success' : 
                   currentMsg.status === 'failed' ? 'error' : 'processing',
            details: currentMsg.progress ? `Progress: ${Math.round(currentMsg.progress * 100)}%` : undefined
          })
        }
      }
    })
    
    return () => unsubscribe()
  }, [currentSessionId])
  
  const addLog = (entry: Omit<LogEntry, 'timestamp'>) => {
    setLogs(prev => [...prev, { ...entry, timestamp: new Date() }])
  }
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (isExpanded && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, isExpanded])
  
  // Get current status
  const currentActivity = logs.filter(log => log.status === 'processing').pop()
  
  return (
    <div className={`fixed bottom-4 right-4 bg-gray-800 border border-gray-700 rounded-lg shadow-lg transition-all duration-300 ${
      isExpanded ? 'w-96 h-96' : 'w-64 h-12'
    }`}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-700 rounded-t-lg transition-colors"
      >
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium text-white">
            {currentActivity ? 'Processing...' : 'Agent Activity'}
          </span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        )}
      </button>
      
      {/* Current Status (collapsed view) */}
      {!isExpanded && currentActivity && (
        <div className="px-3 pb-2 flex items-center gap-2">
          <Loader2 className="w-3 h-3 text-purple-400 animate-spin" />
          <span className="text-xs text-gray-300 truncate">
            {currentActivity.agent}: {currentActivity.action}
          </span>
        </div>
      )}
      
      {/* Logs (expanded view) */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-80">
          {logs.length === 0 ? (
            <div className="text-center text-gray-500 text-sm py-8">
              No activity yet. Start a generation to see agent activity.
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="text-xs space-y-1">
                <div className="flex items-start gap-2">
                  <div className="flex items-center gap-1 mt-0.5">
                    {agentIcons[log.agent] || <Activity className="w-3 h-3" />}
                    {log.status === 'processing' && (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`font-medium ${statusColors[log.status]}`}>
                        {log.agent}
                      </span>
                      <span className="text-gray-500">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-gray-300">{log.action}</div>
                    {log.details && (
                      <div className="text-gray-500 mt-1">{log.details}</div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      )}
    </div>
  )
}