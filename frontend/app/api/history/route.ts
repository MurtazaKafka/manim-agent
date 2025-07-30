import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/history')
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Error fetching history:', error)
    return NextResponse.json(
      { error: 'Failed to fetch history from backend' },
      { status: 500 }
    )
  }
}