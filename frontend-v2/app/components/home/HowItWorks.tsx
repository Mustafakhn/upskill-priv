'use client'

import React from 'react'
import { Search, BookOpen, Rocket } from 'lucide-react'
import Card from '../common/Card'

export default function HowItWorks() {
  const steps = [
    {
      icon: Search,
      title: 'Search Any Topic',
      description: 'Tell us what you want to learn - from beginner to advanced, any subject imaginable',
      color: 'from-teal-600 to-cyan-600',
    },
    {
      icon: BookOpen,
      title: 'Get Curated Resources',
      description: 'Our AI finds and organizes the best tutorials, videos, and articles from 10+ sources',
      color: 'from-cyan-600 to-blue-600',
    },
    {
      icon: Rocket,
      title: 'Start Learning',
      description: 'Follow your personalized roadmap and master your skill with AI guidance',
      color: 'from-blue-600 to-purple-600',
    },
  ]

  return (
    <section className="py-20 sm:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Three simple steps to master any skill
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <Card key={index} hoverable className="text-center">
              <div className="mb-6 flex justify-center">
                <div className={`p-4 rounded-2xl bg-gradient-to-br ${step.color}`}>
                  <step.icon className="w-8 h-8 text-white" />
                </div>
              </div>
              <div className="mb-2 text-sm font-semibold text-teal-600 dark:text-teal-400">
                Step {index + 1}
              </div>
              <h3 className="text-xl font-bold mb-3">{step.title}</h3>
              <p className="text-slate-600 dark:text-slate-400">
                {step.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

