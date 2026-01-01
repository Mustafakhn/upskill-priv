'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { apiClient } from '../services/api'

interface User {
  id: number
  email: string
  created_at: string
  free_journeys_used: number
  is_premium: boolean
  is_admin: boolean
  premium_requested: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<any>
  register: (email: string, password: string) => Promise<any>
  logout: () => void
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const checkAuth = useCallback(async () => {
    try {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token')
        if (token) {
          const userData = await apiClient.getCurrentUser()
          setUser(userData)
          setIsAuthenticated(true)
        } else {
          setUser(null)
          setIsAuthenticated(false)
        }
      }
    } catch (error) {
      // Don't log network errors as they're expected when backend is down
      if (error && typeof error === 'object' && 'message' in error && error.message !== 'Network Error') {
        console.error('Auth check failed:', error)
      }
      setIsAuthenticated(false)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string) => {
    const data = await apiClient.login(email, password)
    setUser(data.user)
    setIsAuthenticated(true)
    return data
  }

  const register = async (email: string, password: string) => {
    const data = await apiClient.register(email, password)
    if (data.access_token) {
      setUser(data.user)
      setIsAuthenticated(true)
    }
    return data
  }

  const logout = () => {
    apiClient.logout()
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        login,
        register,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

