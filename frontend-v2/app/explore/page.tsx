'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import FeaturedTopics from '../components/home/FeaturedTopics'
import Stats from '../components/home/Stats'
import { useAuth } from '../hooks/useAuth'
import Loading from '../components/common/Loading'

export default function ExplorePage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useAuth()

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/explore')
    }
  }, [isAuthenticated, authLoading, router])

  if (authLoading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">
            Explore{' '}
            <span className="bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Topics
            </span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            Browse hundreds of topics and start learning anything you want
          </p>
        </div>
      </div>
      
      <FeaturedTopics />
      <Stats />
    </div>
  )
}

