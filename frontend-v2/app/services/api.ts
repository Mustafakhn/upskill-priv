import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // Handle network errors gracefully
    if (!error.response && error.message === 'Network Error') {
      // Don't log network errors for auth check (already suppressed in AuthContext)
      if (originalRequest.url?.includes('/user/me')) {
        return Promise.reject(error)
      }
      // For other endpoints, provide more context
      console.warn(`Network error for ${originalRequest.url}. Is the backend running at ${API_BASE_URL}?`)
      return Promise.reject(error)
    }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        if (typeof window !== 'undefined') {
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/api/v1/user/refresh`, {
              refresh_token: refreshToken
            })
            
            const { access_token, refresh_token: newRefreshToken } = response.data
            localStorage.setItem('access_token', access_token)
            if (newRefreshToken) {
              localStorage.setItem('refresh_token', newRefreshToken)
            }
            
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface Journey {
  id: number
  user_id: number
  topic: string
  level: string
  goal: string
  status: string
  created_at: string
  resources?: Resource[]
  resource_count: number
  sections?: Section[]
}

export interface Section {
  name: string
  resources: string[]
  description?: string
}

export interface Resource {
  id: string
  url: string
  title: string
  summary: string
  type: 'video' | 'blog' | 'doc'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  tags: string[]
  estimated_time: number
  content?: string
}

export interface ProgressSummary {
  total_resources: number
  completed_count: number
  in_progress_count: number
  not_started_count: number
  completion_percentage: number
  total_time_spent_minutes: number
  progress_by_resource: Record<string, {
    completed: number
    time_spent_minutes: number
    last_accessed_at?: string
    completed_at?: string
  }>
}

export const apiClient = {
  // Auth
  register: async (email: string, password: string) => {
    const response = await api.post('/api/v1/user/register', { email, password })
    return response.data
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/user/login', { email, password })
    if (typeof window !== 'undefined') {
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token)
      }
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token)
      }
    }
    return response.data
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/user/me')
    return response.data
  },

  updateUserName: async (name: string) => {
    const response = await api.put('/api/v1/user/update-name', { name })
    return response.data
  },

  updatePassword: async (oldPassword: string, newPassword: string) => {
    const response = await api.put('/api/v1/user/update-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
    return response.data
  },

  // Popular Topics
  getPopularTopics: async (): Promise<string[]> => {
    try {
      const response = await api.get('/api/v1/journey/topics/popular')
      return response.data.topics || []
    } catch (error) {
      console.error('Error fetching popular topics:', error)
      // Return default topics on error
      return ['Learn Python', 'Master Guitar', 'Italian Cooking', 'Digital Marketing']
    }
  },

  // Premium
  requestPremium: async () => {
    const response = await api.post('/api/v1/user/request-premium')
    return response.data
  },

  // Admin
  getAllUsers: async () => {
    const response = await api.get('/api/v1/user/admin/users')
    return response.data.users
  },

  getPremiumRequests: async () => {
    const response = await api.get('/api/v1/user/admin/premium-requests')
    return response.data.requests
  },

  setPremiumStatus: async (userId: number, isPremium: boolean) => {
    const response = await api.post('/api/v1/user/admin/set-premium', {
      user_id: userId,
      is_premium: isPremium
    })
    return response.data
  },

  // Chat
  startChat: async (message: string, conversationHistory?: ChatMessage[]) => {
    const response = await api.post('/api/v1/chat/start', {
      message,
      conversation_history: conversationHistory || []
    })
    return response.data
  },

  respondToChat: async (message: string, conversationHistory: ChatMessage[], conversationId?: string) => {
    const response = await api.post('/api/v1/chat/respond', {
      message,
      conversation_history: conversationHistory,
      conversation_id: conversationId
    })
    return response.data
  },

  // Journeys
  getJourney: async (journeyId: number): Promise<Journey> => {
    const response = await api.get(`/api/v1/journey/${journeyId}`)
    return response.data
  },

  getUserJourneys: async (): Promise<Journey[]> => {
    const response = await api.get('/api/v1/journey/')
    return response.data
  },

  // Progress
  getProgressSummary: async (journeyId: number): Promise<ProgressSummary> => {
    const response = await api.post(`/api/v1/journey/${journeyId}/progress/summary`)
    return response.data
  },

  markResourceCompleted: async (journeyId: number, resourceId: string) => {
    const response = await api.post(`/api/v1/journey/${journeyId}/progress/complete`, {
      resource_id: resourceId
    })
    return response.data
  },

  markResourceIncomplete: async (journeyId: number, resourceId: string) => {
    const response = await api.post(`/api/v1/journey/${journeyId}/progress/incomplete`, {
      resource_id: resourceId
    })
    return response.data
  },

  markResourceInProgress: async (journeyId: number, resourceId: string) => {
    const response = await api.post(`/api/v1/journey/${journeyId}/progress/in-progress`, {
      resource_id: resourceId
    })
    return response.data
  },

  updateTimeSpent: async (journeyId: number, resourceId: string, timeSpentMinutes: number) => {
    const response = await api.post(`/api/v1/journey/${journeyId}/progress/time`, {
      resource_id: resourceId,
      time_spent_minutes: timeSpentMinutes
    })
    return response.data
  },

  getLastPosition: async (journeyId: number) => {
    const response = await api.get(`/api/v1/journey/${journeyId}/progress/last-position`)
    return response.data
  },

  // Resources
  getResource: async (resourceId: string) => {
    const response = await api.get(`/api/v1/resource/${resourceId}`)
    return response.data
  },

  getResourceContent: async (resourceId: string) => {
    const response = await api.get(`/api/v1/resource/${resourceId}/content`)
    return response.data
  },

  // Chat History
  getUserConversations: async (): Promise<Conversation[]> => {
    const response = await api.get('/api/v1/chat/history')
    return response.data
  },

  getChatHistory: async (conversationId: string) => {
    const response = await api.get(`/api/v1/chat/history/${conversationId}`)
    return response.data
  },

  // AI Companion
  askQuestion: async (journeyId: number, question: string, contextResourceId?: string) => {
    const response = await api.post(`/api/v1/companion/${journeyId}/question`, {
      question,
      context_resource_id: contextResourceId
    })
    return response.data
  },

  summarizeResource: async (resourceId: string) => {
    const response = await api.post(`/api/v1/companion/resource/${resourceId}/summarize`)
    return response.data
  },

  generateExamples: async (resourceId: string, concept: string, count?: number) => {
    const response = await api.post(`/api/v1/companion/resource/examples`, {
      resource_id: resourceId,
      concept,
      count: count || 3
    })
    return response.data
  },

  createQuiz: async (journeyId: number, options?: { resource_id?: string; quiz_type?: string; num_questions?: number }) => {
    const response = await api.post(`/api/v1/quiz/${journeyId}/create`, {
      resource_id: options?.resource_id,
      quiz_type: options?.quiz_type || 'mcq',
      num_questions: options?.num_questions || 5
    })
    return response.data
  },

  getQuiz: async (attemptId: number) => {
    const response = await api.get(`/api/v1/quiz/${attemptId}`)
    return response.data
  },

  getUserQuizzes: async (userId: number, journeyId?: number) => {
    const params = journeyId ? `?journey_id=${journeyId}` : ''
    const response = await api.get(`/api/v1/quiz/user/${userId}/quizzes${params}`)
    return response.data
  },
}

export interface Conversation {
  id: string
  user_id: number
  journey_id?: number
  created_at: string
  updated_at: string
}

export interface ResourceContent {
  content: string | null
  html?: string | null
  url: string
  title: string
  scraped: boolean
  message?: string
}

export default api

