'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { apiClient } from '../services/api'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import { Download, User, Lock, CheckCircle, XCircle } from 'lucide-react'

export default function SettingsPage() {
  const { user, checkAuth } = useAuth()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [installPrompt, setInstallPrompt] = useState<any>(null)
  const [isInstalled, setIsInstalled] = useState(false)
  const [showInstructions, setShowInstructions] = useState(false)

  // Name form state
  const [name, setName] = useState('')
  const [nameLoading, setNameLoading] = useState(false)

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [passwordLoading, setPasswordLoading] = useState(false)

  useEffect(() => {
    if (user) {
      setName(user.name || '')
    }
  }, [user])

  useEffect(() => {
    // Check if PWA is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true)
    }

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      setInstallPrompt(e)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  const handleInstallPWA = async () => {
    if (!installPrompt) {
      setMessage({ type: 'error', text: 'Install prompt not available. The app may already be installed.' })
      return
    }

    try {
      installPrompt.prompt()
      const { outcome } = await installPrompt.userChoice
      
      if (outcome === 'accepted') {
        setMessage({ type: 'success', text: 'App installation started!' })
        setIsInstalled(true)
      } else {
        setMessage({ type: 'error', text: 'App installation declined.' })
      }
      setInstallPrompt(null)
    } catch (error) {
      setMessage({ type: 'error', text: 'Error installing app' })
    }
  }

  const getInstallInstructions = () => {
    if (typeof window === 'undefined') return null
    
    const userAgent = navigator.userAgent.toLowerCase()
    
    if (/iphone|ipad|ipod/.test(userAgent)) {
      return {
        title: 'Install on iOS',
        steps: [
          'Tap the Share button (square with arrow pointing up)',
          'Scroll down and tap "Add to Home Screen"',
          'Tap "Add" to confirm'
        ]
      }
    } else if (/android/.test(userAgent)) {
      return {
        title: 'Install on Android',
        steps: [
          'Tap the menu button (three dots) in the top right',
          'Tap "Install app" or "Add to Home Screen"',
          'Confirm the installation'
        ]
      }
    } else if (/chrome/.test(userAgent)) {
      return {
        title: 'Install in Chrome',
        steps: [
          'Look for the install icon (plus/⊕) in the address bar, or',
          'Click the three-dot menu → "Install Upskill..."',
          'Click "Install" in the dialog that appears'
        ]
      }
    } else if (/firefox/.test(userAgent)) {
      return {
        title: 'Install in Firefox',
        steps: [
          'Click the menu button (three horizontal lines)',
          'Look for "Install" option or the install icon in the address bar',
          'Click to install the app'
        ]
      }
    } else if (/edge/.test(userAgent)) {
      return {
        title: 'Install in Edge',
        steps: [
          'Look for the install icon in the address bar, or',
          'Click the three-dot menu → "Apps" → "Install this site as an app"',
          'Click "Install" to confirm'
        ]
      }
    } else {
      return {
        title: 'Install this app',
        steps: [
          'Look for an install icon in your browser\'s address bar',
          'Or check your browser\'s menu for "Install" or "Add to Home Screen" options',
          'Follow the prompts to complete installation'
        ]
      }
    }
  }

  const instructions = getInstallInstructions()

  const handleUpdateName = async (e: React.FormEvent) => {
    e.preventDefault()
    setNameLoading(true)
    setMessage(null)

    try {
      await apiClient.updateUserName(name)
      setMessage({ type: 'success', text: 'Name updated successfully!' })
      await checkAuth()
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to update name' 
      })
    } finally {
      setNameLoading(false)
    }
  }

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' })
      return
    }

    if (passwordForm.newPassword.length < 6) {
      setMessage({ type: 'error', text: 'New password must be at least 6 characters' })
      return
    }

    setPasswordLoading(true)

    try {
      await apiClient.updatePassword(passwordForm.oldPassword, passwordForm.newPassword)
      setMessage({ type: 'success', text: 'Password updated successfully!' })
      setPasswordForm({ oldPassword: '', newPassword: '', confirmPassword: '' })
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to update password' 
      })
    } finally {
      setPasswordLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <p className="text-center text-gray-600">Please log in to access settings.</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
          message.type === 'success' 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <XCircle className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* PWA Install Section */}
      <Card className="mb-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <Download className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">Install App</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Install Upskill as a Progressive Web App to access it faster and use it offline.
            </p>
            {isInstalled ? (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle className="w-5 h-5" />
                <span>App is installed</span>
              </div>
            ) : installPrompt ? (
              <Button onClick={handleInstallPWA} className="bg-blue-600 hover:bg-blue-700">
                <Download className="w-4 h-4 mr-2" />
                Install App
              </Button>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Automatic install prompt is not available. You can still install the app manually.
                </p>
                <Button 
                  onClick={() => setShowInstructions(!showInstructions)} 
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Download className="w-4 h-4 mr-2" />
                  {showInstructions ? 'Hide' : 'Show'} Install Instructions
                </Button>
                {showInstructions && instructions && (
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
                      {instructions.title}
                    </h3>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700 dark:text-gray-300">
                      {instructions.steps.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Update Name Section */}
      <Card className="mb-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
            <User className="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">Update Name</h2>
            <form onSubmit={handleUpdateName} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2">
                  Display Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                  placeholder="Enter your name"
                />
              </div>
              <Button 
                type="submit" 
                disabled={nameLoading}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {nameLoading ? 'Updating...' : 'Update Name'}
              </Button>
            </form>
          </div>
        </div>
      </Card>

      {/* Update Password Section */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="p-3 bg-red-100 dark:bg-red-900 rounded-lg">
            <Lock className="w-6 h-6 text-red-600 dark:text-red-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">Change Password</h2>
            <form onSubmit={handleUpdatePassword} className="space-y-4">
              <div>
                <label htmlFor="oldPassword" className="block text-sm font-medium mb-2">
                  Current Password
                </label>
                <input
                  id="oldPassword"
                  type="password"
                  value={passwordForm.oldPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, oldPassword: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                  required
                />
              </div>
              <div>
                <label htmlFor="newPassword" className="block text-sm font-medium mb-2">
                  New Password
                </label>
                <input
                  id="newPassword"
                  type="password"
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                  minLength={6}
                  required
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2">
                  Confirm New Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                  minLength={6}
                  required
                />
              </div>
              <Button 
                type="submit" 
                disabled={passwordLoading}
                className="bg-red-600 hover:bg-red-700"
              >
                {passwordLoading ? 'Updating...' : 'Update Password'}
              </Button>
            </form>
          </div>
        </div>
      </Card>
    </div>
  )
}

