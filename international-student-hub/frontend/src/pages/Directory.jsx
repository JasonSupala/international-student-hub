import { useState, useEffect, useCallback } from 'react'
import api from '../api/axios'
import './Directory.css'

export default function Directory() {
  const [entries, setEntries] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/directory/categories/')
      .then(r => setCategories(r.data.results || r.data))
      .catch(() => {})
  }, [])

  const fetchEntries = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (search)         params.search = search
      if (activeCategory) params['category__slug'] = activeCategory
      const res = await api.get('/directory/entries/', { params })
      setEntries(res.data.results || res.data)
    } catch {
      setError('Could not load directory.')
    } finally {
      setLoading(false)
    }
  }, [search, activeCategory])

  useEffect(() => {
    const timer = setTimeout(fetchEntries, 300) // debounce search
    return () => clearTimeout(timer)
  }, [fetchEntries])

  return (
    <div className="directory-page page">
      <div className="page-header">
        <div className="container">
          <h1>Service Directory</h1>
          <p>Student-friendly places near your campus — verified by the community.</p>
        </div>
      </div>

      <div className="container">
        {/* Search bar */}
        <div className="directory-search fade-up">
          <input
            className="directory-search__input"
            type="search"
            placeholder="Search services, food, clinics, SIM cards…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="directory-search__icon">🔍</span>
        </div>

        {/* Category filter tabs */}
        <div className="directory-tabs fade-up fade-up-1">
          <button
            className={`directory-tab ${activeCategory === '' ? 'active' : ''}`}
            onClick={() => setActiveCategory('')}
          >
            All
          </button>
          {categories.map(cat => (
            <button
              key={cat.id}
              className={`directory-tab ${activeCategory === cat.slug ? 'active' : ''}`}
              onClick={() => setActiveCategory(activeCategory === cat.slug ? '' : cat.slug)}
            >
              {cat.icon && <span>{cat.icon}</span>} {cat.name}
            </button>
          ))}
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="loading-center"><div className="spinner" /></div>
        ) : entries.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No results found</h3>
            <p>Try a different search or category filter.</p>
          </div>
        ) : (
          <div className="directory-grid">
            {entries.map((entry, i) => (
              <div key={entry.id} className={`entry-card card fade-up fade-up-${Math.min(i % 5 + 1, 5)}`}>
                <div className="entry-card__top">
                  <div>
                    <h3 className="entry-card__name">{entry.name}</h3>
                    <span className="badge badge-navy">{entry.category_name}</span>
                  </div>
                  {/*entry.verified && (
                    <span className="badge badge-green entry-verified">✓ Verified</span>
                  )*/}
                </div>

                <p className="entry-card__desc">{entry.description}</p>

                <div className="entry-card__details">
                  {entry.address && (
                    <div className="entry-detail">
                      <span>📍</span>
                      <span>{entry.address}</span>
                    </div>
                  )}
                  {entry.hours && (
                    <div className="entry-detail">
                      <span>🕐</span>
                      <span>{entry.hours}</span>
                    </div>
                  )}
                  {entry.phone && (
                    <div className="entry-detail">
                      <span>📞</span>
                      <a href={`tel:${entry.phone}`}>{entry.phone}</a>
                    </div>
                  )}
                </div>

                {entry.tags && (
                  <div className="entry-card__tags">
                    {entry.tags.split(',').map(tag => tag.trim()).filter(Boolean).map(tag => (
                      <span key={tag} className="entry-tag">{tag}</span>
                    ))}
                  </div>
                )}

                <div className="entry-card__actions">
                  {entry.maps_link && (
                    <a href={entry.maps_link} target="_blank" rel="noopener noreferrer" className="btn btn-outline entry-btn">
                      📍 View on Maps
                    </a>
                  )}
                  {entry.website && (
                    <a href={entry.website} target="_blank" rel="noopener noreferrer" className="btn btn-ghost entry-btn">
                      Website →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
