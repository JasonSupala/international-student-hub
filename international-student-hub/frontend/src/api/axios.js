/**
 * api/axios.js — Configured Axios instance
 *
 * - Automatically attaches the JWT access token to every request
 * - On 401 (token expired), silently refreshes and retries the original request
 * - On refresh failure, clears tokens and redirects to /login
 */

import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor ──────────────────────────────────────────────────────
// Attach the access token to every outgoing request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor ─────────────────────────────────────────────────────
// Handle 401 errors by refreshing the token and retrying
let isRefreshing = false
let failedQueue = []   // holds requests that came in while a refresh was in progress

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only handle 401 errors that haven't already been retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request until the refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh')

      if (!refreshToken) {
        // No refresh token — user must log in again
        clearAuthAndRedirect()
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: refreshToken,
        })

        localStorage.setItem('access', data.access)
        api.defaults.headers.common.Authorization = `Bearer ${data.access}`

        processQueue(null, data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        clearAuthAndRedirect()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

function clearAuthAndRedirect() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  // Redirect to login without using React Router (interceptor is outside component tree)
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

export default api
