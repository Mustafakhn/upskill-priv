'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  BookOpen,
  Video,
  FileText,
  ExternalLink,
  CheckCircle,
  Circle,
  Clock,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Loader2,
  ArrowLeft,
  Map
} from 'lucide-react'
import Card from '@/app/components/common/Card'
import Button from '@/app/components/common/Button'
import Badge from '@/app/components/common/Badge'
import Loading from '@/app/components/common/Loading'
import VideoEmbed from '@/app/components/resources/VideoEmbed'
import ArticleViewer from '@/app/components/resources/ArticleViewer'
import RoadmapSidebar from '@/app/components/learning/RoadmapSidebar'
import ChatbotOverlay from '@/app/components/companion/ChatbotOverlay'
import { apiClient, Journey, ProgressSummary } from '@/app/services/api'
import { useAuth } from '@/app/hooks/useAuth'

export default function JourneyDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const journeyId = parseInt(params.id as string)

  const [journey, setJourney] = useState<Journey | null>(null)
  const [progress, setProgress] = useState<ProgressSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentResourceIndex, setCurrentResourceIndex] = useState(0)
  const [roadmapOpen, setRoadmapOpen] = useState(true)
  const [markingComplete, setMarkingComplete] = useState<string | null>(null)

  // For mobile, default to closed roadmap
  useEffect(() => {
    const checkMobile = () => {
      if (window.innerWidth < 1024) {
        setRoadmapOpen(false)
      } else {
        setRoadmapOpen(true)
      }
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])
  const skipTimeTrackingRef = useRef<string | null>(null)

  // Time tracking
  const timeTrackingRef = useRef<{
    startTime: number | null
    resourceId: string | null
    intervalId: NodeJS.Timeout | null
  }>({
    startTime: null,
    resourceId: null,
    intervalId: null
  })

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/journey/' + journeyId)
    }
  }, [isAuthenticated, authLoading, router, journeyId])

  useEffect(() => {
    if (journeyId && isAuthenticated) {
      loadJourneyData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [journeyId, isAuthenticated])

  // Start time tracking when resource changes
  useEffect(() => {
    // Skip if we're currently marking a resource as complete/incomplete
    if (markingComplete) {
      console.log('Skipping time tracking useEffect - completion status being updated')
      return
    }

    if (journey?.resources?.[currentResourceIndex]) {
      const resourceId = journey.resources[currentResourceIndex].id
      // Small delay to ensure progress state is up to date
      const timeoutId = setTimeout(() => {
        startTimeTracking(resourceId)
      }, 50)

      return () => {
        clearTimeout(timeoutId)
        stopTimeTracking()
      }
    } else {
      stopTimeTracking()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentResourceIndex, journey?.resources, progress, markingComplete])

  // Handle visibility change (pause tracking when tab is hidden)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Tab is hidden, stop tracking
        stopTimeTracking()
      } else if (journey?.resources?.[currentResourceIndex]) {
        // Tab is visible, resume tracking
        startTimeTracking(journey.resources[currentResourceIndex].id)
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentResourceIndex, journey?.resources])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTimeTracking()
    }
  }, [])

  const loadJourneyData = async () => {
    try {
      const [journeyData, progressData] = await Promise.all([
        apiClient.getJourney(journeyId),
        apiClient.getProgressSummary(journeyId).catch(() => null)
      ])
      setJourney(journeyData)
      setProgress(progressData)

      // Determine initial resource index
      let initialIndex = 0

      if (progressData && journeyData?.resources) {
        // Find the latest completed resource
        let latestCompletedIndex = -1
        for (let i = 0; i < journeyData.resources.length; i++) {
          const resourceId = journeyData.resources[i].id
          const resourceProgress = progressData.progress_by_resource[resourceId]
          if (resourceProgress?.completed === 2) {
            latestCompletedIndex = i
          }
        }

        // If we found a completed resource, start at the next one (or stay at last if it's the last)
        if (latestCompletedIndex >= 0) {
          initialIndex = Math.min(latestCompletedIndex + 1, journeyData.resources.length - 1)
        } else {
          // No completed resources, try to use last position
          try {
            const lastPos = await apiClient.getLastPosition(journeyId)
            if (lastPos.last_position !== null && lastPos.last_position !== undefined) {
              initialIndex = lastPos.last_position
            }
          } catch (error) {
            console.error('Error loading last position:', error)
          }
        }
      } else {
        // Fallback to last position if no progress data
        try {
          const lastPos = await apiClient.getLastPosition(journeyId)
          if (lastPos.last_position !== null && lastPos.last_position !== undefined) {
            initialIndex = lastPos.last_position
          }
        } catch (error) {
          console.error('Error loading last position:', error)
        }
      }

      setCurrentResourceIndex(initialIndex)
    } catch (error) {
      console.error('Failed to load journey:', error)
    } finally {
      setLoading(false)
    }
  }

  // Start tracking time for a resource
  const startTimeTracking = (resourceId: string) => {
    // Stop previous tracking if any
    stopTimeTracking()

    // Skip if we're currently marking this resource as complete/incomplete
    if (skipTimeTrackingRef.current === resourceId) {
      console.log('Skipping time tracking - completion status being updated:', resourceId)
      return
    }

    // Don't mark as in progress if already completed
    // But allow tracking for incomplete resources (completed = 0 or 1)
    const resourceProgress = progress?.progress_by_resource[resourceId]
    if (resourceProgress?.completed === 2) {
      console.log('Resource already completed, skipping in-progress status:', resourceId)
      return
    }

    timeTrackingRef.current.startTime = Date.now()
    timeTrackingRef.current.resourceId = resourceId

    // Mark as in progress (only if not already completed)
    // This will set completed to 1 if it's currently 0
    apiClient.markResourceInProgress(journeyId, resourceId).catch(console.error)

    // Update time every 30 seconds
    timeTrackingRef.current.intervalId = setInterval(() => {
      if (timeTrackingRef.current.startTime && timeTrackingRef.current.resourceId) {
        const timeSpent = Math.floor((Date.now() - timeTrackingRef.current.startTime) / 60000) // minutes
        if (timeSpent > 0) {
          apiClient.updateTimeSpent(journeyId, timeTrackingRef.current.resourceId, timeSpent).catch(console.error)
        }
      }
    }, 30000) // Every 30 seconds
  }

  // Stop tracking time and save final time
  const stopTimeTracking = async () => {
    if (timeTrackingRef.current.intervalId) {
      clearInterval(timeTrackingRef.current.intervalId)
      timeTrackingRef.current.intervalId = null
    }

    if (timeTrackingRef.current.startTime && timeTrackingRef.current.resourceId) {
      const timeSpent = Math.floor((Date.now() - timeTrackingRef.current.startTime) / 60000) // minutes
      if (timeSpent > 0) {
        try {
          await apiClient.updateTimeSpent(journeyId, timeTrackingRef.current.resourceId, timeSpent)
        } catch (error) {
          console.error('Error updating time spent:', error)
        }
      }
      timeTrackingRef.current.startTime = null
      timeTrackingRef.current.resourceId = null
    }
  }

  const savePosition = async (index: number) => {
    if (journey?.resources?.[index]) {
      // Stop tracking previous resource
      await stopTimeTracking()

      // Start tracking new resource
      startTimeTracking(journey.resources[index].id)
    }
  }

  const handleMarkComplete = async (resourceId: string, e?: React.MouseEvent) => {
    e?.preventDefault()
    e?.stopPropagation()

    // Prevent multiple simultaneous requests
    if (markingComplete === resourceId) {
      console.log('Already processing completion toggle for this resource')
      return
    }

    const isCurrentlyCompleted = isResourceCompleted(resourceId)

    try {
      setMarkingComplete(resourceId)
      skipTimeTrackingRef.current = resourceId // Prevent time tracking from interfering

      console.log('Toggling resource completion:', {
        journeyId,
        resourceId,
        resourceType: currentResource?.type,
        isCurrentlyCompleted,
        willToggleTo: isCurrentlyCompleted ? 'incomplete' : 'complete'
      })

      // Stop time tracking before marking complete to prevent race condition
      stopTimeTracking()

      // Toggle: if completed, mark as incomplete; if not completed, mark as complete
      const result = isCurrentlyCompleted
        ? await apiClient.markResourceIncomplete(journeyId, resourceId)
        : await apiClient.markResourceCompleted(journeyId, resourceId)
      console.log('Toggle result:', result)

      // Reload progress immediately to update UI
      // Try multiple times with increasing delays to handle race conditions
      let progressData = null
      const expectedCompleted = isCurrentlyCompleted ? 0 : 2
      let retries = 5 // Increased retries
      while (retries > 0) {
        try {
          // Increasing delay to ensure backend has processed the commit and any race conditions are resolved
          const delay = 300 * (6 - retries) // 300ms, 600ms, 900ms, 1200ms, 1500ms
          await new Promise(resolve => setTimeout(resolve, delay))

          progressData = await apiClient.getProgressSummary(journeyId)
          const resourceProgress = progressData.progress_by_resource[resourceId]

          console.log(`Progress fetch attempt ${6 - retries}:`, {
            resourceId,
            completed: resourceProgress?.completed,
            expected: expectedCompleted,
            delay: `${delay}ms`
          })

          // If we got the correct value, break early
          if (resourceProgress?.completed === expectedCompleted) {
            console.log(`Progress correctly updated to ${expectedCompleted === 2 ? 'completed (2)' : 'incomplete (0)'}`)
            break
          }

          retries--
          if (retries === 0) {
            console.warn('Progress still shows incorrect value after retries:', {
              resourceId,
              completed: resourceProgress?.completed,
              expected: expectedCompleted
            })
            // Force a full reload as last resort
            await loadJourneyData()
            return // Exit early since loadJourneyData will update state
          }
        } catch (progressError) {
          console.error('Failed to reload progress:', progressError)
          retries--
          if (retries === 0) {
            // Still reload full journey data as fallback
            await loadJourneyData()
            return
          }
        }
      }

      if (progressData) {
        setProgress(progressData)
        console.log('Final progress state:', {
          resourceId,
          completed: progressData.progress_by_resource[resourceId]?.completed,
          allProgress: progressData.progress_by_resource
        })

        // If we marked the current resource as incomplete, restart time tracking
        if (currentResource?.id === resourceId && expectedCompleted === 0) {
          // Small delay to ensure state is fully updated, then clear skip flag
          setTimeout(() => {
            skipTimeTrackingRef.current = null
            startTimeTracking(resourceId)
          }, 100)
        } else {
          // Clear skip flag after a delay
          setTimeout(() => {
            skipTimeTrackingRef.current = null
          }, 500)
        }
      }
    } catch (error: any) {
      console.error('Failed to toggle completion:', error)
      console.error('Error details:', {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
        resourceId,
        journeyId,
        resourceType: currentResource?.type
      })
      // Show user-friendly error message with more details
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error'
      alert(`Failed to toggle resource completion: ${errorMessage}\n\nResource ID: ${resourceId}\nType: ${currentResource?.type}`)
    } finally {
      setMarkingComplete(null)
      // Clear skip flag after a delay to allow time tracking to resume
      setTimeout(() => {
        skipTimeTrackingRef.current = null
      }, 500)
    }
  }

  const handleNext = () => {
    if (journey?.resources && currentResourceIndex < journey.resources.length - 1) {
      const nextIndex = currentResourceIndex + 1
      setCurrentResourceIndex(nextIndex)
      savePosition(nextIndex)
    }
  }

  const handlePrevious = () => {
    if (currentResourceIndex > 0) {
      const prevIndex = currentResourceIndex - 1
      setCurrentResourceIndex(prevIndex)
      savePosition(prevIndex)
    }
  }

  const handleResourceClick = (index: number) => {
    setCurrentResourceIndex(index)
    savePosition(index)
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading your learning journey..." />
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
            <h2 className="text-2xl font-bold mb-2">Journey Not Ready</h2>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              This learning journey is not ready yet. Please check back later.
            </p>
            <Button variant="primary" onClick={() => router.push('/my-learning')}>
              Back to My Learning
            </Button>
          </Card>
        </div>
      </div>
    )
  }

  const currentResource = journey.resources[currentResourceIndex]
  const isResourceCompleted = (resourceId: string) => {
    if (!progress || !resourceId) return false
    const resourceProgress = progress.progress_by_resource[resourceId]
    return resourceProgress?.completed === 2
  }

  return (
    <div className="fixed top-16 inset-x-0 bottom-0 bg-slate-50 dark:bg-slate-900 overflow-hidden">
      <div className="flex h-full overflow-hidden relative">
        {/* Desktop Roadmap Sidebar (in flex layout) */}
        <div className={`hidden lg:block ${roadmapOpen ? 'w-80' : 'w-12'} transition-all duration-300 overflow-hidden flex-shrink-0 h-full relative z-10`}>
          <RoadmapSidebar
            journey={journey}
            currentResourceIndex={currentResourceIndex}
            onResourceClick={handleResourceClick}
            progressByResource={progress?.progress_by_resource}
            isOpen={roadmapOpen}
            onToggle={() => setRoadmapOpen(!roadmapOpen)}
          />
        </div>

        {/* Mobile Roadmap Sidebar (overlay) */}
        {roadmapOpen && (
          <>
            {/* Mobile backdrop when roadmap is open - behind sidebar */}
            <div
              className="lg:hidden fixed top-16 left-80 right-0 bottom-0 bg-black/50 backdrop-blur-md z-40"
              onClick={() => setRoadmapOpen(false)}
            />
            <div className="lg:hidden fixed top-16 left-0 bottom-0 w-80 transition-all duration-300 overflow-hidden h-full z-50 shadow-2xl bg-white dark:bg-slate-800">
              <RoadmapSidebar
                journey={journey}
                currentResourceIndex={currentResourceIndex}
                onResourceClick={handleResourceClick}
                progressByResource={progress?.progress_by_resource}
                isOpen={roadmapOpen}
                onToggle={() => setRoadmapOpen(!roadmapOpen)}
              />
            </div>
          </>
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0 w-full relative z-10">
          {/* Header */}
          <div className="flex-shrink-0 px-4 sm:px-6 py-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <Button
                  variant="ghost"
                  size="sm"
                  icon={<ArrowLeft className="w-4 h-4" />}
                  onClick={() => router.push('/my-learning')}
                  className="flex-shrink-0"
                >
                  <span className="hidden sm:inline">Back to My Learning</span>
                  <span className="sm:hidden">Back</span>
                </Button>
                <button
                  onClick={() => setRoadmapOpen(!roadmapOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 lg:hidden flex-shrink-0"
                  title={roadmapOpen ? 'Hide roadmap' : 'Show roadmap'}
                >
                  <Map className="w-5 h-5" />
                  <span className="text-sm font-medium">{roadmapOpen ? 'Hide' : 'Roadmap'}</span>
                </button>
                <div className="flex-1 min-w-0">
                  <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 truncate">{journey.topic}</h1>
                  <p className="text-sm text-slate-600 dark:text-slate-400 truncate">{journey.goal}</p>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {progress && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">Overall Progress</span>
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    {progress.completed_count} / {progress.total_resources} completed
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-600 to-cyan-600 transition-all duration-500"
                    style={{ width: `${progress.completion_percentage}%` }}
                  />
                </div>
              </div>
            )}

            {/* Resource Navigation */}
            <div className="mt-4 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                icon={<ChevronLeft className="w-4 h-4" />}
                onClick={handlePrevious}
                disabled={currentResourceIndex === 0}
              >
                Previous
              </Button>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Resource {currentResourceIndex + 1} of {journey.resources.length}
              </span>
              <Button
                variant="outline"
                size="sm"
                icon={<ChevronRight className="w-4 h-4" />}
                onClick={handleNext}
                disabled={currentResourceIndex === journey.resources.length - 1}
              >
                Next
              </Button>
            </div>
          </div>

          {/* Resource Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {/* Title First */}
              <Card className="mb-6">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-3 flex-wrap">
                      {currentResource.type === 'video' ? (
                        <Video className="w-5 h-5 text-teal-600 dark:text-teal-400 flex-shrink-0" />
                      ) : currentResource.type === 'blog' ? (
                        <FileText className="w-5 h-5 text-teal-600 dark:text-teal-400 flex-shrink-0" />
                      ) : (
                        <BookOpen className="w-5 h-5 text-teal-600 dark:text-teal-400 flex-shrink-0" />
                      )}
                      <Badge variant="primary">{currentResource.type}</Badge>
                      <Badge variant="secondary">{currentResource.difficulty}</Badge>
                      {currentResource.estimated_time > 0 && (
                        <div className="flex items-center gap-1 text-sm text-slate-600 dark:text-slate-400">
                          <Clock className="w-4 h-4" />
                          {currentResource.estimated_time} min
                        </div>
                      )}
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100 break-words">
                      {currentResource.title}
                    </h2>
                  </div>
                  <div className="flex flex-col gap-2 relative z-10 flex-shrink-0 sm:w-auto w-full">
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('Button clicked for resource:', currentResource.id, currentResource.type)
                        handleMarkComplete(currentResource.id, e)
                      }}
                      type="button"
                      disabled={markingComplete === currentResource.id}
                      className={`px-3 py-2 rounded-lg transition-all flex items-center justify-center gap-2 text-sm font-medium relative z-10 pointer-events-auto disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap ${isResourceCompleted(currentResource.id)
                        ? 'bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800'
                        : 'hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                        }`}
                      title={isResourceCompleted(currentResource.id) ? 'Mark as incomplete' : 'Mark as completed'}
                    >
                      {markingComplete === currentResource.id ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin text-slate-400 dark:text-slate-500" />
                          <span>Updating...</span>
                        </>
                      ) : isResourceCompleted(currentResource.id) ? (
                        <>
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                          <span>Completed</span>
                        </>
                      ) : (
                        <>
                          <Circle className="w-5 h-5 text-slate-400 dark:text-slate-500" />
                          <span>Mark Complete</span>
                        </>
                      )}
                    </button>
                    <a
                      href={currentResource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 rounded-lg transition-all flex items-center justify-center gap-2 text-sm font-medium border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400 whitespace-nowrap"
                    >
                      <ExternalLink className="w-5 h-5" />
                      <span>Open Source</span>
                    </a>
                  </div>
                </div>
              </Card>

              {/* Video or Article Content */}
              {currentResource.type === 'video' ? (
                <>
                  {/* Video Second */}
                  <VideoEmbed
                    url={currentResource.url}
                    title={currentResource.title}
                    className="mb-6"
                  />
                  {/* Description Third */}
                  {currentResource.summary && (
                    <Card className="mb-6">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">Description</h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                        {currentResource.summary}
                      </p>
                    </Card>
                  )}
                </>
              ) : (
                <ArticleViewer
                  resourceId={currentResource.id}
                  resourceUrl={currentResource.url}
                  resourceType={currentResource.type}
                />
              )}
            </div>
          </div>
        </div>

        {/* Chatbot Overlay */}
        <ChatbotOverlay
          journeyId={journeyId}
          resourceId={currentResource.id}
        />
      </div>
    </div>
  )
}
