// Notification utilities
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

export async function subscribeToJourneyNotifications(
  journeyId: number,
  registration: ServiceWorkerRegistration
): Promise<void> {
  // For now, we'll use polling to check journey status
  // In the future, this could be replaced with push subscriptions
  console.log(`Subscribed to notifications for journey ${journeyId}`)
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

