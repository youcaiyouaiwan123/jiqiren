import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'
import type { AdminLoginResult } from '@/types'

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const admin = ref<{ id: number; username: string; role: string } | null>(null)

  async function login(username: string, password: string) {
    const res = await api.post('/admin/login', { username, password })
    const data = res.data as AdminLoginResult
    token.value = data.access_token
    admin.value = data.admin
    localStorage.setItem('admin_token', data.access_token)
    if (data.refresh_token) {
      localStorage.setItem('admin_refresh_token', data.refresh_token)
    }
    return data
  }

  function logout() {
    token.value = ''
    admin.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_refresh_token')
  }

  const isLoggedIn = () => !!token.value

  return { token, admin, login, logout, isLoggedIn }
})
