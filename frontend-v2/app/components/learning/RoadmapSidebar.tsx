'use client'

import React from 'react'
import { X, Map } from 'lucide-react'
import LearningRoadmap from './LearningRoadmap'
import { Journey, ProgressSummary } from '@/app/services/api'

interface RoadmapSidebarProps {
  journey: Journey
  currentResourceIndex: number
  onResourceClick: (index: number) => void
  progressByResource?: ProgressSummary['progress_by_resource']
  isOpen?: boolean
  onToggle?: () => void
}

export default function RoadmapSidebar({
  journey,
  currentResourceIndex,
  onResourceClick,
  progressByResource,
  isOpen = true,
  onToggle
}: RoadmapSidebarProps) {
  // Collapsed state
  if (!isOpen) {
    return (
      <div className="h-full w-full flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col">
        <button
          onClick={onToggle}
          className="w-full h-14 flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200 group relative border-b border-slate-200 dark:border-slate-700"
          title="Roadmap"
        >
          <Map className="w-5 h-5 text-slate-400 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors" />
          <div className="absolute left-full ml-2 px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-slate-100 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-50 shadow-lg">
            <div className="font-medium">Roadmap</div>
          </div>
        </button>
      </div>
    )
  }

  // Expanded state
  return (
    <div className="h-full w-full flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col border-r border-slate-200 dark:border-slate-700">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Map className="w-5 h-5 text-teal-600 dark:text-teal-400" />
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Roadmap</h2>
        </div>
        {onToggle && (
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            title="Collapse roadmap"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Roadmap Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <LearningRoadmap
          journey={journey}
          currentResourceIndex={currentResourceIndex}
          onResourceClick={onResourceClick}
          progressByResource={progressByResource}
        />
      </div>
    </div>
  )
}

