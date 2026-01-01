'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Menu, X, Sparkles, LogOut, User, Crown, Shield } from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import Button from '../common/Button'
import { useAuth } from '../../hooks/useAuth'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const { isAuthenticated, user, logout, loading: authLoading } = useAuth()

  const getNavigation = () => {
    if (isAuthenticated) {
      const nav = [
        { name: 'New Journey', href: '/start' },
        { name: 'My Learning', href: '/my-learning' },
        { name: 'Quizzes', href: '/quizzes' },
        { name: 'Settings', href: '/settings' },
      ]
      if (user?.is_admin) {
        nav.push({ name: 'Admin', href: '/admin' })
      }
      return nav
    }
    return [
      { name: 'Home', href: '/' },
      { name: 'About', href: '/about' },
    ]
  }

  const navigation = getNavigation()

  const isActive = (href: string) => pathname === href

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="p-2 rounded-lg bg-gradient-to-r from-teal-600 to-cyan-600 group-hover:from-teal-700 group-hover:to-cyan-700 transition-all duration-300">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Inurek
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navigation
              .filter(item => item.name !== 'Quizzes' || isAuthenticated)
              .map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'text-teal-600 dark:text-teal-400'
                      : 'text-slate-600 dark:text-slate-400 hover:text-teal-600 dark:hover:text-teal-400'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
          </div>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-4">
            <ThemeToggle />
            {!authLoading && (
              isAuthenticated ? (
                <>
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800">
                    {user?.is_premium && <Crown className="w-4 h-4 text-yellow-500" />}
                    {user?.is_admin && <Shield className="w-4 h-4 text-purple-500" />}
                    <User className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{user?.name || user?.email?.split('@')[0]}</span>
                  </div>
                  <Button variant="ghost" size="sm" icon={<LogOut className="w-4 h-4" />} onClick={handleLogout}>
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Link href="/login">
                    <Button variant="ghost" size="sm">
                      Sign In
                    </Button>
                  </Link>
                  <Link href="/register">
                    <Button variant="primary" size="sm">
                      Get Started
                    </Button>
                  </Link>
                </>
              )
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            <ThemeToggle />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6 text-slate-700 dark:text-slate-300" />
              ) : (
                <Menu className="w-6 h-6 text-slate-700 dark:text-slate-300" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 animate-slide-down">
            <div className="flex flex-col gap-2">
              {navigation
                .filter(item => item.name !== 'Quizzes' || isAuthenticated)
                .map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              <div className="flex gap-2 mt-4">
                {!authLoading && (
                  isAuthenticated ? (
                    <>
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 w-full">
                        {user?.is_premium && <Crown className="w-4 h-4 text-yellow-500" />}
                        {user?.is_admin && <Shield className="w-4 h-4 text-purple-500" />}
                        <User className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                        <span className="text-sm text-slate-700 dark:text-slate-300">{user?.name || user?.email?.split('@')[0]}</span>
                      </div>
                      <Button variant="ghost" size="sm" className="w-full" icon={<LogOut className="w-4 h-4" />} onClick={handleLogout}>
                        Logout
                      </Button>
                    </>
                  ) : (
                    <>
                      <Link href="/login" className="flex-1">
                        <Button variant="ghost" size="sm" className="w-full">
                          Sign In
                        </Button>
                      </Link>
                      <Link href="/register" className="flex-1">
                        <Button variant="primary" size="sm" className="w-full">
                          Sign Up
                        </Button>
                      </Link>
                    </>
                  )
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}

