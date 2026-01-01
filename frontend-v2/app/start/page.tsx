'use client'

import React, { useState, useEffect, Suspense, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Send, Sparkles, Loader2, MessageSquare } from 'lucide-react'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import Loading from '../components/common/Loading'
import ConversationHistory from '../components/chat/ConversationHistory'
import { apiClient, ChatMessage } from '../services/api'
import { useAuth } from '../hooks/useAuth'

function StartPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const topicFromUrl = searchParams.get('topic')
  const { isAuthenticated, loading: authLoading } = useAuth()

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isReady, setIsReady] = useState(false)
  const [journeyId, setJourneyId] = useState<number | null>(null)
  const [showFormatSelector, setShowFormatSelector] = useState(false)
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  const [exampleTopics, setExampleTopics] = useState<string[]>(['Learn Python', 'Master Guitar', 'Italian Cooking', 'Digital Marketing'])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Prevent body scroll when component mounts
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/start')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated && topicFromUrl && messages.length === 0) {
      handleSendMessage(topicFromUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topicFromUrl, isAuthenticated])

  // Fetch popular topics on mount
  useEffect(() => {
    const fetchPopularTopics = async () => {
      try {
        const topics = await apiClient.getPopularTopics()
        if (topics && topics.length > 0) {
          setExampleTopics(topics.slice(0, 4))
        }
      } catch (error) {
        console.error('Error fetching popular topics:', error)
        // Keep default topics on error
      }
    }
    if (isAuthenticated) {
      fetchPopularTopics()
    }
  }, [isAuthenticated])

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || input
    if (!text.trim() || loading) return

    const userMessage: ChatMessage = { role: 'user', content: text }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      let response
      if (messages.length === 0) {
        response = await apiClient.startChat(text, [])
      } else {
        response = await apiClient.respondToChat(text, messages, conversationId || undefined)
      }

      const assistantMessage: ChatMessage = { role: 'assistant', content: response.response }
      setMessages([...newMessages, assistantMessage])

      if (response.conversation_id) {
        setConversationId(response.conversation_id)
        setSelectedConversationId(response.conversation_id)
        // Refresh conversation list
        setRefreshKey(prev => prev + 1)
      }

      if (response.questions && response.questions.length > 0) {
        setSuggestions(response.questions)
        // Check if suggestions are about format - if so, show format selector
        const formatKeywords = ['video', 'article', 'documentation', 'format', 'prefer', 'reading', 'watching', 'tutorial', 'blog', 'doc']
        const isFormatRelated = response.questions.some((q: string) =>
          formatKeywords.some(keyword => q.toLowerCase().includes(keyword))
        )
        setShowFormatSelector(isFormatRelated)
      } else {
        setSuggestions([])
        setShowFormatSelector(false)
      }

      if (response.ready && response.journey_id) {
        setIsReady(true)
        setJourneyId(response.journey_id)
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages([...newMessages, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion)
  }

  const handleStartLearning = () => {
    if (journeyId) {
      router.push(`/journey/${journeyId}`)
    }
  }

  const handleConversationSelect = async (convId: string) => {
    setSelectedConversationId(convId)
    setConversationId(convId)
    setMessages([])
    setIsReady(false)
    setJourneyId(null)
    setLoading(true)

    try {
      const history = await apiClient.getChatHistory(convId)
      if (history && history.messages) {
        setMessages(history.messages)
        // Check if this conversation has a journey
        const conversations = await apiClient.getUserConversations()
        const conv = Array.isArray(conversations)
          ? conversations.find(c => c.id === convId)
          : null
        if (conv?.journey_id) {
          setIsReady(true)
          setJourneyId(conv.journey_id)
        }
      } else if (history && Array.isArray(history)) {
        setMessages(history)
      }
    } catch (error) {
      console.error('Error loading conversation:', error)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    setConversationId(null)
    setSelectedConversationId(null)
    setMessages([])
    setIsReady(false)
    setJourneyId(null)
    setSuggestions([])
  }

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen py-8 flex items-center justify-center">
        <Loading text="Loading..." />
      </div>
    )
  }

  return (
    <div className="fixed top-16 inset-x-0 bottom-0 flex overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-12'} transition-all duration-300 border-r border-slate-200 dark:border-slate-700 overflow-hidden flex-shrink-0`}>
        <ConversationHistory
          key={refreshKey}
          currentConversationId={selectedConversationId}
          onConversationSelect={handleConversationSelect}
          onNewChat={handleNewChat}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header - Fixed */}
        <div className="flex-shrink-0 px-4 sm:px-6 py-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
          <div className="flex items-center gap-3">
            {/* {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors lg:hidden"
              >
                <MessageSquare className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </button>
            )} */}
            <div className="text-center flex-1">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 text-sm font-medium mb-2">
                <Sparkles className="w-4 h-4" />
                AI Learning Assistant
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100">
                Let&apos;s Create Your Learning Journey
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                Tell me what you want to learn and I&apos;ll create a personalized roadmap for you
              </p>
            </div>
          </div>
        </div>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            {/* Chat Container */}
            {messages.length === 0 ? (
              <Card className="mb-3">
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Start a Conversation</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-4">
                    I&apos;ll ask you a few questions to understand your learning goals
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center max-w-md mx-auto">
                    {exampleTopics.map((topic) => (
                      <button
                        key={topic}
                        onClick={() => handleSendMessage(topic)}
                        className="px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-teal-50 dark:hover:bg-teal-900/20 hover:text-teal-600 dark:hover:text-teal-400 transition-all"
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                </div>
              </Card>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-start gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center shadow-lg">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${message.role === 'user'
                        ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white'
                        : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700'
                        }`}
                    >
                      <div className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</div>
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center">
                        <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                          You
                        </span>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex items-start gap-4 justify-start">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center shadow-lg">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-white dark:bg-slate-800 px-4 py-3 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-teal-600 dark:text-teal-400" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Ready to start - Fixed at bottom */}
        {isReady && journeyId && (
          <div className="flex-shrink-0 px-4 sm:px-6 py-3 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="max-w-4xl mx-auto">
              <Card className="bg-gradient-to-r from-teal-50 to-cyan-50 dark:from-teal-900/20 dark:to-cyan-900/20 border-teal-200 dark:border-teal-800">
                <div className="text-center py-3">
                  <h3 className="text-lg font-bold mb-1 text-teal-900 dark:text-teal-100">
                    🎉 Your Learning Journey is Ready!
                  </h3>
                  <p className="text-sm text-teal-700 dark:text-teal-300 mb-3">
                    I&apos;ve created a personalized roadmap with curated resources just for you
                  </p>
                  <Button variant="primary" size="lg" onClick={handleStartLearning}>
                    Start Learning Now
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Format Selection - Just above input (only show when format is being asked) */}
        {!isReady && messages.length > 0 && showFormatSelector && (
          <div className="flex-shrink-0 px-4 sm:px-6 py-2 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="max-w-4xl mx-auto">
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Preferred material type:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { label: 'Videos', value: 'I prefer video tutorials' },
                  { label: 'Articles', value: 'I prefer reading articles' },
                  { label: 'Documentation', value: 'I prefer documentation' },
                  { label: 'Mixed', value: 'I prefer a mix of all types' }
                ].map((format) => (
                  <button
                    key={format.label}
                    onClick={() => handleSuggestionClick(format.value)}
                    disabled={loading}
                    className="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 hover:border-teal-500 hover:text-teal-600 dark:hover:text-teal-400 transition-all disabled:opacity-50"
                  >
                    {format.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Suggestions - Just above input */}
        {suggestions.length > 0 && !isReady && (
          <div className="flex-shrink-0 px-4 sm:px-6 py-2 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="max-w-4xl mx-auto">
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Quick replies:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    disabled={loading}
                    className="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 hover:border-teal-500 hover:text-teal-600 dark:hover:text-teal-400 transition-all disabled:opacity-50"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input - Fixed at bottom */}
        {!isReady && (
          <div className="flex-shrink-0 px-4 sm:px-6 py-3 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type your message..."
                  disabled={loading}
                  className="input flex-1"
                />
                <Button
                  variant="primary"
                  onClick={() => handleSendMessage()}
                  disabled={loading || !input.trim()}
                  icon={loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                >
                  Send
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function StartPage() {
  return (
    <Suspense fallback={<Loading text="Loading..." />}>
      <StartPageContent />
    </Suspense>
  )
}

