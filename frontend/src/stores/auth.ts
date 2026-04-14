import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import api from '@/utils/api'
import type { UserInfo, LoginResult } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const storedUser = localStorage.getItem('user')
  let initialUser: UserInfo | null = null
  if (storedUser) {
    try {
      initialUser = JSON.parse(storedUser) as UserInfo
    } catch {
      localStorage.removeItem('user')
    }
  }
  const user = ref<UserInfo | null>(initialUser)

  watch(user, (value) => {
    if (value) {
      localStorage.setItem('user', JSON.stringify(value))
      return
    }
    localStorage.removeItem('user')
  }, { deep: true })

  async function login(account: string, password: string) {
    const res = await api.post('/auth/login', { account, password })
    const data = res.data as LoginResult
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  }

  async function sendCode(target: string, type: 'phone' | 'email' = 'phone') {
    const res = await api.post('/auth/send-code', { target, type })
    return res.data
  }

  async function register(params: { phone?: string; email?: string; password: string; nickname?: string; invite_code?: string; verify_code?: string }) {
    const res = await api.post('/auth/register', params)
    return res.data
  }

  async function fetchProfile() {
    const res = await api.get('/auth/profile')
    user.value = res.data as UserInfo
    return user.value
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const isLoggedIn = () => !!token.value

  return { token, user, login, sendCode, register, fetchProfile, logout, isLoggedIn }
})
