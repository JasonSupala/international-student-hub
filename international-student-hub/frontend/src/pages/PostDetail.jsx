import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [post, setPost] = useState(null)
  const [loading, setLoading] = useState(true)
  const [replyBody, setReplyBody] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get(`/community/posts/${id}/`)
      .then(r => setPost(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  async function handleUpvotePost() {
    if (!user) return
    const res = await api.post(`/community/posts/${id}/upvote/`)
    setPost(p => ({ ...p, upvotes: res.data.upvotes }))
  }

  async function handleUpvoteReply(replyId) {
    if (!user) return
    const res = await api.post(`/community/replies/${replyId}/upvote/`)
    setPost(p => ({
      ...p,
      replies: p.replies.map(r => r.id === replyId ? { ...r, upvotes: res.data.upvotes } : r)
    }))
  }

  async function handleAccept(replyId) {
    const res = await api.post(`/community/replies/${replyId}/accept/`)
    if (res.data.is_accepted) {
      setPost(p => ({
        ...p,
        replies: p.replies.map(r => ({ ...r, is_accepted: r.id === replyId }))
      }))
    }
  }

  async function handleReplySubmit(e) {
    e.preventDefault()
    if (!replyBody.trim()) return
    setSubmitting(true)
    try {
      const res = await api.post('/community/replies/', { post: id, body: replyBody })
      setPost(p => ({ ...p, replies: [...(p.replies || []), res.data] }))
      setReplyBody('')
    } catch {}
    finally { setSubmitting(false) }
  }

  if (loading) return <div className="loading-center" style={{paddingTop: 120}}><div className="spinner" /></div>
  if (!post) return (
    <div className="page" style={{paddingTop: 120, textAlign:'center'}}>
      <h2>Post not found</h2>
      <Link to="/community" className="btn btn-outline" style={{marginTop:16}}>← Back to Community</Link>
    </div>
  )

  return (
    <div className="post-detail-page page">
      <div className="container">
        <Link to="/community" className="back-link">← Back to Community</Link>

        {/* Post */}
        <div className="post-detail card fade-up">
          <div className="post-detail__main">
            <div className="post-detail__sidebar">
              <button className="post-upvote-btn" onClick={handleUpvotePost} disabled={!user}>
                ▲<span>{post.upvotes}</span>
              </button>
            </div>
            <div className="post-detail__content">
              <div className="post-detail__meta">
                {post.university && <span className="badge badge-gold">{post.university}</span>}
                <span className="post-meta-item">👤 {post.author?.username}</span>
                <span className="post-meta-item">{new Date(post.created_at).toLocaleDateString()}</span>
              </div>
              <h1 className="post-detail__title">{post.title}</h1>
              <p className="post-detail__body">{post.body}</p>
            </div>
          </div>
        </div>

        {/* Replies */}
        <div className="replies-section">
          <h2 className="replies-heading">
            {post.replies?.length || 0} {post.replies?.length === 1 ? 'reply' : 'replies'}
          </h2>

          {post.replies?.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h3>No replies yet</h3>
              <p>Be the first to answer!</p>
            </div>
          )}

          {post.replies?.map((reply, i) => (
            <div
              key={reply.id}
              className={`reply-card card fade-up fade-up-${Math.min(i + 1, 5)} ${reply.is_accepted ? 'reply-card--accepted' : ''}`}
            >
              <div className="reply-card__sidebar">
                <button
                  className="post-upvote-btn post-upvote-btn--sm"
                  onClick={() => handleUpvoteReply(reply.id)}
                  disabled={!user}
                >
                  ▲<span>{reply.upvotes}</span>
                </button>
                {reply.is_accepted && (
                  <span className="accepted-badge" title="Accepted answer">✓</span>
                )}
              </div>
              <div className="reply-card__content">
                <p className="reply-card__body">{reply.body}</p>
                <div className="reply-card__meta">
                  <span>👤 {reply.author?.username}</span>
                  <span>{new Date(reply.created_at).toLocaleDateString()}</span>
                  {user && post.author?.id === user.id && !reply.is_accepted && (
                    <button
                      className="btn btn-ghost accept-btn"
                      onClick={() => handleAccept(reply.id)}
                    >
                      ✓ Accept answer
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Reply form */}
        {user ? (
          <div className="reply-form card fade-up">
            <h3>Add a reply</h3>
            <form onSubmit={handleReplySubmit}>
              <textarea
                rows={4}
                placeholder="Share your knowledge or experience…"
                value={replyBody}
                onChange={e => setReplyBody(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Posting…' : 'Post reply →'}
              </button>
            </form>
          </div>
        ) : (
          <div className="alert alert-info" style={{marginTop: 24}}>
            <Link to="/login" className="auth-link">Log in</Link> to post a reply.
          </div>
        )}
      </div>
    </div>
  )
}
