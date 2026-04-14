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

api.interceptors.response.use(
  (res) => {
    const data = res.data
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      if (data.code === 1002) {
        localStorage.removeItem('token')
        localStorage.removeItem('admin_token')
        const path = window.location.pathname
        if (path.startsWith('/admin')) {
          window.location.href = '/admin/login'
        } else {
          window.location.href = '/login'
        }
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
