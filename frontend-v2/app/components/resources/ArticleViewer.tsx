'use client'

import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { ExternalLink, Loader2 } from 'lucide-react'
import Card from '../common/Card'
import Button from '../common/Button'
import { apiClient } from '@/app/services/api'

interface ArticleViewerProps {
  resourceId: string
  resourceUrl: string
  resourceTitle?: string
  resourceType: 'video' | 'blog' | 'doc'
}

export default function ArticleViewer({ 
  resourceId, 
  resourceUrl, 
  resourceType 
}: ArticleViewerProps) {
  const [content, setContent] = useState<string | null>(null)
  const [htmlContent, setHtmlContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scraped, setScraped] = useState(false)

  useEffect(() => {
    const loadContent = async () => {
      if (resourceType === 'video') {
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const data = await apiClient.getResourceContent(resourceId)
        setContent(data.content)
        setHtmlContent(data.html || null)
        setScraped(data.scraped)
        if (data.message) {
          setError(data.message)
        }
      } catch (err) {
        console.error('Error loading article content:', err)
        setError('Failed to load article content')
      } finally {
        setLoading(false)
      }
    }

    loadContent()
  }, [resourceId, resourceType])

  if (resourceType === 'video') {
    return null // Videos are handled separately
  }

  if (loading) {
    return (
      <Card className="mb-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-teal-600 dark:text-teal-400 animate-spin" />
        </div>
      </Card>
    )
  }

  if (error && !content) {
    return (
      <Card className="mb-6 relative z-0 pointer-events-none">
        <p className="text-slate-600 dark:text-slate-400 mb-4">{error}</p>
        <Button
          variant="primary"
          icon={<ExternalLink className="w-4 h-4" />}
          onClick={() => window.open(resourceUrl, '_blank')}
          className="pointer-events-auto"
        >
          Open Original Article
        </Button>
      </Card>
    )
  }

  if (!content || content.length < 100) {
    return (
      <Card className="mb-6 relative z-0 pointer-events-none">
        <p className="text-slate-600 dark:text-slate-400 mb-4">
          {error || 'Full article content is not available. Please visit the original source to read the complete article.'}
        </p>
        <Button
          variant="primary"
          icon={<ExternalLink className="w-4 h-4" />}
          onClick={() => window.open(resourceUrl, '_blank')}
          className="pointer-events-auto"
        >
          Open Original Article
        </Button>
      </Card>
    )
  }

  // Format content for better readability
  const formatContent = (text: string): string => {
    const paragraphs = text.split('\n\n').map(p => p.trim()).filter(p => p.length > 0)
    const seen = new Set<string>()
    const uniqueParagraphs: string[] = []
    
    for (const para of paragraphs) {
      const key = para.toLowerCase().substring(0, 100)
      if (seen.has(key)) continue
      
      if (para.length < 30) {
        const navKeywords = ['home', 'about', 'contact', 'menu', 'navigation', 'skip', 'jump', 'cookie', 'privacy', 'terms']
        if (navKeywords.some(keyword => para.toLowerCase().includes(keyword))) {
          continue
        }
      }
      
      if (para.length < 80 && para.split(' ').length < 10) {
        const isLikelyHeader = para.split(' ').every(word => 
          word.length > 0 && word[0] === word[0].toUpperCase()
        )
        if (isLikelyHeader && seen.size > 0) continue
      }
      
      seen.add(key)
      uniqueParagraphs.push(para)
    }
    
    return uniqueParagraphs.join('\n\n')
  }
  
  const formattedContent = formatContent(content)

  // Extract main content from HTML
  const extractMainContentFromHTML = (html: string, baseUrl: string): string => {
    if (typeof window === 'undefined') return ''
    
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      
      const unwanted = doc.querySelectorAll('script, style, nav, header, footer, aside, .nav, .menu, .sidebar, .ad, .advertisement, .social, .share, .breadcrumb, .cookie, .newsletter, .related, .comments, .comment-section')
      unwanted.forEach(el => el.remove())
      
      const mainContent = doc.querySelector('article, main, .content, .main, .post, .article, .entry, .body, .text, .prose') || doc.body
      
      if (!mainContent) return ''
      
      // Fix links
      const links = mainContent.querySelectorAll('a[href]')
      links.forEach(link => {
        const href = link.getAttribute('href')
        if (href) {
          try {
            if (!href.startsWith('http://') && !href.startsWith('https://')) {
              if (href.startsWith('//')) {
                link.setAttribute('href', `https:${href}`)
              } else if (href.startsWith('/')) {
                const baseUrlObj = new URL(baseUrl)
                link.setAttribute('href', `${baseUrlObj.origin}${href}`)
              } else {
                const resolvedUrl = new URL(href, baseUrl)
                link.setAttribute('href', resolvedUrl.href)
              }
            }
            link.setAttribute('target', '_blank')
            link.setAttribute('rel', 'noopener noreferrer')
          } catch (error) {
            console.warn('Error fixing link URL:', href, error)
          }
        }
      })
      
      // Fix images
      const images = mainContent.querySelectorAll('img[src]')
      images.forEach(img => {
        const src = img.getAttribute('src')
        if (src) {
          try {
            if (!src.startsWith('http://') && !src.startsWith('https://')) {
              if (src.startsWith('//')) {
                img.setAttribute('src', `https:${src}`)
              } else if (src.startsWith('/')) {
                const baseUrlObj = new URL(baseUrl)
                img.setAttribute('src', `${baseUrlObj.origin}${src}`)
              } else {
                const resolvedUrl = new URL(src, baseUrl)
                img.setAttribute('src', resolvedUrl.href)
              }
            }
          } catch (error) {
            console.warn('Error fixing image URL:', src, error)
          }
        }
      })
      
      return mainContent.innerHTML
    } catch (error) {
      console.error('Error parsing HTML:', error)
      return ''
    }
  }

  return (
    <Card className="mb-6">
      {!scraped && (
        <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-sm text-yellow-700 dark:text-yellow-400">
            This content was fetched from the original source. For the best experience, you can also{' '}
            <a
              href={resourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-teal-600 dark:text-teal-400 hover:underline font-medium"
            >
              visit the original article
            </a>
            .
          </p>
        </div>
      )}
      
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <div className="text-slate-700 dark:text-slate-300 leading-relaxed">
          {htmlContent && typeof window !== 'undefined' ? (
            <div 
              className="article-content"
              dangerouslySetInnerHTML={{ 
                __html: extractMainContentFromHTML(htmlContent, resourceUrl) 
              }}
            />
          ) : content && (content.includes('#') || content.includes('**') || content.includes('`')) ? (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-4 text-slate-600 dark:text-slate-400 leading-relaxed">{children}</p>,
                h1: ({ children }) => <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4 mt-6 first:mt-0">{children}</h1>,
                h2: ({ children }) => <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-3 mt-5 first:mt-0">{children}</h2>,
                h3: ({ children }) => <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2 mt-4 first:mt-0">{children}</h3>,
                h4: ({ children }) => <h4 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2 mt-3 first:mt-0">{children}</h4>,
                strong: ({ children }) => <strong className="font-semibold text-slate-900 dark:text-slate-100">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
                code: ({ children, className }) => {
                  const isInline = !className
                  return isInline ? (
                    <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-sm font-mono text-teal-600 dark:text-teal-400">{children}</code>
                  ) : (
                    <code className="block bg-slate-100 dark:bg-slate-800 p-4 rounded-lg text-sm font-mono overflow-x-auto my-4 border border-slate-200 dark:border-slate-700">
                      {children}
                    </code>
                  )
                },
                ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-2 ml-4">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-2 ml-4">{children}</ol>,
                li: ({ children }) => <li className="text-slate-600 dark:text-slate-400">{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-teal-600 dark:border-teal-400 pl-4 italic my-4 text-slate-600 dark:text-slate-400">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-teal-600 dark:text-teal-400 hover:underline"
                  >
                    {children}
                  </a>
                ),
                hr: () => <hr className="my-6 border-slate-200 dark:border-slate-700" />,
              }}
            >
              {formattedContent}
            </ReactMarkdown>
          ) : (
            <div className="space-y-6">
              {formattedContent.split('\n\n').map((paragraph, idx) => {
                const isHeading = paragraph.length < 120 && 
                                 (paragraph.split(' ').length < 15) &&
                                 (paragraph.endsWith(':') || 
                                  paragraph.split(' ').every(word => 
                                    word.length > 0 && (word[0] === word[0].toUpperCase() || /^\d+\./.test(word))
                                  ))
                
                const isListItem = /^[\d\-\*•]\s+/.test(paragraph.trim())
                
                if (isHeading) {
                  const level = paragraph.length < 60 ? 'h2' : 'h3'
                  const HeadingTag = level === 'h2' ? 'h2' : 'h3'
                  return (
                    <HeadingTag 
                      key={idx} 
                      className={`font-semibold text-slate-900 dark:text-slate-100 mb-2 mt-6 first:mt-0 ${
                        level === 'h2' ? 'text-2xl' : 'text-xl'
                      }`}
                    >
                      {paragraph.replace(/^[\d\-\*•]\s+/, '').replace(/:$/, '')}
                    </HeadingTag>
                  )
                }
                
                if (isListItem) {
                  return (
                    <div key={idx} className="ml-4">
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                        {paragraph}
                      </p>
                    </div>
                  )
                }
                
                return (
                  <p key={idx} className="text-slate-600 dark:text-slate-400 leading-relaxed text-base">
                    {paragraph}
                  </p>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
        <Button
          variant="outline"
          icon={<ExternalLink className="w-4 h-4" />}
          onClick={() => window.open(resourceUrl, '_blank')}
        >
          Visit Original Source
        </Button>
      </div>
    </Card>
  )
}

