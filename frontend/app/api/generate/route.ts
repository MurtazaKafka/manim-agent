import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log('API Route: Received request body:', body)
    console.log('API Route: Conversation history length:', body.conversation_history?.length || 0)
    
    // Forward the request to the backend
    const backendUrl = 'http://localhost:8000/api/generate'
    console.log('API Route: Forwarding to backend:', backendUrl)
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    console.log('API Route: Backend response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('API Route: Backend error response:', errorText)
      throw new Error(`Backend returned ${response.status}: ${errorText}`)
    }
    
    const data = await response.json()
    console.log('API Route: Backend response data:', data)
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('API Route: Error forwarding to backend:', error)
    if (error instanceof Error) {
      console.error('API Route: Error message:', error.message)
      console.error('API Route: Error stack:', error.stack)
    }
    return NextResponse.json(
      { 
        error: 'Failed to connect to backend. Make sure the API server is running on port 8000.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}