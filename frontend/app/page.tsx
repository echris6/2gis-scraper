'use client'

import { useState, useMemo } from 'react'
import Particles from './components/Particles'

interface Business {
  name: string
  address: string
  phone?: string
  website?: string
  rating?: number
  review_count?: number
}

interface ScrapeResult {
  success: boolean
  total: number
  stats: {
    with_phone: number
    with_website: number
    no_website: number
    avg_rating: number
  }
  businesses: Business[]
}

const PARTICLE_COLORS = ['#52525b', '#71717a', '#a1a1aa'];
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [city, setCity] = useState('moscow')
  const [query, setQuery] = useState('автомойка')
  const [pages, setPages] = useState(2)
  const [enrichContacts, setEnrichContacts] = useState(true)
  const [noWebsiteOnly, setNoWebsiteOnly] = useState(false)
  const [requirePhone, setRequirePhone] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScrapeResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastLogCount, setLastLogCount] = useState(0)

  // Poll backend logs while scraping
  const pollLogs = async () => {
    try {
      const response = await fetch(`${API_URL}/logs`)
      const data = await response.json()
      const logs = data.logs || []

      // Only log new entries
      if (logs.length > lastLogCount) {
        const newLogs = logs.slice(lastLogCount)
        newLogs.forEach((log: string) => {
          if (log.includes('ERROR')) {
            console.log(`%c[BACKEND] ${log}`, 'color: #ef4444; font-weight: 500')
          } else {
            console.log(`%c[BACKEND] ${log}`, 'color: #8b5cf6; font-weight: 500')
          }
        })
        setLastLogCount(logs.length)
      }
    } catch (err) {
      // Silently fail - don't spam console with polling errors
    }
  }

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    setLastLogCount(0)

    console.log('%c🚀 Starting scrape...', 'color: #10b981; font-weight: bold; font-size: 14px')
    console.log('City:', city)
    console.log('Query:', query)
    console.log('Pages:', pages)
    console.log('Enrich contacts:', enrichContacts)

    // Start polling logs
    const logPollInterval = setInterval(pollLogs, 500)

    try {
      const response = await fetch(`${API_URL}/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          city,
          query,
          pages,
          enrich_contacts: enrichContacts,
          no_website_only: noWebsiteOnly,
          require_phone: requirePhone,
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('%c❌ Backend error:', 'color: #ef4444; font-weight: bold', errorText)
        throw new Error('Failed to scrape')
      }

      const data = await response.json()

      // Get final logs
      await pollLogs()

      console.log('%c✅ Scrape completed successfully!', 'color: #10b981; font-weight: bold; font-size: 14px')
      console.log('Total businesses:', data.total)
      console.log('Stats:', data.stats)
      setResult(data)
    } catch (err) {
      console.error('%c❌ Error:', 'color: #ef4444; font-weight: bold', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      clearInterval(logPollInterval)
      setLoading(false)
    }
  }

  const downloadCSV = () => {
    if (!result) return

    // Helper function to escape CSV values
    const escapeCsvValue = (value: string | number | undefined): string => {
      if (value === undefined || value === null || value === '') return ''
      const str = String(value)
      // If value contains comma, quote, or newline, wrap in quotes and escape quotes
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`
      }
      return str
    }

    const headers = ['Name', 'Address', 'Phone', 'Website', 'Rating', 'Reviews']
    const rows = result.businesses.map(b => [
      escapeCsvValue(b.name),
      escapeCsvValue(b.address),
      escapeCsvValue(b.phone),
      escapeCsvValue(b.website),
      escapeCsvValue(b.rating),
      escapeCsvValue(b.review_count),
    ])

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${city}_${query}_leads.csv`
    link.click()
  }

  return (
    <div className="split-screen">
      {/* Left Sidebar - Form */}
      <aside className="sidebar">
        <Particles
          particleColors={PARTICLE_COLORS}
          particleCount={150}
          particleSpread={8}
          speed={0.05}
          particleBaseSize={80}
          moveParticlesOnHover={true}
          particleHoverFactor={0.5}
          alphaParticles={true}
          disableRotation={false}
        />
        <div className="sidebar-content">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-3xl font-semibold text-zinc-900 mb-2">
              2GIS Lead Scraper
            </h1>
            <p className="text-sm text-zinc-600">
              Extract qualified leads from 2GIS directory
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleScrape} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-zinc-900 mb-2">
                City
              </label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="input-field"
                placeholder="e.g., Moscow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-900 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="input-field"
                placeholder="e.g., автомойка"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-900 mb-2">
                Pages
              </label>
              <div className="number-input-wrapper">
                <input
                  type="number"
                  value={pages}
                  onChange={(e) => setPages(Number(e.target.value))}
                  min={1}
                  max={50}
                  className="input-field"
                />
                <div className="number-input-controls">
                  <button
                    type="button"
                    className="number-input-btn"
                    onClick={() => setPages(Math.min(50, pages + 1))}
                  >
                    <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                      <path d="M1 5L5 1L9 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                  <button
                    type="button"
                    className="number-input-btn"
                    onClick={() => setPages(Math.max(1, pages - 1))}
                  >
                    <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                      <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enrichContacts}
                  onChange={(e) => setEnrichContacts(e.target.checked)}
                  className="checkbox"
                />
                <span className="text-sm text-zinc-700">
                  Enrich with phone/website
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={noWebsiteOnly}
                  onChange={(e) => setNoWebsiteOnly(e.target.checked)}
                  className="checkbox"
                />
                <span className="text-sm text-zinc-700">
                  No website only
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={requirePhone}
                  onChange={(e) => setRequirePhone(e.target.checked)}
                  className="checkbox"
                />
                <span className="text-sm text-zinc-700">
                  Require phone
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Scraping...' : 'Start Scraping'}
            </button>
          </form>

          {/* Error */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="mt-12 space-y-6">
              {/* Header with Download */}
              <div className="flex items-center justify-between">
                <h2 className="text-base font-medium text-zinc-900">
                  {result.total} businesses found
                </h2>
                <button
                  onClick={downloadCSV}
                  className="text-xs font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                >
                  Download CSV →
                </button>
              </div>

              {/* Stats Row */}
              <div className="grid grid-cols-4 gap-3 py-3 border-y border-zinc-800">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-zinc-600 mb-1">Phone</p>
                  <p className="text-sm font-medium text-zinc-300">
                    {result.stats.with_phone} <span className="text-xs text-zinc-600">({Math.round((result.stats.with_phone / result.total) * 100)}%)</span>
                  </p>
                </div>

                <div>
                  <p className="text-[10px] uppercase tracking-wider text-zinc-600 mb-1">No Web</p>
                  <p className="text-sm font-medium text-zinc-300">
                    {result.stats.no_website} <span className="text-xs text-zinc-600">({Math.round((result.stats.no_website / result.total) * 100)}%)</span>
                  </p>
                </div>

                <div>
                  <p className="text-[10px] uppercase tracking-wider text-zinc-600 mb-1">Website</p>
                  <p className="text-sm font-medium text-zinc-300">
                    {result.stats.with_website} <span className="text-xs text-zinc-600">({Math.round((result.stats.with_website / result.total) * 100)}%)</span>
                  </p>
                </div>

                <div>
                  <p className="text-[10px] uppercase tracking-wider text-zinc-600 mb-1">Rating</p>
                  <p className="text-sm font-medium text-zinc-300">
                    {result.stats.avg_rating} <span className="text-xs text-zinc-600">/5.0</span>
                  </p>
                </div>
              </div>

              {/* Business List */}
              <div className="space-y-2">
                {result.businesses.slice(0, 10).map((business, idx) => (
                  <div key={idx} className="business-row">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="text-xs font-medium text-zinc-200 flex-1">
                          {business.name}
                        </h3>
                        {business.rating && (
                          <span className="text-[11px] text-zinc-400 flex-shrink-0">★ {business.rating}</span>
                        )}
                      </div>
                      <p className="text-[11px] text-zinc-600">{business.address}</p>
                      <div className="flex items-center gap-3 text-[11px] mt-0.5">
                        {business.phone && (
                          <span className="text-zinc-500">{business.phone}</span>
                        )}
                        {business.website && (
                          <a
                            href={business.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-zinc-400 hover:text-zinc-200 transition-colors"
                          >
                            Website →
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {result.businesses.length > 10 && (
                  <p className="text-[11px] text-zinc-600 text-center py-3">
                    +{result.businesses.length - 10} more in CSV
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Right Side - Background Image */}
      <div className="bg-showcase"></div>
    </div>
  )
}
