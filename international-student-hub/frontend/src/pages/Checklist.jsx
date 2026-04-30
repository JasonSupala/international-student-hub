import { useState, useEffect } from 'react'
import api from '../api/axios'
import './Checklist.css'

export default function Checklist() {
  const [categories, setCategories] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  // Track which items are being toggled (to disable button during API call)
  const [toggling, setToggling] = useState(new Set())

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    setLoading(true)
    try {
      const [catRes, sumRes] = await Promise.all([
        api.get('/checklist/categories/'),
        api.get('/checklist/progress/summary/'),
      ])
      setCategories(catRes.data.results || catRes.data)
      setSummary(sumRes.data)
    } catch (err) {
      setError('Could not load checklist. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function toggleItem(item) {
    if (toggling.has(item.id)) return
    setToggling((s) => new Set(s).add(item.id))

    const newCompleted = !item.completed

    // Optimistic update — update UI immediately, then sync with server
    setCategories((cats) =>
      cats.map((cat) => ({
        ...cat,
        items: cat.items.map((i) =>
          i.id === item.id ? { ...i, completed: newCompleted } : i
        ),
      }))
    )
    setSummary((s) => {
      if (!s) return s
      const delta = newCompleted ? 1 : -1
      const newCount = s.completed_count + delta
      return {
        ...s,
        completed_count: newCount,
        percent_complete: Math.round((newCount / s.total_items) * 1000) / 10,
      }
    })

    try {
      await api.post('/checklist/progress/', {
        item: item.id,
        completed: newCompleted,
      })
    } catch {
      // Revert on failure
      fetchData()
    } finally {
      setToggling((s) => {
        const next = new Set(s)
        next.delete(item.id)
        return next
      })
    }
  }

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  return (
    <div className="checklist-page page">
      <div className="page-header">
        <div className="container">
          <h1>Arrival Checklist</h1>
          <p>Track your first-week tasks — one at a time.</p>
        </div>
      </div>

      <div className="container">
        {error && <div className="alert alert-error" style={{marginBottom: 24}}>{error}</div>}

        {/* Progress bar */}
        {summary && (
          <div className="progress-bar-card card fade-up">
            <div className="progress-bar-card__top">
              <div>
                <h3>Your progress</h3>
                <p>{summary.completed_count} of {summary.total_items} tasks complete</p>
              </div>
              <span className="progress-pct">{summary.percent_complete}%</span>
            </div>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{ width: `${summary.percent_complete}%` }}
              />
            </div>
            {summary.percent_complete === 100 && (
              <div className="progress-complete">
                🎉 You've completed everything! Welcome to Taiwan.
              </div>
            )}
          </div>
        )}

        {/* Categories + items */}
        {categories.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>No checklist items yet</h3>
            <p>An admin needs to add checklist items via the Django admin.</p>
          </div>
        ) : (
          categories.map((cat, i) => (
            <div key={cat.id} className={`checklist-category fade-up fade-up-${Math.min(i + 1, 5)}`}>
              <div className="checklist-category__header">
                <span className="checklist-category__icon">{cat.icon || '📌'}</span>
                <h2>{cat.name}</h2>
                <span className="checklist-category__count">
                  {cat.items.filter(i => i.completed).length}/{cat.items.length}
                </span>
              </div>

              {cat.description && (
                <p className="checklist-category__desc">{cat.description}</p>
              )}

              <div className="checklist-items">
                {cat.items.filter(i => i.is_active).map((item) => (
                  <div
                    key={item.id}
                    className={`checklist-item card ${item.completed ? 'checklist-item--done' : ''}`}
                  >
                    <button
                      className={`checklist-checkbox ${item.completed ? 'checked' : ''}`}
                      onClick={() => toggleItem(item)}
                      disabled={toggling.has(item.id)}
                      aria-label={item.completed ? 'Mark incomplete' : 'Mark complete'}
                    >
                      {item.completed && '✓'}
                    </button>

                    <div className="checklist-item__body">
                      <h4 className="checklist-item__title">{item.title}</h4>
                      <p className="checklist-item__desc">{item.description}</p>

                      <div className="checklist-item__meta">
                        {item.estimated_minutes && (
                          <span className="badge badge-navy">
                            ⏱ ~{item.estimated_minutes} min
                          </span>
                        )}
                        {item.university && (
                          <span className="badge badge-gold">{item.university}</span>
                        )}
                        {item.resource_url && (
                          <a
                            href={item.resource_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="checklist-item__link"
                          >
                            More info →
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
