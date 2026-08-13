import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  function parseToken(t) {
    try {
      const payload = JSON.parse(atob(t.split('.')[1]))
      return { email: payload.sub, name: payload.name, roles: payload.roles || [] }
    } catch { return null }
  }

  if (token.value) {
    user.value = parseToken(token.value)
  }

  async function login(email, password) {
    const { data } = await authApi.login(email, password)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    user.value = parseToken(data.access_token)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isAuthenticated, login, logout }
})
