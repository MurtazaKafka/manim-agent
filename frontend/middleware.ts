import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Log all API requests for debugging
  if (request.nextUrl.pathname.startsWith('/api/')) {
    console.log('API Request:', request.nextUrl.pathname)
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*'
}