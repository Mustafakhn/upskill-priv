'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from './hooks/useAuth'
import Hero from './components/home/Hero'
import HowItWorks from './components/home/HowItWorks'
import FeaturedTopics from './components/home/FeaturedTopics'
import Stats from './components/home/Stats'
import ChatExamples from './components/home/ChatExamples'
import Loading from './components/common/Loading'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useAuth()

  // Check if running as PWA (standalone mode)
  useEffect(() => {
    if (authLoading) return

    const isPWA = 
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true ||
      document.referrer.includes('android-app://')

    // Redirect logged-in PWA users to my-learning page
    if (isAuthenticated && isPWA) {
      router.replace('/my-learning')
    }
  }, [isAuthenticated, authLoading, router])

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading text="Loading..." />
      </div>
    )
  }

  return (
    <div>
      <Hero />
      <ChatExamples />
      <HowItWorks />
      <FeaturedTopics />
      <Stats />
    </div>
  )
}
