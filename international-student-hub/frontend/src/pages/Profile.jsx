import { useEffect, useState } from 'react'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import './Profile.css'

const UNIVERSITIES = [
  '', 'NSYSU', 'NTU', 'NCKU', 'NTHU', 'NYCU', 'NCU', 'NTNU', 'FJU',
  'CYCU', 'NCHU', 'CCU', 'NDHU', 'Other',
]

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'id', label: 'Bahasa Indonesia' },
  { value: 'vi', label: 'Vietnamese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'zh', label: 'Traditional Chinese' },
]

const MAX_AVATAR_SIZE = 5 * 1024 * 1024

function formatApiError(data) {
  if (!data) return 'Could not save profile.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const fieldErrors = Object.entries(data)
    .map(([field, messages]) => {
      const text = Array.isArray(messages) ? messages.join(' ') : messages
      return `${field}: ${text}`
    })
    .filter(Boolean)

  return fieldErrors[0] || 'Could not save profile.'
}

export default function Profile() {
  const { user, updateUser } = useAuth()
  const profile = user?.profile || {}

  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    country: profile.country || '',
    university: profile.university || '',
    bio: profile.bio || '',
    preferred_language: profile.preferred_language || 'en',
    arrival_date: profile.arrival_date || '',
  })
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [avatarFile, setAvatarFile] = useState(null)
  const [avatarPreview, setAvatarPreview] = useState(profile.avatar || '')

  useEffect(() => {
    if (!avatarFile) {
      setAvatarPreview(profile.avatar || '')
      return
    }
    const nextPreview = URL.createObjectURL(avatarFile)
    setAvatarPreview(nextPreview)
    return () => URL.revokeObjectURL(nextPreview)
  }, [avatarFile, profile.avatar])

  const handleChange = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0] || null
    setError('')

    if (file && file.size > MAX_AVATAR_SIZE) {
      setAvatarFile(null)
      e.target.value = ''
      setError('avatar: File too large. Maximum avatar size is 5MB.')
      return
    }

    setAvatarFile(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (avatarFile?.size > MAX_AVATAR_SIZE) {
      setError('avatar: File too large. Maximum avatar size is 5MB.')
      return
    }

    setSaving(true)
    setError('')
    setSuccess(false)
    try {
      const payload = avatarFile ? new FormData() : form
      if (avatarFile) {
        Object.entries(form).forEach(([key, value]) => payload.append(key, value ?? ''))
        payload.append('avatar', avatarFile)
      }
      await api.patch('/auth/profile/', payload)
      // Refresh user state from server
      const { data } = await api.get('/auth/profile/')
      updateUser(data)
      setAvatarFile(null)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(formatApiError(err.response?.data))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="profile-page page">
      <div className="page-header">
        <div className="container">
          <h1>My Profile</h1>
          <p>Update your details and preferences.</p>
        </div>
      </div>

      <div className="container">
        <div className="profile-layout">
          {/* Avatar card */}
          <div className="profile-avatar-card card fade-up">
            <div className="profile-avatar">
              {avatarPreview ? (
                <img src={avatarPreview} alt={`${user?.username}'s avatar`} />
              ) : (
                user?.username?.charAt(0).toUpperCase()
              )}
            </div>
            <h2 className="profile-username">@{user?.username}</h2>
            {profile.university && (
              <span className="badge badge-navy">{profile.university}</span>
            )}
            {profile.country && (
              <p className="profile-country">🌍 {profile.country}</p>
            )}
            {profile.arrival_date && (
              <p className="profile-arrival">
                ✈️ Arrived {new Date(profile.arrival_date).toLocaleDateString('en', { month: 'long', year: 'numeric' })}
              </p>
            )}
          </div>

          {/* Edit form */}
          <div className="profile-form-card card fade-up fade-up-1">
            <h3>Edit profile</h3>

            {success && <div className="alert alert-success">Profile saved successfully!</div>}
            {error   && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit} className="profile-form">
              <div className="profile-form__row">
                <div className="form-group">
                  <label>First name</label>
                  <input name="first_name" value={form.first_name} onChange={handleChange} placeholder="First name" />
                </div>
                <div className="form-group">
                  <label>Last name</label>
                  <input name="last_name" value={form.last_name} onChange={handleChange} placeholder="Last name" />
                </div>
              </div>

              <div className="form-group">
                <label>Profile picture</label>
                <input name="avatar" type="file" accept="image/*" onChange={handleAvatarChange} />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="your@email.com" />
              </div>

              <div className="profile-form__row">
                <div className="form-group">
                  <label>Country</label>
                  <input name="country" value={form.country} onChange={handleChange} placeholder="Indonesia" />
                </div>
                <div className="form-group">
                  <label>University</label>
                  <select name="university" value={form.university} onChange={handleChange}>
                    {UNIVERSITIES.map(u => (
                      <option key={u} value={u}>{u || '— Select —'}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Arrival date</label>
                <input name="arrival_date" type="date" value={form.arrival_date} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Bio <span className="label-hint">(max 500 chars)</span></label>
                <textarea
                  name="bio"
                  rows={3}
                  maxLength={500}
                  value={form.bio}
                  onChange={handleChange}
                  placeholder="Tell the community a bit about yourself…"
                />
                <span className="char-count">{form.bio.length}/500</span>
              </div>

              <div className="form-group">
                <label>Preferred language</label>
                <select name="preferred_language" value={form.preferred_language} onChange={handleChange}>
                  {LANGUAGES.map(l => (
                    <option key={l.value} value={l.value}>{l.label}</option>
                  ))}
                </select>
              </div>

              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Saving…' : 'Save changes'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
