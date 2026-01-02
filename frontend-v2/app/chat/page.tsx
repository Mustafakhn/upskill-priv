'use client'

import React, { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { MessageSquare, Send, Loader2 } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Loading from '../components/common/Loading'
import { apiClient, ChatMessage } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import ConversationHistory from '../components/chat/ConversationHistory'

export default function ChatPage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading, user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/chat')
      return
    }
  }, [isAuthenticated, authLoading, router])

  const [refreshKey, setRefreshKey] = useState(0)

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    const messageText = input.trim()
    setInput('')
    setLoading(true)

    try {
      let response
      if (messages.length === 0 && !conversationId) {
        // Start new conversation
        response = await apiClient.startChat(messageText, [])
      } else {
        // Continue existing conversation
        response = await apiClient.respondToChat(messageText, messages, conversationId || undefined)
      }

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.response || response.answer,
        timestamp: new Date().toISOString()
      }

      setMessages([...newMessages, aiMessage])

      if (response.conversation_id) {
        setConversationId(response.conversation_id)
        setSelectedConversationId(response.conversation_id)
        // Refresh conversation list
        setRefreshKey(prev => prev + 1)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages([...newMessages, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleConversationSelect = async (convId: string) => {
    setSelectedConversationId(convId)
    setConversationId(convId)
    setMessages([])
    setLoading(true)

    try {
      const history = await apiClient.getChatHistory(convId)
      if (history && history.messages) {
        setMessages(history.messages)
      } else if (history && Array.isArray(history)) {
        // If API returns array directly
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
  }

  if (authLoading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="fixed top-16 inset-x-0 bottom-0 bg-slate-50 dark:bg-slate-900 overflow-hidden">
      {/* Mobile backdrop when sidebar is open */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed top-16 left-80 bottom-0 right-0 bg-black/50 backdrop-blur-md z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex h-full overflow-hidden relative">
        {/* Desktop Sidebar (in flex layout) */}
        <div className={`hidden lg:block ${sidebarOpen ? 'w-80' : 'w-12'} transition-all duration-300 overflow-hidden flex-shrink-0 h-full relative z-10 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700`}>
          <ConversationHistory
            key={refreshKey}
            currentConversationId={selectedConversationId}
            onConversationSelect={handleConversationSelect}
            onNewChat={handleNewChat}
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />
        </div>

        {/* Mobile Sidebar (overlay) */}
        {sidebarOpen && (
          <div className="lg:hidden fixed top-16 left-0 bottom-0 w-80 transition-all duration-300 overflow-hidden h-full z-50 shadow-2xl bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700">
            <ConversationHistory
              key={refreshKey}
              currentConversationId={selectedConversationId}
              onConversationSelect={handleConversationSelect}
              onNewChat={handleNewChat}
              isOpen={sidebarOpen}
              onToggle={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        )}

        {/* Main chat area */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0 w-full relative z-10">
          {/* Header */}
          <div className="flex-shrink-0 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="flex items-center justify-between max-w-4xl mx-auto">
              <div className="flex items-center gap-2 sm:gap-3">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-2 flex-shrink-0"
                  title={sidebarOpen ? 'Hide history' : 'Show history'}
                >
                  <MessageSquare className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                  <span className="font-medium text-sm lg:hidden">{sidebarOpen ? 'Hide' : 'History'}</span>
                </button>
                <h1 className="text-base sm:text-lg lg:text-xl font-semibold text-slate-900 dark:text-slate-100">AI Chat</h1>
              </div>
              {conversationId && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNewChat}
                  className="text-xs sm:text-sm"
                >
                  <span className="hidden sm:inline">New Chat</span>
                  <span className="sm:hidden">New</span>
                </Button>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8 min-h-0">
            <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
              {messages.length === 0 ? (
                <div className="text-center py-8 sm:py-12">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 rounded-xl bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center">
                    <MessageSquare className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
                  </div>
                  <h2 className="text-lg sm:text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    Start a conversation
                  </h2>
                  <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 px-4">
                    Ask me anything about learning or get help with your journey
                  </p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-start gap-2 sm:gap-3 lg:gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center shadow-lg">
                        <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] sm:max-w-[75%] rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 shadow-sm text-sm sm:text-base ${message.role === 'user'
                        ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white'
                        : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700'
                        }`}
                    >
                      <div className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</div>
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center">
                        <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                          You
                        </span>
                      </div>
                    )}
                  </div>
                ))
              )}
              {loading && (
                <div className="flex items-start gap-2 sm:gap-3 lg:gap-4 justify-start">
                  <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center shadow-lg">
                    <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
                  </div>
                  <div className="bg-white dark:bg-slate-800 px-3 py-2 sm:px-4 sm:py-3 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin text-teal-600 dark:text-teal-400" />
                      <span className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input */}
          <div className="flex-shrink-0 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
            <div className="max-w-4xl mx-auto">
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSendMessage()
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything..."
                  className="flex-1 input text-sm sm:text-base"
                  disabled={loading}
                />
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  icon={<Send className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
                  disabled={loading || !input.trim()}
                  className="text-xs sm:text-sm"
                >
                  <span className="hidden sm:inline">Send</span>
                  <span className="sm:hidden">Send</span>
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
