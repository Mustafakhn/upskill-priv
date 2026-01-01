'use client'

import React from 'react'
import { CheckCircle, Circle, Video, FileText, BookOpen, Clock } from 'lucide-react'
import { Journey, Resource } from '@/app/services/api'
import Badge from '../common/Badge'
import Card from '../common/Card'

interface LearningRoadmapProps {
  journey: Journey
  currentResourceIndex?: number
  onResourceClick?: (index: number) => void
  progressByResource?: Record<string, { completed: number; time_spent_minutes: number }>
  className?: string
  hideEstimatedTime?: boolean
}

export default function LearningRoadmap({
  journey,
  currentResourceIndex,
  onResourceClick,
  progressByResource,
  className = '',
  hideEstimatedTime = false
}: LearningRoadmapProps) {
  const resourceMap = new Map(journey.resources?.map((r, idx) => [r.id, { resource: r, index: idx }]) || [])
  const resourcesInSections = new Set<string>()

  // Build sections with all resources included
  let sections: Array<{
    name: string
    description?: string
    resources: Array<Resource & { globalIndex: number }>
  }> = []

  if (journey.sections && journey.sections.length > 0) {
    sections = journey.sections
      .map(section => ({
        name: section.name,
        description: section.description,
        resources: section.resources
          .map(rid => resourceMap.get(rid))
          .filter((item): item is NonNullable<typeof item> => item !== undefined)
          .map(item => {
            resourcesInSections.add(item.resource.id)
            return { ...item.resource, globalIndex: item.index }
          })
      }))
      .filter(section => section.resources.length > 0)

    // Add resources not in any section to the last section (or create a new one)
    const allResourceIds = new Set(journey.resources?.map(r => r.id) || [])
    const missingResources = Array.from(allResourceIds).filter(id => !resourcesInSections.has(id))

    if (missingResources.length > 0) {
      const missingResourcesList = missingResources
        .map(rid => resourceMap.get(rid))
        .filter((item): item is NonNullable<typeof item> => item !== undefined)
        .map(item => ({ ...item.resource, globalIndex: item.index }))
        .sort((a, b) => a.globalIndex - b.globalIndex) // Sort by original order

      if (sections.length > 0) {
        // Append to last section
        sections[sections.length - 1].resources.push(...missingResourcesList)
        // Sort all resources in the last section by globalIndex
        sections[sections.length - 1].resources.sort((a, b) => a.globalIndex - b.globalIndex)
      } else {
        // Create a default section with all missing resources
        sections.push({
          name: 'Additional Resources',
          description: 'Additional learning materials',
          resources: missingResourcesList
        })
      }
    }
  } else {
    // No sections defined, show all resources in a default section
    sections = [{
      name: 'Learning Path',
      description: 'Your personalized journey',
      resources: (journey.resources || []).map((r, idx) => ({ ...r, globalIndex: idx }))
    }]
  }

  const getResourceStatus = (resourceId: string, globalIndex: number): 'completed' | 'active' | 'pending' => {
    if (progressByResource?.[resourceId]?.completed === 2) return 'completed'
    if (currentResourceIndex === globalIndex) return 'active'
    if (progressByResource?.[resourceId]?.completed === 1) return 'active'
    return 'pending'
  }

  const overallProgress = progressByResource
    ? Math.round(
      (Object.values(progressByResource).filter(p => p.completed === 2).length /
        (journey.resources?.length || 1)) * 100
    )
    : 0


  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4" />
      case 'blog':
        return <FileText className="w-4 h-4" />
      case 'doc':
        return <BookOpen className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  return (
    <div className={className}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">Learning Roadmap</h2>
        <p className="text-slate-600 dark:text-slate-400 mb-4">Your structured path to mastery</p>

        {/* Overall progress */}
        {progressByResource && (
          <Card className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wide">Overall Progress</h3>
              <span className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
                {overallProgress}%
              </span>
            </div>
            <div className="h-2.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-teal-600 to-cyan-600 transition-all duration-500"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-slate-600 dark:text-slate-400">
              {Object.values(progressByResource).filter(p => p.completed === 2).length} of {journey.resources?.length || 0} resources completed
            </div>
          </Card>
        )}
      </div>

      <div className="space-y-8">
        {sections.map((section, sectionIndex) => {
          const sectionProgress = section.resources.filter(r =>
            getResourceStatus(r.id, r.globalIndex) === 'completed'
          ).length
          const sectionTotal = section.resources.length
          const sectionPercentage = sectionTotal > 0 ? (sectionProgress / sectionTotal) * 100 : 0

          // Calculate progress height for vertical line - based on completed resources
          const completedCount = section.resources.filter(r =>
            getResourceStatus(r.id, r.globalIndex) === 'completed'
          ).length

          return (
            <div key={sectionIndex} className="relative">
              {/* Section header */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{section.name}</h3>
                    {section.description && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{section.description}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                      {sectionProgress} / {sectionTotal}
                    </div>
                    <div className="text-xs text-slate-600 dark:text-slate-400">completed</div>
                  </div>
                </div>
                <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-600 to-cyan-600 transition-all duration-500"
                    style={{ width: `${sectionPercentage}%` }}
                  />
                </div>
              </div>

              {/* Resources timeline - Stepper style */}
              <div className="relative bg-slate-50/50 dark:bg-slate-800/30 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
                {/* Background gradient effect */}
                <div className="absolute inset-0 rounded-2xl overflow-hidden opacity-20 pointer-events-none">
                  <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-gradient-to-br from-teal-600 to-cyan-600 blur-3xl"></div>
                  <div className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-gradient-to-tl from-cyan-600 to-teal-600 blur-3xl"></div>
                </div>

                <div className="relative">
                  <ol className="relative pl-4">
                    {(() => {
                      const totalItems = section.resources.length
                      if (totalItems === 0) return null

                      // Count completed resources
                      const completedCount = section.resources.filter(r =>
                        getResourceStatus(r.id, r.globalIndex) === 'completed'
                      ).length

                      // Calculate progress percentage: 0% to 100%
                      // Each resource represents (100 / totalItems)% of progress
                      const progressPercentage = totalItems > 0
                        ? (completedCount / totalItems) * 100
                        : 0

                      // Calculate line positioning
                      // Dots are centered vertically in each li with top-1/2 -translate-y-1/2
                      // Each li has mb-10 (2.5rem) spacing except the last one
                      // The line should span from center of first dot to center of last dot
                      // Since dots are centered, we'll position the line to start from the first li's center
                      // and end at the last li's center
                      // We'll use CSS to target the first and last li, or calculate based on structure

                      // Better approach: Use a ref or calculate the actual positions
                      // For now, we'll use a conservative estimate: assume average li height
                      // and position line accordingly

                      return (
                        <>
                          {/* Background line - full height from first to last dot center */}
                          {totalItems > 1 && (
                            <div
                              className="absolute w-0.5 bg-slate-200 dark:bg-slate-700"
                              style={{
                                left: '1rem',
                                // Position line to start from first dot center and end at last dot center
                                // Dots are centered with top-1/2, so they're approximately at the vertical center of each li
                                // We need to estimate where the first and last dot centers are
                                // Since li heights vary, we'll use a conservative approach:
                                // Start from a small offset from top (where first dot center likely is)
                                // End with a small offset from bottom (where last dot center likely is)
                                // Adjust these values based on typical li height
                                top: '2.5rem', // Approximate center of first li (assuming ~3rem height)
                                bottom: '2.5rem' // Approximate center of last li
                              }}
                            />
                          )}

                          {/* Progress line - fills from 0% to current progress percentage */}
                          {totalItems > 1 && progressPercentage > 0 && (
                            <div
                              className="absolute w-0.5 bg-gradient-to-b from-teal-600 via-cyan-600 to-teal-600 transition-all duration-700 ease-out z-0"
                              style={{
                                left: '1rem',
                                top: '2.5rem',
                                // Height as percentage of the total line height
                                // The background line spans from top: 1.5rem to bottom: 1.5rem
                                // So available height = 100% - 3rem (1.5rem top + 1.5rem bottom)
                                height: `calc((100% - 3rem) * ${progressPercentage} / 100)`
                              }}
                            />
                          )}
                        </>
                      )
                    })()}

                    {section.resources.map((resource, resourceIndex) => {
                      const status = getResourceStatus(resource.id, resource.globalIndex)
                      const isCompleted = status === 'completed'
                      const isActive = status === 'active'
                      const isPending = status === 'pending'
                      const isLast = resourceIndex === section.resources.length - 1

                      // Get icon based on resource type and status
                      const getResourceIcon = () => {
                        if (isCompleted) {
                          return (
                            <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                          )
                        }
                        if (resource.type === 'video') {
                          return (
                            <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                              <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0 0 10 9.87v4.263a1 1 0 0 0 1.555.832l3.197-2.132a1 1 0 0 0 0-1.664Z" />
                              <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                            </svg>
                          )
                        }
                        if (resource.type === 'blog') {
                          return (
                            <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                              <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 9h3m-3 3h3m-3 3h3m-6 1c-.306-.613-.933-1-1.618-1H7.618c-.685 0-1.312.387-1.618 1M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm7 5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z" />
                            </svg>
                          )
                        }
                        return (
                          <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 4h3a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3m0 3h6m-3 5h3m-6 0h.01M12 16h3m-6 0h.01M10 3v4h4V3h-4Z" />
                          </svg>
                        )
                      }

                      return (
                        <li
                          key={resource.id}
                          className={`${isLast ? '' : 'mb-10'} pl-12 cursor-pointer group transition-all duration-300 relative`}
                          onClick={() => onResourceClick?.(resource.globalIndex)}
                        >
                          <span className={`absolute flex items-center justify-center w-8 h-8 rounded-full -left-4 top-1/2 -translate-y-1/2 ring-4 z-20 ${isCompleted
                            ? 'text-white bg-gradient-to-br from-teal-600 to-cyan-600 ring-white dark:ring-slate-900 shadow-[0_0_20px_rgba(20,184,166,0.6),0_0_40px_rgba(20,184,166,0.4)] dark:shadow-[0_0_20px_rgba(94,234,212,0.6),0_0_40px_rgba(94,234,212,0.4)]'
                            : isActive || (resource.type === 'blog' || resource.type === 'doc') || resource.type === 'video'
                              ? 'text-white bg-gradient-to-br from-teal-600 to-cyan-600 ring-white dark:ring-slate-900 shadow-lg shadow-teal-500/50'
                              : 'text-slate-600 dark:text-slate-400 bg-slate-200 dark:bg-slate-700 ring-white dark:ring-slate-900'
                            }`}>
                            {getResourceIcon()}
                          </span>
                          <div className={`transition-all duration-300 ${isPending ? 'opacity-60' : 'opacity-100'
                            }`}>
                            <h3 className={`font-medium leading-tight text-slate-900 dark:text-slate-100 ${isCompleted
                              ? 'text-teal-600 dark:text-teal-400'
                              : isActive
                                ? 'text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400'
                                : ''
                              }`}>
                              {resource.title}
                            </h3>
                            <div className="flex items-center gap-2 mt-1 text-sm text-slate-600 dark:text-slate-400">
                              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${resource.type === 'video'
                                ? 'bg-teal-50 dark:bg-teal-900/30 border-teal-200 dark:border-teal-800 text-teal-600 dark:text-teal-400'
                                : resource.type === 'blog'
                                  ? 'bg-cyan-50 dark:bg-cyan-900/30 border-cyan-200 dark:border-cyan-800 text-cyan-600 dark:text-cyan-400'
                                  : 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-600 dark:text-green-400'
                                }`}>
                                {resource.type === 'video' ? 'Video' : resource.type === 'blog' ? 'Article' : 'Doc'}
                              </span>
                              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${resource.difficulty === 'beginner'
                                ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-600 dark:text-green-400'
                                : resource.difficulty === 'intermediate'
                                  ? 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800 text-yellow-600 dark:text-yellow-400'
                                  : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-600 dark:text-red-400'
                                }`}>
                                {resource.difficulty}
                              </span>
                              {/* {!hideEstimatedTime && resource.estimated_time && resource.estimated_time > 0 && (
                                <span className="text-xs flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {resource.estimated_time} min
                                </span>
                              )} */}
                            </div>
                          </div>
                        </li>
                      )
                    })}
                  </ol>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

