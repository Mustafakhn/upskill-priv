'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import Card from '../common/Card'
import { 
  Code, 
  Music, 
  Palette, 
  ChefHat, 
  Camera, 
  Dumbbell, 
  Languages, 
  Briefcase,
  Heart,
  Wrench,
  BookOpen,
  Sparkles
} from 'lucide-react'

export default function FeaturedTopics() {
  const router = useRouter()

  const topics = [
    { name: 'Programming', icon: Code, color: 'from-blue-500 to-cyan-500', emoji: '💻' },
    { name: 'Music', icon: Music, color: 'from-purple-500 to-pink-500', emoji: '🎸' },
    { name: 'Art & Design', icon: Palette, color: 'from-pink-500 to-rose-500', emoji: '🎨' },
    { name: 'Cooking', icon: ChefHat, color: 'from-orange-500 to-red-500', emoji: '🍳' },
    { name: 'Photography', icon: Camera, color: 'from-teal-500 to-green-500', emoji: '📸' },
    { name: 'Fitness', icon: Dumbbell, color: 'from-green-500 to-emerald-500', emoji: '💪' },
    { name: 'Languages', icon: Languages, color: 'from-indigo-500 to-purple-500', emoji: '🌍' },
    { name: 'Business', icon: Briefcase, color: 'from-slate-500 to-gray-500', emoji: '💼' },
    { name: 'Health', icon: Heart, color: 'from-red-500 to-pink-500', emoji: '❤️' },
    { name: 'DIY & Crafts', icon: Wrench, color: 'from-yellow-500 to-orange-500', emoji: '🔨' },
    { name: 'Writing', icon: BookOpen, color: 'from-cyan-500 to-blue-500', emoji: '✍️' },
    { name: 'Personal Growth', icon: Sparkles, color: 'from-violet-500 to-purple-500', emoji: '✨' },
  ]

  const handleTopicClick = (topic: string) => {
    router.push(`/start?topic=${encodeURIComponent(topic)}`)
  }

  return (
    <section className="py-20 sm:py-32 bg-slate-50/50 dark:bg-slate-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Explore Popular Topics
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Choose from hundreds of topics or search for anything you want to learn
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {topics.map((topic) => (
            <Card
              key={topic.name}
              clickable
              hoverable
              onClick={() => handleTopicClick(topic.name)}
              className="text-center p-6 group"
            >
              <div className="mb-3 flex justify-center">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${topic.color} group-hover:scale-110 transition-transform duration-300`}>
                  <topic.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
                {topic.name}
              </h3>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

