'use client'

import React, { useEffect, useState } from 'react'
import { MessageSquare, ChevronLeft } from 'lucide-react'
import { apiClient, Conversation } from '@/app/services/api'
import Loading from '../common/Loading'
import { formatConversationTime } from '@/app/utils/time'

interface ConversationHistoryProps {
  currentConversationId: string | null
  onConversationSelect: (conversationId: string) => void
  isOpen?: boolean
  onToggle?: () => void
  onNewChat?: () => void
}

export default function ConversationHistory({ 
  currentConversationId, 
  onConversationSelect, 
  isOpen = true, 
  onToggle,
  onNewChat
}: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  const fetchConversations = async () => {
    setLoading(true)
    try {
      const data = await apiClient.getUserConversations()
      // Sort by updated_at descending (most recent first)
      const sorted = Array.isArray(data) 
        ? data.sort((a, b) => 
            new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
          )
        : []
      setConversations(sorted)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      setConversations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConversations()
  }, [])

  // Refresh when conversation changes (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentConversationId) {
        fetchConversations()
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [currentConversationId])


  const getPreview = (conv: Conversation) => {
    if (conv.journey_id) {
      return 'Journey created'
    }
    return 'Chat conversation'
  }

  // Always show expanded state (no collapsed state)
  return (
      <aside className="h-full w-full flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-teal-600 dark:text-teal-400" />
            <h2 className="text-sm sm:text-base font-semibold text-slate-900 dark:text-slate-100">Chat History</h2>
          </div>
          {onToggle && (
            <button
              onClick={onToggle}
              className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              title="Collapse history"
            >
              <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          )}
        </div>

        {/* New Chat Button */}
        {onNewChat && (
          <div className="px-4 py-2 sm:py-3 border-b border-slate-200 dark:border-slate-700">
            <button
              onClick={onNewChat}
              className="w-full px-3 py-2 sm:px-4 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-white rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md"
            >
              + New Chat
            </button>
          </div>
        )}

        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden py-2 min-h-0" style={{ WebkitOverflowScrolling: 'touch' }}>
          {loading ? (
            <div className="p-3 sm:p-4 text-center">
              <Loading size="sm" text="Loading..." />
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-3 sm:p-4 text-center">
              <p className="text-slate-600 dark:text-slate-400 text-xs sm:text-sm">No conversations yet</p>
            </div>
          ) : (
            <div className="space-y-1 px-2">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => {
                    onConversationSelect(conv.id)
                    if (typeof window !== 'undefined' && window.innerWidth < 1024 && onToggle) {
                      onToggle()
                    }
                  }}
                  className={`
                    w-full text-left p-2.5 sm:p-3 rounded-lg transition-all duration-150 border
                    ${
                      currentConversationId === conv.id
                        ? 'bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800 shadow-sm'
                        : 'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-700 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex items-center justify-between mb-1 sm:mb-1.5">
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{formatConversationTime(conv.updated_at)}</span>
                    {conv.journey_id && (
                      <span className="px-1.5 sm:px-2 py-0.5 bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 rounded text-xs font-medium">
                        Done
                      </span>
                    )}
                  </div>
                  <p className={`text-xs sm:text-sm truncate font-medium ${
                    currentConversationId === conv.id 
                      ? 'text-teal-600 dark:text-teal-400' 
                      : 'text-slate-700 dark:text-slate-300'
                  }`}>{getPreview(conv)}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>
  )
}

