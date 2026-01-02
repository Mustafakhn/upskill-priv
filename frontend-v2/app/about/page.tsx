import React from 'react'
import { Target, Users, Zap } from 'lucide-react'
import Image from 'next/image'
import Card from '../components/common/Card'

export default function AboutPage() {
  const features = [
    {
      icon: 'bulb',
      title: 'AI-Powered Curation',
      description: 'Our AI analyzes thousands of resources to find the best content for your learning goals',
    },
    {
      icon: Target,
      title: 'Personalized Paths',
      description: 'Every learning journey is tailored to your skill level, goals, and preferences',
    },
    {
      icon: Users,
      title: 'Learn Anything',
      description: 'From programming to cooking, music to marketing - master any skill you want',
    },
    {
      icon: Zap,
      title: 'Fast & Efficient',
      description: 'Stop wasting time searching. Get a structured roadmap in minutes',
    },
  ]

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">
            About{' '}
            <span className="bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Upskill
            </span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            We&apos;re on a mission to make learning accessible, structured, and personalized for everyone.
            No more endless searching - just clear paths to mastery.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} hoverable>
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center">
                  {feature.icon === 'bulb' ? (
                    <Image
                      src="/upskill-logo.svg"
                      alt="Bulb Icon"
                      width={24}
                      height={24}
                      className="w-6 h-6 object-contain"
                    />
                  ) : (
                    <feature.icon className="w-6 h-6 text-white" />
                  )}
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Mission */}
        <Card className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            Learning should be simple, not overwhelming. Every day, millions of people want to learn new skills
            but get lost in the sea of content online. Which tutorial should I follow? Is this resource good?
            Where do I even start?
          </p>
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            Upskill solves this problem. We use AI to understand your learning goals and create personalized
            roadmaps with the best resources from across the internet - all organized in a clear, step-by-step path.
          </p>
          <p className="text-slate-600 dark:text-slate-400">
            Whether you&apos;re learning to code, cook, play guitar, or anything else - we&apos;re here to guide you
            from beginner to expert.
          </p>
        </Card>
      </div>
    </div>
  )
}

