'use client'

import React, { useState } from 'react'
import { Search, X, Loader2 } from 'lucide-react'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  autoFocus?: boolean
  value?: string
  onChange?: (value: string) => void
  loading?: boolean
  suggestions?: string[]
  className?: string
}

export default function SearchBar({
  onSearch,
  placeholder = 'What do you want to learn today?',
  autoFocus = false,
  value: controlledValue,
  onChange,
  loading = false,
  suggestions = [],
  className = '',
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  
  const value = controlledValue !== undefined ? controlledValue : internalValue
  const setValue = onChange || setInternalValue

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      onSearch(value.trim())
      setShowSuggestions(false)
    }
  }

  const handleClear = () => {
    setValue('')
    setShowSuggestions(false)
  }

  const handleSuggestionClick = (suggestion: string) => {
    setValue(suggestion)
    onSearch(suggestion)
    setShowSuggestions(false)
  }

  return (
    <div className={`relative ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={value}
            onChange={(e) => {
              setValue(e.target.value)
              setShowSuggestions(true)
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className="input pl-12 pr-12 text-lg"
          />
          {loading ? (
            <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-teal-600 animate-spin" />
          ) : value ? (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
            >
              <X className="w-4 h-4 text-slate-400" />
            </button>
          ) : null}
        </div>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && value && (
        <div className="absolute top-full left-0 right-0 mt-2 card p-2 z-50 animate-slide-down">
          {suggestions
            .filter((s) => s.toLowerCase().includes(value.toLowerCase()))
            .slice(0, 5)
            .map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left px-4 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-slate-700 dark:text-slate-300"
              >
                {suggestion}
              </button>
            ))}
        </div>
      )}
    </div>
  )
}

