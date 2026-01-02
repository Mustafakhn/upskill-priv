// Service Worker for Push Notifications
self.addEventListener('install', (event) => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim())
})

self.addEventListener('push', (event) => {
  let data = {}
  try {
    data = event.data ? event.data.json() : {}
  } catch (e) {
    console.error('Error parsing push data:', e)
    data = { title: 'Upskill', body: 'You have a new notification' }
  }

  const title = data.title || 'Upskill'
  const options = {
    body: data.body || 'Your learning journey is ready!',
    icon: '/upskill-logo.svg',
    badge: '/upskill-logo.svg',
    tag: data.tag || 'journey-ready',
    data: data.data || {},
    requireInteraction: false,
    actions: data.actions || []
  }

  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const data = event.notification.data
  const urlToOpen = data.url || '/my-learning'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if there's already a window/tab open with the target URL
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i]
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus()
        }
      }
      // If not, open a new window/tab
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen)
      }
    })
  )
})

