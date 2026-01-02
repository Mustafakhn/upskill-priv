'use client'

import { useEffect } from 'react'
import { registerServiceWorker } from '../../utils/notifications'

export default function ServiceWorkerSetup() {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      registerServiceWorker().catch(console.error)
    }
  }, [])

  return null
}

