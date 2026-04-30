/**
 * context/AuthContext.jsx
 *
 * Provides authentication state to the entire app.
 * Wrap your app in <AuthProvider> and consume with useAuth().
 *
 * useAuth() returns:
 *   user       — current user object (null if not logged in)
 *   loading    — true while checking auth on first load
 *   login()    — call with { username, password }, stores tokens
 *   logout()   — blacklists refresh token, clears state
 *   updateUser()— update local user state after profile edit
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true) // checking stored token on mount

  // On mount: if we have a stored access token, fetch the user profile
  useEffect(() => {
    const token = localStorage.getItem('access')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .get('/auth/profile/')
      .then(({ data }) => setUser(data))
      .catch(() => {
        // Token invalid or expired and refresh also failed — clear everything
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (credentials) => {
    // POST /api/v1/auth/login/ → { access, refresh }
    const { data } = await api.post('/auth/login/', credentials)
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)

    // Fetch the full user profile after login
    const { data: profile } = await api.get('/auth/profile/')
    setUser(profile)
    return profile
  }, [])

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem('refresh')
    try {
      if (refresh) await api.post('/auth/logout/', { refresh })
    } catch (_) {
      // Ignore errors — clear local state regardless
    } finally {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      setUser(null)
    }
  }, [])

  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
