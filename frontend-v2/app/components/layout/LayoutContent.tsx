'use client'

import { useAuth } from '../../hooks/useAuth'
import Footer from './Footer'

export default function LayoutContent() {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading || isAuthenticated) {
    return null
  }
  
  return <Footer />
}

