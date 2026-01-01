'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, BookOpen, Clock, TrendingUp, CheckCircle } from 'lucide-react'
import Card from '@/app/components/common/Card'
import Button from '@/app/components/common/Button'
import Loading from '@/app/components/common/Loading'
import LearningRoadmap from '@/app/components/learning/LearningRoadmap'
import { apiClient, Journey, ProgressSummary } from '@/app/services/api'
import { useAuth } from '@/app/hooks/useAuth'

export default function JourneyPreviewPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [journey, setJourney] = useState<Journey | null>(null)
  const [progress, setProgress] = useState<ProgressSummary | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchJourneyRef = React.useRef(false)

  const fetchJourney = React.useCallback(async () => {
    if (fetchJourneyRef.current) return // Prevent duplicate calls
    fetchJourneyRef.current = true
    try {
      setLoading(true)
      const [journeyData, progressData] = await Promise.all([
        apiClient.getJourney(Number(params.id)),
        apiClient.getProgressSummary(Number(params.id)).catch(() => null)
      ])
      setJourney(journeyData)
      setProgress(progressData)
    } catch (error) {
      console.error('Error fetching journey:', error)
    } finally {
      setLoading(false)
      fetchJourneyRef.current = false
    }
  }, [params.id])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/journey/' + params.id + '/preview')
      return
    }
    if (isAuthenticated) {
      fetchJourney()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id, isAuthenticated, authLoading])

  if (authLoading || loading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading journey..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  if (!journey || journey.status !== 'ready' || !journey.resources || journey.resources.length === 0) {
    return (
      <div className="min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="text-center py-12">
            <div className="inline-block w-12 h-12 border-2 border-teal-600/30 border-t-teal-600 rounded-full animate-spin mb-6"></div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              {journey?.status === 'pending' && 'Preparing your journey...'}
              {journey?.status === 'scraping' && 'Finding resources...'}
              {journey?.status === 'curating' && 'Organizing your path...'}
              {!journey && 'Journey not found'}
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-sm">This may take a few minutes</p>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowLeft className="w-4 h-4" />}
            onClick={() => router.back()}
            className="mb-6"
          >
            Back
          </Button>
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4 text-slate-900 dark:text-slate-100">
              {journey.topic}
            </h1>
            <p className="text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-2xl mx-auto leading-relaxed">
              {journey.goal}
            </p>
          </div>
        </div>

        {/* Overview cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-12">
          <Card>
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                {journey.resources.length}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Resources</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                {journey.sections?.length || 1}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Stages</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                {journey.level}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Level</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
                {progress ? `${progress.completion_percentage}%` : '0%'}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-center gap-1">
                <CheckCircle className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                Completed
              </div>
            </div>
          </Card>
        </div>

        {/* Roadmap */}
        <div className="mb-12">
          <LearningRoadmap 
            journey={journey} 
            progressByResource={progress?.progress_by_resource}
            hideEstimatedTime={true}
          />
        </div>

        {/* CTA */}
        <div className="text-center">
          <Button
            variant="primary"
            size="lg"
            onClick={() => router.push(`/journey/${journey.id}`)}
          >
            Start Learning Journey
          </Button>
        </div>
      </div>
    </div>
  )
}

