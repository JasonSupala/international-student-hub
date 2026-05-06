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
  const [isSuperuser, setIsSuperuser] = useState(false)
  const [loading, setLoading] = useState(true) // checking stored token on mount

  const applyUser = useCallback(async (profile) => {
    const normalized = {
      ...profile,
      is_staff: Boolean(profile?.is_staff),
      is_superuser: Boolean(profile?.is_superuser),
    }

    if (!normalized.is_superuser) {
      try {
        await api.get('/admin-panel/users/', { params: { page_size: 1 } })
        normalized.is_superuser = true
      } catch (_) {
        normalized.is_superuser = false
      }
    }

    setUser(normalized)
    setIsSuperuser(normalized.is_superuser)
    return normalized
  }, [])

  // On mount: if we have a stored access token, fetch the user profile
  useEffect(() => {
    const token = localStorage.getItem('access')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .get('/auth/profile/')
      .then(({ data }) => applyUser(data))
      .catch(() => {
        // Token invalid or expired and refresh also failed — clear everything
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        setUser(null)
        setIsSuperuser(false)
      })
      .finally(() => setLoading(false))
  }, [applyUser])

  const login = useCallback(async (credentials) => {
    // POST /api/v1/auth/login/ → { access, refresh }
    const { data } = await api.post('/auth/login/', credentials)
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)

    // Fetch the full user profile after login
    const { data: profile } = await api.get('/auth/profile/')
    return applyUser(profile)
  }, [applyUser])

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
      setIsSuperuser(false)
    }
  }, [])

  const updateUser = useCallback((updatedUser) => {
    const normalized = {
      ...updatedUser,
      is_staff: Boolean(updatedUser?.is_staff),
      is_superuser: Boolean(updatedUser?.is_superuser),
    }
    setUser(normalized)
    setIsSuperuser(normalized.is_superuser)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isSuperuser, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
