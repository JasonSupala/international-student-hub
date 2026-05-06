import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import api from '../api/axios'
import './DetailPages.css'

export default function DirectoryEntryDetail() {
  const { slug } = useParams()
  const [entry, setEntry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    api.get(`/directory/entries/${slug}/`)
      .then((res) => {
        setEntry(res.data)
        setError('')
      })
      .catch((err) => {
        setError(err.response?.status === 404 ? 'Directory entry not found.' : 'Could not load directory entry.')
      })
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  const tags = entry?.tags?.split(',').map(tag => tag.trim()).filter(Boolean) || []

  return (
    <div className="detail-page page">
      <div className="container">
        <Link className="detail-back" to="/directory">Back to directory</Link>

        {error ? (
          <div className="alert alert-error">{error}</div>
        ) : entry && (
          <div className="detail-layout">
            <article className="detail-main card">
              <h1 className="detail-title">{entry.name}</h1>
              {entry.description && <p className="detail-summary">{entry.description}</p>}
              <div className="detail-markdown">
                <ReactMarkdown>{entry.detail_description || entry.description}</ReactMarkdown>
              </div>
            </article>

            <aside className="detail-side card">
              <div className="detail-meta">
                {entry.category_name && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">Category</span>
                    <span>{entry.category_name}</span>
                  </div>
                )}
                {entry.university && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">University</span>
                    <span>{entry.university}</span>
                  </div>
                )}
                {entry.address && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">Address</span>
                    <span>{entry.address}</span>
                  </div>
                )}
                {entry.hours && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">Hours</span>
                    <span>{entry.hours}</span>
                  </div>
                )}
                {entry.phone && (
                  <div className="detail-meta-row">
                    <span className="detail-meta-label">Phone</span>
                    <a href={`tel:${entry.phone}`}>{entry.phone}</a>
                  </div>
                )}
                <div className="detail-meta-row">
                  <span className="detail-meta-label">Verified</span>
                  <span>{entry.verified ? 'Yes' : 'No'}</span>
                </div>
              </div>

              {tags.length > 0 && (
                <div className="detail-tags">
                  {tags.map(tag => <span key={tag} className="entry-tag">{tag}</span>)}
                </div>
              )}

              <div className="detail-actions">
                {entry.maps_link && (
                  <a className="btn btn-outline" href={entry.maps_link} target="_blank" rel="noopener noreferrer">
                    View on Maps
                  </a>
                )}
                {entry.website && (
                  <a className="btn btn-primary" href={entry.website} target="_blank" rel="noopener noreferrer">
                    Website
                  </a>
                )}
              </div>
            </aside>
          </div>
        )}
      </div>
    </div>
  )
}
