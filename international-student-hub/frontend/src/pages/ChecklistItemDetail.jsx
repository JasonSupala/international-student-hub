import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import api from '../api/axios'
import './DetailPages.css'

export default function ChecklistItemDetail() {
  const { slug } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    api.get(`/checklist/items/${slug}/`)
      .then((res) => {
        setItem(res.data)
        setError('')
      })
      .catch((err) => {
        setError(err.response?.status === 404 ? 'Checklist item not found.' : 'Could not load checklist item.')
      })
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  return (
    <div className="detail-page page">
      <div className="container">
        <Link className="detail-back" to="/checklist">Back to checklist</Link>

        {error ? (
          <div className="alert alert-error">{error}</div>
        ) : item && (
          <div className="detail-layout">
            <article className="detail-main card">
              <h1 className="detail-title">{item.title}</h1>
              {item.description && <p className="detail-summary">{item.description}</p>}
              <div className="detail-markdown">
                <ReactMarkdown>{item.detail_description || item.description}</ReactMarkdown>
              </div>
            </article>

            <aside className="detail-side card">
              <div className="detail-meta">
                {item.estimated_minutes && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">Estimated time</span>
                    <span>~{item.estimated_minutes} min</span>
                  </div>
                )}
                {item.university && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">University</span>
                    <span>{item.university}</span>
                  </div>
                )}
                <div className="detail-meta-row">
                  <span className="detail-meta-label">Status</span>
                  <span>{item.completed ? 'Completed' : 'Not completed'}</span>
                </div>
              </div>

              {item.resource_url && (
                <div className="detail-actions">
                  <a className="btn btn-primary" href={item.resource_url} target="_blank" rel="noopener noreferrer">
                    Open resource
                  </a>
                </div>
              )}
            </aside>
          </div>
        )}
      </div>
    </div>
  )
}
