'use client'

import React from 'react'
import { MessageSquare } from 'lucide-react'
import Image from 'next/image'
import Card from '../common/Card'

const exampleConversations = [
  {
    user: "I want to learn Python programming from scratch",
    ai: "I'll create a personalized learning path for Python programming. Let me curate the best resources including beginner-friendly tutorials, interactive exercises, and practical projects to help you master Python step by step."
  },
  {
    user: "Teach me how to play guitar",
    ai: "Great! I'll design a learning journey for guitar that starts with the basics - holding the guitar, reading tabs, and learning your first chords. We'll progress through fingerpicking, strumming patterns, and eventually playing your favorite songs."
  },
  {
    user: "I want to master Italian cooking",
    ai: "Perfect! I'll create a culinary journey through Italian cuisine. We'll start with fundamental techniques like making fresh pasta, then explore regional specialties, classic sauces, and traditional recipes that will make you feel like you're cooking in a Tuscan kitchen."
  }
]

export default function ChatExamples() {
  return (
    <section className="py-16 sm:py-24 bg-slate-50 dark:bg-slate-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 text-sm font-medium mb-4">
            <MessageSquare className="w-4 h-4" />
            See How It Works
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            AI-Powered Learning Conversations
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Just tell our AI what you want to learn, and it creates a personalized learning path with curated resources
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exampleConversations.map((example, index) => (
            <Card key={index} className="p-6">
              <div className="space-y-4">
                {/* User message */}
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">U</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">You</p>
                    <p className="text-sm text-slate-700 dark:text-slate-300">{example.user}</p>
                  </div>
                </div>

                {/* AI response */}
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-cyan-600 flex items-center justify-center flex-shrink-0">
                    <Image
                      src="/upskill-logo.svg"
                      alt="Bulb Icon"
                      width={16}
                      height={16}
                      className="w-4 h-4 object-contain"
                    />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">AI Assistant</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{example.ai}</p>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Ready to start your learning journey?
          </p>
          <a
            href="/register"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-white rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Get Started Free
            <Image
              src="/upskill-logo.svg"
              alt="Bulb Icon"
              width={16}
              height={16}
              className="w-4 h-4 object-contain"
            />
          </a>
        </div>
      </div>
    </section>
  )
}

