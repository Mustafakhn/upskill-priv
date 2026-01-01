'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, X, FileText, Lightbulb, BookOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { apiClient } from '@/app/services/api'
import Button from '../common/Button'

interface CompanionChatProps {
  journeyId: number
  resourceId?: string
  onClose?: () => void
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  type?: 'answer' | 'summary' | 'quiz' | 'examples'
  quizAttemptId?: number
}

export default function CompanionChat({ journeyId, resourceId, onClose }: CompanionChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setShowQuickActions(false)
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await apiClient.askQuestion(journeyId, userMessage, resourceId)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        type: 'answer'
      }])
    } catch (error) {
      console.error('Error asking question:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = async (action: string, params?: { concept?: string }) => {
    setShowQuickActions(false)
    setIsLoading(true)

    try {
      let response: { resource_title?: string; summary?: string; examples?: Array<{ title: string; description: string; code_or_demo?: string }> }
      let content = ''
      let type: Message['type'] = 'answer'

      switch (action) {
        case 'summarize':
          if (!resourceId) {
            setMessages(prev => [...prev, {
              role: 'assistant',
              content: 'Please select a resource first to summarize.'
            }])
            setIsLoading(false)
            return
          }
          response = await apiClient.summarizeResource(resourceId)
          content = `**Summary of ${response.resource_title}:**\n\n${response.summary}`
          type = 'summary'
          break

        case 'quiz':
          const quizData = await apiClient.createQuiz(journeyId, {
            resource_id: resourceId,
            quiz_type: 'mcq',
            num_questions: 5
          })
          content = `I've created a quiz for you! Click the button below to start.`
          type = 'quiz'
          setMessages(prev => [...prev, {
            role: 'assistant',
            content,
            type: 'quiz',
            quizAttemptId: quizData.attempt_id
          }])
          setIsLoading(false)
          return

        case 'examples':
          if (!resourceId || !params?.concept) {
            setMessages(prev => [...prev, {
              role: 'assistant',
              content: 'Please specify a concept to generate examples for. You can ask: "Give me examples of [concept]"'
            }])
            setIsLoading(false)
            return
          }
          response = await apiClient.generateExamples(resourceId, params.concept, 3)
          const examplesContent = response.examples?.map((ex, idx: number) =>
            `**Example ${idx + 1}: ${ex.title}**\n${ex.description}${ex.code_or_demo ? `\n\n\`\`\`\n${ex.code_or_demo}\n\`\`\`` : ''}`
          ).join('\n\n---\n\n')
          content = `**Examples for "${params.concept}":**\n\n${examplesContent}`
          type = 'examples'
          break

        default:
          content = 'Unknown action'
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content,
        type
      }])
    } catch (error) {
      console.error('Error with quick action:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-800 border-l border-slate-200 dark:border-slate-700">
      {/* Header */}
      {/* <div className="flex-shrink-0 p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">AI Learning Companion</h3>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">Ask questions, get summaries, take quizzes</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div> */}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && showQuickActions && (
          <div className="space-y-2">
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Quick actions:</p>
            <button
              onClick={() => handleQuickAction('summarize')}
              disabled={!resourceId}
              className="w-full text-left p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-teal-500 dark:hover:border-teal-500 rounded-lg text-sm transition-all duration-150 disabled:opacity-50 flex items-center gap-2"
            >
              <FileText className="w-4 h-4 text-teal-600 dark:text-teal-400" />
              Summarize current resource
            </button>
            <button
              onClick={() => handleQuickAction('quiz')}
              className="w-full text-left p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-teal-500 dark:hover:border-teal-500 rounded-lg text-sm transition-all duration-150 flex items-center gap-2"
            >
              <BookOpen className="w-4 h-4 text-teal-600 dark:text-teal-400" />
              Generate quiz
            </button>
            <button
              onClick={() => {
                const concept = prompt('What concept would you like examples for?')
                if (concept) handleQuickAction('examples', { concept })
              }}
              disabled={!resourceId}
              className="w-full text-left p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-teal-500 dark:hover:border-teal-500 rounded-lg text-sm transition-all duration-150 disabled:opacity-50 flex items-center gap-2"
            >
              <Lightbulb className="w-4 h-4 text-teal-600 dark:text-teal-400" />
              Get examples
            </button>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                  ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-900 dark:text-slate-100'
                }`}
            >
              {msg.role === 'assistant' ? (
                <>
                  <div className="text-sm prose prose-slate dark:prose-invert max-w-none">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                        em: ({ children }) => <em className="italic">{children}</em>,
                        code: ({ children, className }) => {
                          const isInline = !className
                          return isInline ? (
                            <code className="bg-slate-200 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                          ) : (
                            <code className="block bg-slate-200 dark:bg-slate-800 p-3 rounded text-xs font-mono overflow-x-auto">{children}</code>
                          )
                        },
                        ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                        li: ({ children }) => <li className="ml-2">{children}</li>,
                        h1: ({ children }) => <h1 className="text-lg font-semibold mb-2 mt-3 first:mt-0">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-sm font-semibold mb-1 mt-2 first:mt-0">{children}</h3>,
                        blockquote: ({ children }) => <blockquote className="border-l-4 border-teal-600 dark:border-teal-400 pl-3 italic my-2">{children}</blockquote>,
                        hr: () => <hr className="my-3 border-slate-300 dark:border-slate-600" />,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                  {msg.type === 'quiz' && msg.quizAttemptId && (
                    <Button
                      variant="primary"
                      size="sm"
                      className="mt-3"
                      onClick={() => window.location.href = `/quizzes?attempt=${msg.quizAttemptId}`}
                    >
                      Start Quiz
                    </Button>
                  )}
                </>
              ) : (
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <div className="w-2 h-2 bg-teal-600 dark:bg-teal-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-teal-600 dark:bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-teal-600 dark:bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-4 border-t border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              e.target.style.height = 'auto'
              e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
            placeholder="Ask a question..."
            className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
            rows={1}
            disabled={isLoading}
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            disabled={!input.trim() || isLoading}
            icon={<Send className="w-4 h-4" />}
          >
            Send
          </Button>
        </form>
      </div>
    </div>
  )
}

