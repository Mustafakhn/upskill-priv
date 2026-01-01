'use client'

import React from 'react'

interface VideoEmbedProps {
  url: string
  title?: string
  className?: string
}

export default function VideoEmbed({ url, title, className = '' }: VideoEmbedProps) {
  // Extract YouTube video ID
  const getYouTubeId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /youtube\.com\/watch\?.*v=([^&\n?#]+)/,
    ]
    
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match && match[1]) {
        return match[1]
      }
    }
    return null
  }

  // Extract Vimeo video ID
  const getVimeoId = (url: string): string | null => {
    const patterns = [
      /vimeo\.com\/(\d+)/,
      /player\.vimeo\.com\/video\/(\d+)/,
    ]
    
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match && match[1]) {
        return match[1]
      }
    }
    return null
  }

  const youtubeId = getYouTubeId(url)
  const vimeoId = getVimeoId(url)

  if (youtubeId) {
    return (
      <div className={`w-full ${className}`}>
        <div className="relative aspect-video bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-lg">
          <iframe
            src={`https://www.youtube.com/embed/${youtubeId}?rel=0`}
            title={title || 'Video player'}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute top-0 left-0 w-full h-full"
          />
        </div>
      </div>
    )
  }

  if (vimeoId) {
    return (
      <div className={`w-full ${className}`}>
        <div className="relative aspect-video bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-lg">
          <iframe
            src={`https://player.vimeo.com/video/${vimeoId}`}
            title={title || 'Video player'}
            allow="autoplay; fullscreen; picture-in-picture"
            allowFullScreen
            className="absolute top-0 left-0 w-full h-full"
          />
        </div>
      </div>
    )
  }

  // Not a supported video platform
  return null
}

