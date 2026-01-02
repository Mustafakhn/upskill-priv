'use client'

import React from 'react'
import { ArrowRight, Bot } from 'lucide-react'
import SearchBar from '../common/SearchBar'
import Button from '../common/Button'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../hooks/useAuth'

export default function Hero() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()

  const handleSearch = (query: string) => {
    if (isAuthenticated) {
      router.push(`/start?topic=${encodeURIComponent(query)}`)
    } else {
      router.push(`/register?redirect=/start&topic=${encodeURIComponent(query)}`)
    }
  }

  const popularSearches = [
    'Python Programming',
    'Guitar for Beginners',
    'Italian Cooking',
    'Digital Marketing',
    'Web Development',
    'Photography',
  ]

  return (
    <section className="relative py-20 sm:py-32 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal-400/20 dark:bg-teal-600/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-400/20 dark:bg-cyan-600/10 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 text-sm font-medium mb-6 animate-slide-down">
            <Bot className="w-4 h-4" />
            AI-Powered Learning Companion
          </div>

          {/* Heading */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 animate-slide-up">
            Master{' '}
            <span className="bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Any Skill
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl sm:text-2xl text-slate-600 dark:text-slate-400 mb-12 animate-slide-up" style={{ animationDelay: '100ms' }}>
            From cooking to coding, guitar to gardening - find the best tutorials, videos, and articles curated just for you
          </p>

          {/* Search Bar */}
          <div className="mb-8 animate-slide-up" style={{ animationDelay: '200ms' }}>
            <SearchBar
              onSearch={handleSearch}
              placeholder="What do you want to learn today?"
              suggestions={popularSearches}
              className="max-w-2xl mx-auto"
            />
          </div>

          {/* Popular searches */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-12 animate-fade-in" style={{ animationDelay: '300ms' }}>
            <span className="text-sm text-slate-600 dark:text-slate-400">Popular:</span>
            {popularSearches.slice(0, 4).map((search) => (
              <button
                key={search}
                onClick={() => handleSearch(search)}
                className="px-3 py-1 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-700 dark:text-slate-300 hover:border-teal-500 dark:hover:border-teal-500 hover:text-teal-600 dark:hover:text-teal-400 transition-all duration-200"
              >
                {search}
              </button>
            ))}
          </div>

          {/* CTA Button */}
          <div className="animate-fade-in" style={{ animationDelay: '400ms' }}>
            <Button
              variant="primary"
              size="lg"
              icon={<ArrowRight className="w-5 h-5" />}
              onClick={() => router.push(isAuthenticated ? '/start' : '/register')}
            >
              {isAuthenticated ? 'Start Learning Now' : 'Get Started Free'}
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}

