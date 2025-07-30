import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const response = await fetch(`http://localhost:8000/api/status/${params.sessionId}`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Error fetching status:', error)
    return NextResponse.json(
      { error: 'Failed to fetch status from backend' },
      { status: 500 }
    )
  }
}