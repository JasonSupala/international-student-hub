import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api, { clearAccessToken, refreshAccessToken, setAccessToken } from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isSuperuser, setIsSuperuser] = useState(false)
  const [loading, setLoading] = useState(true)

  const clearAuthState = useCallback(() => {
    clearAccessToken()
    setUser(null)
    setIsSuperuser(false)
  }, [])

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

  useEffect(() => {
    refreshAccessToken()
      .then(() => api.get('/auth/profile/'))
      .then(({ data }) => applyUser(data))
      .catch(() => clearAuthState())
      .finally(() => setLoading(false))
  }, [applyUser, clearAuthState])

  const login = useCallback(async (credentials) => {
    const { data } = await api.post('/auth/login/', credentials)
    setAccessToken(data.access)

    const { data: profile } = await api.get('/auth/profile/')
    return applyUser(profile)
  }, [applyUser])

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout/')
    } catch (_) {
      // Ignore server-side logout failures and clear client state regardless.
    } finally {
      clearAuthState()
    }
  }, [clearAuthState])

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
