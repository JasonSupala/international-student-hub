import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import './Auth.css'

const UNIVERSITIES = [
  '', 'NSYSU', 'NTU', 'NCKU', 'NTHU', 'NYCU', 'NCU', 'NTNU', 'FJU',
  'CYCU', 'NCHU', 'CCU', 'NDHU', 'Other',
]

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '',
    first_name: '', last_name: '', country: '', university: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await api.post('/auth/register/', form)
      // Auto-login after registration
      await login({ username: form.username, password: form.password })
      navigate('/checklist')
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        setErrors(data)
      } else {
        setErrors({ non_field_errors: ['Registration failed. Please try again.'] })
      }
    } finally {
      setLoading(false)
    }
  }

  const fieldError = (name) =>
    errors[name] ? <span className="field-error">{errors[name][0]}</span> : null

  return (
    <div className="auth-page page">
      <div className="auth-card auth-card--wide card fade-up">
        <div className="auth-card__header">
          <Link to="/" className="auth-logo">
            <span className="navbar__logo-mark">ISH</span>
          </Link>
          <h1>Create your account</h1>
          <p>Free forever. No spam. Just help for your first weeks.</p>
        </div>

        {errors.non_field_errors && (
          <div className="alert alert-error">{errors.non_field_errors[0]}</div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form__row">
            <div className="form-group">
              <label>First name</label>
              <input name="first_name" placeholder="Budi" value={form.first_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Last name</label>
              <input name="last_name" placeholder="Santoso" value={form.last_name} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label>Username *</label>
            <input name="username" placeholder="budi_taiwan" value={form.username} onChange={handleChange} required />
            {fieldError('username')}
          </div>

          <div className="form-group">
            <label>Email *</label>
            <input name="email" type="email" placeholder="budi@email.com" value={form.email} onChange={handleChange} required />
            {fieldError('email')}
          </div>

          <div className="auth-form__row">
            <div className="form-group">
              <label>Country</label>
              <input name="country" placeholder="Indonesia" value={form.country} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>University</label>
              <select name="university" value={form.university} onChange={handleChange}>
                {UNIVERSITIES.map((u) => (
                  <option key={u} value={u}>{u || '— Select —'}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Password *</label>
            <input name="password" type="password" placeholder="Min. 8 characters" value={form.password} onChange={handleChange} required />
            {fieldError('password')}
          </div>

          <div className="form-group">
            <label>Confirm password *</label>
            <input name="password2" type="password" placeholder="Repeat password" value={form.password2} onChange={handleChange} required />
          </div>

          <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
            {loading ? 'Creating account…' : 'Create account →'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Log in</Link>
        </p>
      </div>
    </div>
  )
}
