import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const isAdmin = config.url?.includes('/admin/')
  const token = isAdmin ? localStorage.getItem('admin_token') : localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Silent token refresh ──────────────────────────────────────────────────────

let _isRefreshing = false
let _pendingQueue: Array<(token: string | null) => void> = []

function _notifyPending(token: string | null) {
  _pendingQueue.forEach((cb) => cb(token))
  _pendingQueue = []
}

/** Calls /auth/refresh via raw axios (bypasses our interceptors to avoid loops). */
async function _tryRefresh(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null
  try {
    const res = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
    const wrapper = res.data // { code, data: { access_token, refresh_token } }
    if (wrapper?.code !== 0 || !wrapper?.data?.access_token) return null
    localStorage.setItem('token', wrapper.data.access_token)
    localStorage.setItem('refresh_token', wrapper.data.refresh_token)
    return wrapper.data.access_token as string
  } catch {
    return null
  }
}

function _handleSessionExpired() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('admin_token')
  localStorage.removeItem('user')
  ElMessage.warning({ message: '登录已过期，请重新登录', duration: 3000 })
  const path = window.location.pathname
  // Small delay so the toast is visible before navigation
  setTimeout(() => {
    window.location.href = path.startsWith('/admin') ? '/admin/login' : '/login'
  }, 1500)
}

// ─────────────────────────────────────────────────────────────────────────────

api.interceptors.response.use(
  async (res) => {
    const data = res.data
    if (data.code !== 0) {
      const isAdmin = res.config.url?.includes('/admin/')
      const isRetry = (res.config as Record<string, unknown>)._retry === true

      // Attempt silent refresh for user (non-admin) requests on first 1002
      if (data.code === 1002 && !isAdmin && !isRetry) {
        ;(res.config as Record<string, unknown>)._retry = true

        if (_isRefreshing) {
          // Another refresh is already in flight — queue this retry
          return new Promise((resolve, reject) => {
            _pendingQueue.push((token) => {
              if (token) {
                res.config.headers = { ...res.config.headers, Authorization: `Bearer ${token}` }
                resolve(api(res.config))
              } else {
                reject(data)
              }
            })
          })
        }

        _isRefreshing = true
        const newToken = await _tryRefresh()
        _isRefreshing = false

        if (newToken) {
          _notifyPending(newToken)
          res.config.headers = { ...res.config.headers, Authorization: `Bearer ${newToken}` }
          return api(res.config)
        } else {
          _notifyPending(null)
          _handleSessionExpired()
          return Promise.reject(data)
        }
      }

      // All other errors (including admin 1002 and retry failures)
      ElMessage.error(data.message || '请求失败')
      if (data.code === 1002) {
        localStorage.removeItem('token')
        localStorage.removeItem('admin_token')
        const path = window.location.pathname
        window.location.href = path.startsWith('/admin') ? '/admin/login' : '/login'
      }
      return Promise.reject(data)
    }
    return data
  },
  (err) => {
    ElMessage.error('网络异常，请稍后重试')
    return Promise.reject(err)
  },
)

export default api
