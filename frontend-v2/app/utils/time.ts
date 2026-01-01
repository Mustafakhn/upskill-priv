/**
 * Utility functions for time handling and conversion
 */

/**
 * Convert UTC timestamp string to local browser time
 * @param utcString - ISO 8601 UTC timestamp string
 * @returns Formatted local time string
 */
export function formatLocalTime(utcString: string | null | undefined): string {
  if (!utcString) return 'N/A'
  
  try {
    const date = new Date(utcString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid date'
  }
}

/**
 * Format date for conversation history (relative time for recent, absolute for older)
 * @param utcString - ISO 8601 UTC timestamp string
 * @returns Formatted time string
 */
export function formatConversationTime(utcString: string | null | undefined): string {
  if (!utcString) return 'N/A'
  
  try {
    const date = new Date(utcString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    // Less than 1 minute
    if (diffMins < 1) return 'Just now'
    
    // Less than 1 hour
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`
    
    // Less than 24 hours
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    
    // Less than 7 days
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    // Older than 7 days - show full date
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    console.error('Error formatting conversation time:', error)
    return 'Invalid date'
  }
}

/**
 * Format date for display (short format)
 * @param utcString - ISO 8601 UTC timestamp string
 * @returns Formatted date string
 */
export function formatDate(utcString: string | null | undefined): string {
  if (!utcString) return 'N/A'
  
  try {
    const date = new Date(utcString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid date'
  }
}

/**
 * Format date and time for display
 * @param utcString - ISO 8601 UTC timestamp string
 * @returns Formatted date and time string
 */
export function formatDateTime(utcString: string | null | undefined): string {
  if (!utcString) return 'N/A'
  
  try {
    const date = new Date(utcString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  } catch (error) {
    console.error('Error formatting date time:', error)
    return 'Invalid date'
  }
}

