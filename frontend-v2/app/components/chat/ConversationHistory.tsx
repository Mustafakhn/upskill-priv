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

  // Collapsed state
  if (!isOpen) {
    return (
      <div className="h-full w-full flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col">
        <button
          onClick={onToggle}
          className="w-full h-14 flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200 group relative border-b border-slate-200 dark:border-slate-700"
          title="Chat History"
        >
          <MessageSquare className="w-5 h-5 text-slate-400 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors" />
          <div className="absolute left-full ml-2 px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-slate-100 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-50 shadow-lg">
            <div className="font-medium">Chat History</div>
            {conversations.length > 0 && (
              <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{conversations.length} conversations</div>
            )}
          </div>
        </button>
      </div>
    )
  }

  return (
    <>
      {/* Overlay for mobile - positioned to not cover sidebar */}
      {isOpen && onToggle && (
        <div
          className="fixed top-0 right-0 bottom-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          style={{ left: '320px' }}
          onClick={onToggle}
        />
      )}

      {/* Sidebar - higher z-index than overlay */}
      <aside className="h-full w-full flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col relative z-50">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between flex-shrink-0">
          <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">Chat History</h2>
          {onToggle && (
            <button
              onClick={onToggle}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
              title="Collapse history"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* New Chat Button */}
        {onNewChat && (
          <div className="px-5 py-3 border-b border-slate-200 dark:border-slate-700">
            <button
              onClick={onNewChat}
              className="w-full px-4 py-2 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md"
            >
              + New Chat
            </button>
          </div>
        )}

        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto py-2 min-h-0">
          {loading ? (
            <div className="p-4 text-center">
              <Loading size="sm" text="Loading..." />
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center">
              <p className="text-slate-600 dark:text-slate-400 text-sm">No conversations yet</p>
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
                    w-full text-left p-3 rounded-lg transition-all duration-150 border
                    ${
                      currentConversationId === conv.id
                        ? 'bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800 shadow-sm'
                        : 'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-700 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{formatConversationTime(conv.updated_at)}</span>
                    {conv.journey_id && (
                      <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 rounded text-xs font-medium">
                        Done
                      </span>
                    )}
                  </div>
                  <p className={`text-sm truncate font-medium ${
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
    </>
  )
}

