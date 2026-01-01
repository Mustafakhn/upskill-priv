'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Users, Crown, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Badge from '../components/common/Badge'
import Loading from '../components/common/Loading'
import { apiClient } from '../services/api'
import { useAuth } from '../hooks/useAuth'

interface PremiumRequest {
  id: number
  email: string
  name?: string | null
  free_journeys_used: number
  premium_requested: boolean
  created_at: string
}

interface AdminUser {
  id: number
  email: string
  name?: string | null
  free_journeys_used: number
  is_premium: boolean
  is_admin: boolean
  premium_requested: boolean
  created_at: string
}

export default function AdminPage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading, user } = useAuth()
  const [premiumRequests, setPremiumRequests] = useState<PremiumRequest[]>([])
  const [allUsers, setAllUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'requests' | 'users'>('requests')
  const [processing, setProcessing] = useState<number | null>(null)

  const loadData = React.useCallback(async () => {
    try {
      const [requests, users] = await Promise.all([
        apiClient.getPremiumRequests(),
        apiClient.getAllUsers()
      ])
      setPremiumRequests(requests)
      setAllUsers(users)
    } catch (error) {
      console.error('Failed to load admin data:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/admin')
      return
    }
    if (isAuthenticated && user && !user.is_admin) {
      router.push('/my-learning')
      return
    }
    if (isAuthenticated && user?.is_admin) {
      loadData()
    }
  }, [isAuthenticated, authLoading, user, router, loadData])

  const handleSetPremium = async (userId: number, isPremium: boolean) => {
    setProcessing(userId)
    try {
      await apiClient.setPremiumStatus(userId, isPremium)
      await loadData() // Reload data
    } catch (error) {
      console.error('Failed to update premium status:', error)
      alert('Failed to update premium status. Please try again.')
    } finally {
      setProcessing(null)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen py-8 flex items-center justify-center">
        <Loading text="Loading..." />
      </div>
    )
  }

  if (!isAuthenticated || !user?.is_admin) {
    return null
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2">Admin Panel</h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage users and premium upgrades
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setActiveTab('requests')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'requests'
                ? 'text-teal-600 dark:text-teal-400 border-b-2 border-teal-600 dark:border-teal-400'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            Premium Requests ({premiumRequests.length})
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'users'
                ? 'text-teal-600 dark:text-teal-400 border-b-2 border-teal-600 dark:border-teal-400'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            All Users ({allUsers.length})
          </button>
        </div>

        {/* Premium Requests Tab */}
        {activeTab === 'requests' && (
          <Card>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">Premium Upgrade Requests</h2>
            {premiumRequests.length === 0 ? (
              <p className="text-slate-600 dark:text-slate-400 text-center py-8">No premium requests at this time.</p>
            ) : (
              <div className="space-y-3">
                {premiumRequests.map((request) => (
                  <div
                    key={request.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Users className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                        <div className="flex flex-col">
                          <span className="font-medium text-slate-900 dark:text-slate-100">
                            {request.name || request.email}
                          </span>
                          {request.name && (
                            <span className="text-xs text-slate-500 dark:text-slate-400">{request.email}</span>
                          )}
                        </div>
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">
                        Free journeys used: {request.free_journeys_used} / 5
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {processing === request.id ? (
                        <Loader2 className="w-5 h-5 animate-spin text-teal-600 dark:text-teal-400" />
                      ) : (
                        <>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleSetPremium(request.id, true)}
                            icon={<CheckCircle className="w-4 h-4" />}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSetPremium(request.id, false)}
                            icon={<XCircle className="w-4 h-4" />}
                          >
                            Deny
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* All Users Tab */}
        {activeTab === 'users' && (
          <Card>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">All Users</h2>
            <div className="space-y-3">
              {allUsers.map((adminUser) => (
                <div
                  key={adminUser.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Users className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                      <div className="flex flex-col">
                        <span className="font-medium text-slate-900 dark:text-slate-100">
                          {adminUser.name || adminUser.email}
                        </span>
                        {adminUser.name && (
                          <span className="text-xs text-slate-500 dark:text-slate-400">{adminUser.email}</span>
                        )}
                      </div>
                      {adminUser.is_admin && (
                        <Badge variant="warning">Admin</Badge>
                      )}
                      {adminUser.is_premium && (
                        <Badge variant="success">
                          <Crown className="w-3 h-3 inline mr-1" />
                          Premium
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                      Free journeys: {adminUser.free_journeys_used} / 5
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {processing === adminUser.id ? (
                      <Loader2 className="w-5 h-5 animate-spin text-teal-600 dark:text-teal-400" />
                    ) : (
                      <Button
                        variant={adminUser.is_premium ? "outline" : "primary"}
                        size="sm"
                        onClick={() => handleSetPremium(adminUser.id, !adminUser.is_premium)}
                        icon={adminUser.is_premium ? <XCircle className="w-4 h-4" /> : <Crown className="w-4 h-4" />}
                      >
                        {adminUser.is_premium ? 'Remove Premium' : 'Make Premium'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}

