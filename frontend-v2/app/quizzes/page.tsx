'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { BookOpen, CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Badge from '../components/common/Badge'
import Loading from '../components/common/Loading'
import { apiClient } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import { formatDate, formatDateTime } from '../utils/time'

interface QuizAttempt {
  attempt_id: number
  journey_id: number
  resource_id?: string
  quiz_type: string
  score?: number
  completed: boolean
  created_at: string
  completed_at?: string
}

interface QuizDetail extends QuizAttempt {
  questions: Array<{
    question: string
    options?: string[]
    correct_answer?: number | string
    explanation?: string
    sample_answer?: string
  }>
  answers?: Record<string, any>
  journey?: {
    id: number
    topic: string
  }
  resource?: {
    id: string
    title: string
    url: string
    type: string
  }
}

export default function QuizzesPage() {
  const router = useRouter()
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const [quizzes, setQuizzes] = useState<QuizAttempt[]>([])
  const [selectedQuiz, setSelectedQuiz] = useState<QuizDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/quizzes')
      return
    }
    if (isAuthenticated && user) {
      loadQuizzes()
    }
  }, [isAuthenticated, authLoading, user, router])

  const loadQuizzes = async () => {
    if (!user?.id) return
    try {
      const data = await apiClient.getUserQuizzes(user.id)
      setQuizzes(data.quizzes || [])
    } catch (error) {
      console.error('Error loading quizzes:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadQuizDetail = async (attemptId: number) => {
    setLoadingDetail(true)
    try {
      const quizData = await apiClient.getQuiz(attemptId)
      
      let journeyInfo = null
      if (quizData.journey_id) {
        try {
          const journey = await apiClient.getJourney(quizData.journey_id)
          journeyInfo = {
            id: journey.id,
            topic: journey.topic
          }
        } catch (error) {
          console.error('Error loading journey:', error)
        }
      }

      let resourceInfo = null
      if (quizData.resource_id) {
        try {
          const resource = await apiClient.getResource(quizData.resource_id)
          resourceInfo = {
            id: resource.id,
            title: resource.title,
            url: resource.url,
            type: resource.type
          }
        } catch (error) {
          console.error('Error loading resource:', error)
        }
      }

      setSelectedQuiz({
        ...quizData,
        journey: journeyInfo,
        resource: resourceInfo
      })
    } catch (error) {
      console.error('Error loading quiz detail:', error)
    } finally {
      setLoadingDetail(false)
    }
  }

  const handleRetake = async (quiz: QuizAttempt) => {
    try {
      await apiClient.createQuiz(quiz.journey_id, {
        quiz_type: quiz.quiz_type,
        resource_id: quiz.resource_id,
        num_questions: 5
      })
      if (user) {
        await loadQuizzes()
      }
    } catch (error) {
      console.error('Error creating new quiz:', error)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen py-8">
        <Loading text="Loading quizzes..." />
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold mb-2">My Quizzes</h1>
              <p className="text-slate-600 dark:text-slate-400">Review your quiz attempts and track your progress</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              icon={<ArrowLeft className="w-4 h-4" />}
              onClick={() => router.push('/my-learning')}
            >
              Back to Learning
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quiz List */}
          <div className="lg:col-span-1">
            <Card>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Quiz Attempts ({quizzes.length})
              </h2>
              {quizzes.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center">
                    <BookOpen className="w-8 h-8 text-slate-400" />
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">No quizzes yet. Start a journey to take quizzes!</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {quizzes.map((quiz) => (
                    <button
                      key={quiz.attempt_id}
                      onClick={() => loadQuizDetail(quiz.attempt_id)}
                      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                        selectedQuiz?.attempt_id === quiz.attempt_id
                          ? 'bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800 shadow-sm'
                          : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-teal-300 dark:hover:border-teal-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                          {quiz.quiz_type}
                        </span>
                        {quiz.completed && quiz.score !== null && (
                          <span className={`text-xs font-bold px-2 py-1 rounded-lg ${
                            quiz.score >= 80 ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800' :
                            quiz.score >= 60 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800' :
                            'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'
                          }`}>
                            {quiz.score}%
                          </span>
                        )}
                      </div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">
                        {quiz.completed ? 'Completed' : 'In Progress'}
                      </div>
                      <div className="text-xs text-slate-600 dark:text-slate-400">
                        {formatDate(quiz.created_at)}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Quiz Detail */}
          <div className="lg:col-span-2">
            {loadingDetail ? (
              <Card>
                <div className="py-12 flex items-center justify-center">
                  <Loading size="md" />
                </div>
              </Card>
            ) : selectedQuiz ? (
              <Card>
                {/* Header */}
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Quiz Details</h2>
                    {selectedQuiz.completed && selectedQuiz.score !== null && (
                      <div className={`text-4xl font-bold ${
                        selectedQuiz.score >= 80 ? 'text-green-600 dark:text-green-400' :
                        selectedQuiz.score >= 60 ? 'text-yellow-600 dark:text-yellow-400' :
                        'text-red-600 dark:text-red-400'
                      }`}>
                        {selectedQuiz.score}%
                      </div>
                    )}
                  </div>

                  {/* Source Information */}
                  <div className="space-y-3 p-4 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl">
                    {selectedQuiz.journey && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-slate-600 dark:text-slate-400 font-medium">Journey:</span>
                        <button
                          onClick={() => router.push(`/journey/${selectedQuiz.journey!.id}`)}
                          className="text-teal-600 dark:text-teal-400 hover:underline font-medium"
                        >
                          {selectedQuiz.journey.topic}
                        </button>
                      </div>
                    )}
                    {selectedQuiz.resource && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-slate-600 dark:text-slate-400 font-medium">Source:</span>
                        <a
                          href={selectedQuiz.resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-teal-600 dark:text-teal-400 hover:underline font-medium"
                        >
                          {selectedQuiz.resource.title}
                        </a>
                        <Badge variant="secondary" className="text-xs">
                          {selectedQuiz.resource.type}
                        </Badge>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-slate-600 dark:text-slate-400 font-medium">Type:</span>
                      <span className="text-slate-900 dark:text-slate-100">{selectedQuiz.quiz_type.toUpperCase()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-slate-600 dark:text-slate-400 font-medium">Created:</span>
                      <span className="text-slate-900 dark:text-slate-100">
                        {formatDateTime(selectedQuiz.created_at)}
                      </span>
                    </div>
                    {selectedQuiz.completed_at && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-slate-600 dark:text-slate-400 font-medium">Completed:</span>
                        <span className="text-slate-900 dark:text-slate-100">
                          {formatDateTime(selectedQuiz.completed_at)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Questions and Answers */}
                {selectedQuiz.questions && selectedQuiz.questions.length > 0 && (
                  <div className="space-y-6">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-6">
                      Questions & Answers
                    </h3>
                    {selectedQuiz.questions.map((q, idx) => {
                      const userAnswer = selectedQuiz.answers?.[idx] ?? selectedQuiz.answers?.[String(idx)]
                      const isMCQ = selectedQuiz.quiz_type === 'mcq'
                      const isCorrect = isMCQ 
                        ? userAnswer === q.correct_answer 
                        : userAnswer && userAnswer.trim()
                      
                      return (
                        <div key={idx} className="border border-slate-200 dark:border-slate-700 rounded-xl p-6 bg-slate-50 dark:bg-slate-800/50">
                          <div className="flex items-start gap-4 mb-4">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                              selectedQuiz.completed 
                                ? (isCorrect ? 'bg-green-600 text-white' : 'bg-red-600 text-white')
                                : 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100'
                            }`}>
                              {selectedQuiz.completed ? (isCorrect ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />) : idx + 1}
                            </div>
                            <div className="flex-1">
                              <div className="prose prose-slate dark:prose-invert prose-sm max-w-none mb-4">
                                <ReactMarkdown
                                  components={{
                                    p: ({ children }) => <p className="mb-2 text-slate-900 dark:text-slate-100 font-medium">{children}</p>,
                                    strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                                  }}
                                >
                                  {q.question}
                                </ReactMarkdown>
                              </div>

                              {isMCQ && q.options && (
                                <div className="space-y-2 mb-4">
                                  {q.options.map((opt: string, optIdx: number) => (
                                    <div
                                      key={optIdx}
                                      className={`p-3 rounded-lg border text-sm transition-all ${
                                        selectedQuiz.completed
                                          ? optIdx === q.correct_answer
                                            ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 font-medium'
                                            : optIdx === userAnswer && optIdx !== q.correct_answer
                                            ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 font-medium'
                                            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                                          : optIdx === userAnswer
                                          ? 'bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800 text-slate-900 dark:text-slate-100 font-medium'
                                          : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                                      }`}
                                    >
                                      <span className="font-semibold mr-2">{String.fromCharCode(65 + optIdx)}.</span>
                                      {opt}
                                      {selectedQuiz.completed && optIdx === q.correct_answer && (
                                        <span className="ml-2 text-xs">✓ Correct</span>
                                      )}
                                      {selectedQuiz.completed && optIdx === userAnswer && optIdx !== q.correct_answer && (
                                        <span className="ml-2 text-xs">Your answer</span>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              )}

                              {!isMCQ && (
                                <div className="mb-4">
                                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-2 font-medium">Your answer:</p>
                                  <p className="p-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-700 dark:text-slate-300">
                                    {userAnswer || 'No answer provided'}
                                  </p>
                                  {q.sample_answer && selectedQuiz.completed && (
                                    <>
                                      <p className="text-xs text-slate-600 dark:text-slate-400 mb-2 mt-4 font-medium">Sample answer:</p>
                                      <p className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-slate-700 dark:text-slate-300">
                                        {q.sample_answer}
                                      </p>
                                    </>
                                  )}
                                </div>
                              )}

                              {q.explanation && selectedQuiz.completed && (
                                <div className="mt-4 p-4 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
                                  <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-2 uppercase tracking-wide">Explanation:</p>
                                  <div className="prose prose-slate dark:prose-invert prose-sm max-w-none">
                                    <ReactMarkdown
                                      components={{
                                        p: ({ children }) => <p className="mb-1 text-slate-700 dark:text-slate-300 text-sm">{children}</p>,
                                      }}
                                    >
                                      {q.explanation}
                                    </ReactMarkdown>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}

                {/* Actions */}
                {selectedQuiz.completed && (
                  <div className="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700">
                    <Button
                      variant="primary"
                      onClick={() => handleRetake(selectedQuiz)}
                    >
                      Retake Quiz
                    </Button>
                  </div>
                )}
              </Card>
            ) : (
              <Card>
                <div className="py-12 text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center">
                    <BookOpen className="w-8 h-8 text-slate-400" />
                  </div>
                  <p className="text-slate-600 dark:text-slate-400">Select a quiz to view details</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

