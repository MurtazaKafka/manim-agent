// WebSocket message types for real-time updates

export interface StatusUpdate {
  session_id: string;
  status: 'processing' | 'completed' | 'error';
  current_agent?: string;
  progress: number;
  message: string;
  video_url?: string;
  error?: string;
  details?: string;
}

export interface StreamingUpdate {
  type: 'streaming';
  agent: string;
  content: string;
  timestamp: string;
}

export type WebSocketMessage = StatusUpdate | StreamingUpdate;

// Type guard
export function isStreamingUpdate(msg: any): msg is StreamingUpdate {
  return msg && msg.type === 'streaming';
}