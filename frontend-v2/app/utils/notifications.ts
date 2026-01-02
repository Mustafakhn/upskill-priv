// Notification utilities
import { apiClient } from '../services/api'

export async function requestNotificationPermission(): Promise<boolean> {
  if (!('Notification' in window)) {
    console.warn('This browser does not support notifications')
    return false
  }

  if (Notification.permission === 'granted') {
    return true
  }

  if (Notification.permission === 'denied') {
    console.warn('Notification permission denied')
    return false
  }

  // Request permission
  const permission = await Notification.requestPermission()
  return permission === 'granted'
}

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.warn('Service workers are not supported')
    return null
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/'
    })
    console.log('Service Worker registered:', registration)
    return registration
  } catch (error) {
    console.error('Service Worker registration failed:', error)
    return null
  }
}

export async function subscribeToPushNotifications(
  registration: ServiceWorkerRegistration
): Promise<PushSubscription | null> {
  if (!('PushManager' in window)) {
    console.warn('Push messaging is not supported')
    return null
  }

  try {
    // Check if already subscribed
    let subscription = await registration.pushManager.getSubscription()
    
    if (!subscription) {
      // Request permission first
      const permission = await requestNotificationPermission()
      if (!permission) {
        console.warn('Notification permission not granted')
        return null
      }

      // Subscribe to push notifications
      // Note: We need the VAPID public key from the backend
      // For now, we'll try to get it from an endpoint or use a placeholder
      const vapidPublicKey = await getVapidPublicKey()
      if (!vapidPublicKey) {
        console.warn('VAPID public key not available')
        return null
      }

      const keyArray = urlBase64ToUint8Array(vapidPublicKey)
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: keyArray as BufferSource
      })
    }

    // Send subscription to backend
    try {
      await apiClient.subscribeToPush(subscription)
      console.log('Push subscription sent to backend')
    } catch (error) {
      console.error('Failed to send subscription to backend:', error)
      // Continue anyway - subscription is created locally
    }

    return subscription
  } catch (error) {
    console.error('Push subscription failed:', error)
    return null
  }
}

async function getVapidPublicKey(): Promise<string | null> {
  // Try to get from backend API
  try {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${API_BASE_URL}/api/v1/push/vapid-public-key`)
    if (response.ok) {
      const data = await response.json()
      return data.publicKey
    }
  } catch (error) {
    console.warn('Could not fetch VAPID public key from backend:', error)
  }
  return null
}

// Convert VAPID key from base64url to Uint8Array
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export function showLocalNotification(title: string, options?: NotificationOptions): void {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    return
  }

  new Notification(title, {
    icon: '/upskill-logo.svg',
    badge: '/upskill-logo.svg',
    ...options
  })
}

