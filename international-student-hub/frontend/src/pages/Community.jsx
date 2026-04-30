import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import './Community.css'

export default function Community() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', body: '', university: '' })
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState('')

  useEffect(() => {
    const timer = setTimeout(fetchPosts, 250)
    return () => clearTimeout(timer)
  }, [search])

  async function fetchPosts() {
    setLoading(true)
    try {
      const params = {}
      if (search) params.search = search
      const res = await api.get('/community/posts/', { params })
      setPosts(res.data.results || res.data)
    } catch {
      // fail silently — posts are public
    } finally {
      setLoading(false)
    }
  }

  async function handleUpvote(e, postId) {
    e.preventDefault()
    e.stopPropagation()
    if (!user) { navigate('/login'); return }
    try {
      const res = await api.post(`/community/posts/${postId}/upvote/`)
      setPosts(ps => ps.map(p => p.id === postId ? { ...p, upvotes: res.data.upvotes } : p))
    } catch {}
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      const res = await api.post('/community/posts/', form)
      setPosts(ps => [res.data, ...ps])
      setForm({ title: '', body: '', university: '' })
      setShowForm(false)
      navigate(`/community/${res.data.id}`)
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Could not create post.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="community-page page">
      <div className="page-header">
        <div className="container">
          <h1>Community Q&A</h1>
          <p>Ask questions, share tips, connect with other international students.</p>
        </div>
      </div>

      <div className="container">
        <div className="community-toolbar fade-up">
          <input
            className="community-search"
            type="search"
            placeholder="Search questions…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {user ? (
            <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? '✕ Cancel' : '+ New post'}
            </button>
          ) : (
            <Link to="/login" className="btn btn-outline">Log in to post</Link>
          )}
        </div>

        {/* New post form */}
        {showForm && (
          <div className="post-form card fade-up">
            <h3>Ask a question or share a tip</h3>
            {formError && <div className="alert alert-error">{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  placeholder="e.g. How do I open a bank account without Chinese?"
                  value={form.title}
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label>Details *</label>
                <textarea
                  rows={4}
                  placeholder="Share more context, what you've tried, etc."
                  value={form.body}
                  onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label>University (optional)</label>
                <input
                  placeholder="e.g. NSYSU"
                  value={form.university}
                  onChange={e => setForm(f => ({ ...f, university: e.target.value }))}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Posting…' : 'Post question →'}
              </button>
            </form>
          </div>
        )}

        {loading ? (
          <div className="loading-center"><div className="spinner" /></div>
        ) : posts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>No posts yet</h3>
            <p>Be the first to ask a question!</p>
          </div>
        ) : (
          <div className="posts-list">
            {posts.map((post, i) => (
              <Link
                key={post.id}
                to={`/community/${post.id}`}
                className={`post-card card fade-up fade-up-${Math.min(i % 5 + 1, 5)}`}
              >
                <div className="post-card__left">
                  <button
                    className="post-upvote"
                    onClick={e => handleUpvote(e, post.id)}
                    title="Upvote"
                  >
                    ▲ <span>{post.upvotes}</span>
                  </button>
                </div>
                <div className="post-card__body">
                  <h3 className="post-card__title">{post.title}</h3>
                  <p className="post-card__excerpt">
                    {post.body.length > 160 ? post.body.slice(0, 160) + '…' : post.body}
                  </p>
                  <div className="post-card__meta">
                    <span>👤 {post.author?.username || 'Anonymous'}</span>
                    {post.university && <span className="badge badge-gold">{post.university}</span>}
                    <span>💬 {post.reply_count} replies</span>
                    <span>{new Date(post.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
