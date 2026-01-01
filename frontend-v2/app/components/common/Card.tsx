'use client'

import React from 'react'

interface CardProps {
  children: React.ReactNode
  hoverable?: boolean
  clickable?: boolean
  className?: string
  onClick?: () => void
}

export default function Card({
  children,
  hoverable = false,
  clickable = false,
  className = '',
  onClick,
}: CardProps) {
  const baseClasses = 'card p-6'
  const interactiveClasses = hoverable || clickable ? 'card-hover' : ''
  const cursorClass = clickable ? 'cursor-pointer' : ''

  return (
    <div
      className={`${baseClasses} ${interactiveClasses} ${cursorClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

