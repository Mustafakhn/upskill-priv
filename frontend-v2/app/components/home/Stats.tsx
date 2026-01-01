'use client'

import React from 'react'
import Card from '../common/Card'

export default function Stats() {
  const stats = [
    { value: '500+', label: 'Topics Covered' },
    { value: '10K+', label: 'Curated Resources' },
    { value: '15+', label: 'Content Sources' },
    { value: '5K+', label: 'Happy Learners' },
  ]

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card key={index} className="text-center">
              <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
                {stat.value}
              </div>
              <div className="text-sm sm:text-base text-slate-600 dark:text-slate-400">
                {stat.label}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

