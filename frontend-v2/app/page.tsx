'use client'

import Hero from './components/home/Hero'
import HowItWorks from './components/home/HowItWorks'
import FeaturedTopics from './components/home/FeaturedTopics'
import Stats from './components/home/Stats'
import ChatExamples from './components/home/ChatExamples'

export default function Home() {
  return (
    <div>
      <Hero />
      <ChatExamples />
      <HowItWorks />
      <FeaturedTopics />
      <Stats />
    </div>
  )
}
