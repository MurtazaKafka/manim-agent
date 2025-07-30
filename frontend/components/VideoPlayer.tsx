'use client'

import React, { useRef, useEffect } from 'react'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import '@videojs/themes/dist/fantasy/index.css'
import { Download } from 'lucide-react'

interface VideoPlayerProps {
  src: string
  className?: string
}

export default function VideoPlayer({ src, className = '' }: VideoPlayerProps) {
  const videoRef = useRef<HTMLDivElement>(null)
  const playerRef = useRef<any>(null)

  useEffect(() => {
    if (!playerRef.current && videoRef.current) {
      const videoElement = document.createElement('video-js')
      videoElement.classList.add('vjs-big-play-centered', 'vjs-theme-fantasy')
      videoRef.current.appendChild(videoElement)

      const player = playerRef.current = videojs(videoElement, {
        controls: true,
        responsive: true,
        fluid: true,
        sources: [{
          src: src,
          type: 'video/mp4'
        }],
        playbackRates: [0.5, 1, 1.5, 2],
      })

      player.ready(() => {
        console.log('Video player is ready')
      })
    }

    return () => {
      const player = playerRef.current
      if (player && !player.isDisposed()) {
        player.dispose()
        playerRef.current = null
      }
    }
  }, [src])

  useEffect(() => {
    const player = playerRef.current
    if (player) {
      player.src({ src: src, type: 'video/mp4' })
    }
  }, [src])

  const handleDownload = async () => {
    try {
      const response = await fetch(src)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `manim_animation_${Date.now()}.mp4`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className={`relative rounded-lg overflow-hidden shadow-lg ${className}`}>
      <div data-vjs-player>
        <div ref={videoRef} />
      </div>
      
      <button
        onClick={handleDownload}
        className="absolute top-4 right-4 z-10 bg-white/80 hover:bg-white p-2 rounded-lg shadow-md transition-colors"
        title="Download video"
      >
        <Download className="w-5 h-5 text-claude-text" />
      </button>
    </div>
  )
}