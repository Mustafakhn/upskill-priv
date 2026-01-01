'use client'

import React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/app/contexts/ThemeContext'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all duration-300"
      aria-label="Toggle theme"
    >
      {theme === 'light' ? (
        <Moon className="w-5 h-5 text-slate-700 dark:text-slate-300 transition-transform duration-500 rotate-0" />
      ) : (
        <Sun className="w-5 h-5 text-slate-700 dark:text-slate-300 transition-transform duration-500 rotate-180" />
      )}
    </button>
  )
}

