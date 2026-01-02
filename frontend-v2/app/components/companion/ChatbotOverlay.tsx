'use client'

import React, { useState } from 'react'
import { MessageCircle, X } from 'lucide-react'
import CompanionChat from './CompanionChat'
import Button from '../common/Button'

interface ChatbotOverlayProps {
  journeyId: number
  resourceId?: string
}

export default function ChatbotOverlay({ journeyId, resourceId }: ChatbotOverlayProps) {
  const [isOpen, setIsOpen] = useState(false)

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          variant="primary"
          size="lg"
          icon={<MessageCircle className="w-5 h-5" />}
          onClick={() => setIsOpen(true)}
          className="rounded-full shadow-lg hover:shadow-xl transition-all duration-300"
        >
          AI Companion
        </Button>
      </div>
    )
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
        onClick={() => setIsOpen(false)}
      />
      
      {/* Desktop: Floating window */}
      <div className="hidden lg:flex fixed bottom-6 right-6 w-96 h-[600px] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-2xl flex flex-col z-50">
        <div className="flex-shrink-0 px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center">
              <MessageCircle className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">AI Companion</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-hidden">
          <CompanionChat
            journeyId={journeyId}
            resourceId={resourceId}
            onClose={() => setIsOpen(false)}
          />
        </div>
      </div>

      {/* Mobile: Overlay chatbot */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 h-[85vh] bg-white dark:bg-slate-900 z-50 flex flex-col rounded-t-2xl shadow-2xl border-t border-slate-200 dark:border-slate-700 animate-slide-up">
        <div className="flex-shrink-0 px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center">
              <MessageCircle className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">AI Companion</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="flex-1 overflow-hidden">
          <CompanionChat
            journeyId={journeyId}
            resourceId={resourceId}
            onClose={() => setIsOpen(false)}
          />
        </div>
      </div>
    </>
  )
}

