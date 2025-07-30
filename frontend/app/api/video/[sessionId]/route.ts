import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const response = await fetch(`http://localhost:8000/api/video/${params.sessionId}`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    // Get the video data
    const videoBuffer = await response.arrayBuffer()
    
    // Return the video with proper headers
    return new NextResponse(videoBuffer, {
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Disposition': `inline; filename="manim_animation_${params.sessionId}.mp4"`,
      },
    })
    
  } catch (error) {
    console.error('Error fetching video:', error)
    return NextResponse.json(
      { error: 'Failed to fetch video from backend' },
      { status: 500 }
    )
  }
}