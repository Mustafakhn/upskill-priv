'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BookOpen, Clock, CheckCircle, TrendingUp, Plus, Crown, AlertCircle } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Badge from '../components/common/Badge'
import Loading from '../components/common/Loading'
import { apiClient, Journey } from '../services/api'
import { useAuth } from '../hooks/useAuth'

export default function MyLearningPage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading, user } = useAuth()
  const [journeys, setJourneys] = useState<Journey[]>([])
  const [loading, setLoading] = useState(true)
  const [requestingPremium, setRequestingPremium] = useState(false)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/my-learning')
      return
    }
    if (isAuthenticated) {
      loadJourneys()
    }
  }, [isAuthenticated, authLoading, router])

  const loadJourneys = async () => {
    try {
      const data = await apiClient.getUserJourneys()
      // Load full journey details to get resources
      const journeysWithResources = await Promise.allSettled(
        data.map(async (journey) => {
          if (journey.status === 'ready' && journey.id) {
            try {
              const fullJourney = await apiClient.getJourney(journey.id)
              return fullJourney
            } catch (error: any) {
              // Log error but don't break the entire page
              console.error(`Failed to load journey ${journey.id}:`, error)
              // Return the basic journey object if full details fail to load
              return journey
            }
          }
          return journey
        })
      )
      // Extract successful results, fallback to basic journey for failed ones
      const resolvedJourneys = journeysWithResources.map((result, index) => {
        if (result.status === 'fulfilled') {
          return result.value
        } else {
          console.error(`Journey at index ${index} failed to load:`, result.reason)
          // Return the basic journey from original data
          return data[index] || null
        }
      }).filter(journey => journey !== null)
      
      setJourneys(resolvedJourneys)
    } catch (error: any) {
      console.error('Failed to load journeys:', error)
      // Show user-friendly error message
      if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
        console.warn('Backend might not be running or unreachable. Please check if the backend server is running.')
      }
      setJourneys([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'primary'
      case 'completed':
        return 'success'
      case 'pending':
      case 'scraping':
      case 'curating':
        return 'warning'
      default:
        return 'secondary'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'ready':
        return 'Ready'
      case 'completed':
        return 'Completed'
      case 'pending':
        return 'Pending'
      case 'scraping':
        return 'Scraping'
      case 'curating':
        return 'Curating'
      default:
        return status.charAt(0).toUpperCase() + status.slice(1)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading your learning journeys..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl sm:text-4xl font-bold">My Learning</h1>
            {user && !user.is_premium && (
              <Button
                variant="primary"
                size="sm"
                icon={<Crown className="w-4 h-4" />}
                onClick={async () => {
                  if (user.premium_requested) {
                    alert('You have already requested premium upgrade. Please wait for admin approval.')
                    return
                  }
                  setRequestingPremium(true)
                  try {
                    await apiClient.requestPremium()
                    alert('Premium upgrade requested successfully! An admin will review your request.')
                    // Refresh user data
                    window.location.reload()
                  } catch (error: any) {
                    alert(error?.response?.data?.detail || 'Failed to request premium upgrade. Please try again.')
                  } finally {
                    setRequestingPremium(false)
                  }
                }}
                disabled={requestingPremium || user.premium_requested}
              >
                {user.premium_requested ? 'Request Pending' : 'Upgrade to Premium'}
              </Button>
            )}
            {user?.is_premium && (
              <Badge variant="success" className="flex items-center gap-1">
                <Crown className="w-4 h-4" />
                Premium
              </Badge>
            )}
          </div>
          <p className="text-slate-600 dark:text-slate-400">
            Track your progress and continue your learning journey
            {user && !user.is_premium && (
              <span className="block mt-2 text-sm">
                {user.free_journeys_used} / 5 free journeys used
              </span>
            )}
            {user?.is_premium && (
              <span className="block mt-2 text-sm text-teal-600 dark:text-teal-400">
                Unlimited journeys with Premium
              </span>
            )}
          </p>
        </div>

        {/* Stats */}
        {journeys.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-teal-100 dark:bg-teal-900/30">
                  <BookOpen className="w-6 h-6 text-teal-600 dark:text-teal-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{journeys.length}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Total Journeys</div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                  <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {journeys.filter(j => j.status === 'ready').length}
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">In Progress</div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {journeys.filter(j => j.status === 'completed').length}
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Completed</div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                  <Clock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
            <div className="text-2xl font-bold">
              {journeys.reduce((sum, j) => sum + (j.resources?.length || j.resource_count || 0), 0)}
            </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Total Resources</div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Journeys List */}
        {journeys.length === 0 ? (
          <Card className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <BookOpen className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No Learning Journeys Yet</h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Start your first learning journey and master any skill you want
            </p>
            <Button
              variant="primary"
              icon={<Plus className="w-5 h-5" />}
              onClick={() => router.push('/start')}
            >
              Start Learning
            </Button>
          </Card>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Your Journeys</h2>
              <Button
                variant="primary"
                size="sm"
                icon={<Plus className="w-4 h-4" />}
                onClick={() => router.push('/start')}
              >
                New Journey
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {journeys.map((journey) => (
                <Card
                  key={journey.id}
                  hoverable
                  clickable
                  onClick={() => router.push(`/journey/${journey.id}`)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-1">{journey.topic}</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                        {journey.goal}
                      </p>
                    </div>
                    <Badge variant={getStatusColor(journey.status) as 'primary' | 'secondary' | 'success' | 'warning' | 'danger'}>
                      {getStatusLabel(journey.status)}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                    <div className="flex items-center gap-1">
                      <BookOpen className="w-4 h-4" />
                      <span>{journey.resources?.length || journey.resource_count || 0} resources</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Badge variant="secondary">{journey.level}</Badge>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div className="flex items-center gap-2">
                      {journey.status === 'ready' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/journey/${journey.id}/preview`)
                          }}
                          className="flex-1"
                        >
                          Preview
                        </Button>
                      )}
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          if (journey.status === 'ready') {
                            router.push(`/journey/${journey.id}`)
                          } else {
                            router.push(`/journey/${journey.id}/preview`)
                          }
                        }}
                        className="flex-1"
                      >
                        {journey.status === 'ready' ? 'Continue' : 'View Status'}
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

