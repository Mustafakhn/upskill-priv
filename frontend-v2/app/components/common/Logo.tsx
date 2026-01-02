'use client'

import Image from 'next/image'
import Link from 'next/link'
import { cn } from '@/app/utils/cn'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  className?: string
  href?: string
}

export default function Logo({ size = 'md', showText = true, className, href = '/' }: LogoProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  }

  const iconSizes = {
    sm: 24,
    md: 32,
    lg: 40
  }

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  }

  const content = (
    <div className={cn('flex items-center gap-2 group', className)}>
      <div className={cn(
        'relative rounded-lg overflow-hidden bg-gradient-to-r from-teal-600 to-cyan-600 group-hover:from-teal-700 group-hover:to-cyan-700 transition-all duration-300 flex items-center justify-center',
        sizeClasses[size]
      )}>
        <Image
          src="/upskill-logo.svg"
          alt="Upskill Logo"
          width={iconSizes[size]}
          height={iconSizes[size]}
          className={cn('object-contain', sizeClasses[size])}
          priority
        />
      </div>
      {showText && (
        <span className={cn(
          'font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent',
          textSizes[size]
        )}>
          Upskill
        </span>
      )}
    </div>
  )

  if (href) {
    return (
      <Link href={href} className="inline-block">
        {content}
      </Link>
    )
  }

  return content
}

