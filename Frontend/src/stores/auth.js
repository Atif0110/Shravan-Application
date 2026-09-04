import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { secureFetch, refreshCsrfToken } from '@/api'

export const auth = defineStore('auth', () => {
  const backend_url = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
  const token = ref(null)
  const user_details = ref(sessionStorage.getItem('user_details'))

  const parsedUser = computed(() => {
    try {
      return user_details.value ? JSON.parse(user_details.value) : null
    } catch {
      return null
    }
  })

  const username = computed(() => parsedUser.value?.username || '')
  const email = computed(() => parsedUser.value?.email || '')
  const role = computed(() => parsedUser.value?.role || null)
  const isAuthenticated = computed(() => user_details.value !== null)

  function updateUser() {
    user_details.value = sessionStorage.getItem('user_details')
  }

  function removeUserDetails() {
    sessionStorage.removeItem('user_details')
    localStorage.removeItem('userName')
    user_details.value = null
  }

  async function login(credentials) {
    try {
      await refreshCsrfToken()
      const response = await secureFetch(`${backend_url}/api/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      })
      const data = await response.json()
      if (!response.ok) return { status: false, message: data.error || 'Login failed' }

      const details = {
        user_id: data.user.user_id,
        username: data.user.user_name,
        role: data.user.role,
        email: data.user.email,
      }
      sessionStorage.setItem('user_details', JSON.stringify(details))
      localStorage.setItem('userName', data.user.user_name)
      updateUser()
      return { status: true, message: data.message, username: data.user.user_name, role: data.user.role }
    } catch {
      return { status: false, message: 'Unable to connect to the server' }
    }
  }

  async function register(details) {
    try {
      await refreshCsrfToken()
      const response = await secureFetch(`${backend_url}/api/create_user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(details),
      })
      const data = await response.json()
      return response.ok
        ? { status: true, message: data.message }
        : { status: false, message: data.error || 'Registration failed' }
    } catch {
      return { status: false, message: 'Unable to connect to the server' }
    }
  }

  async function logout() {
    try {
      const response = await secureFetch(`${backend_url}/api/users/logout`, { method: 'POST' })
      const data = await response.json()
      removeUserDetails()
      return response.ok
        ? { status: true, message: data.message }
        : { status: false, message: data.error || 'Logout failed' }
    } catch {
      removeUserDetails()
      return { status: false, message: 'Unable to connect to the server' }
    }
  }

  return { login, logout, register, token, username, isAuthenticated, backend_url, role, email, updateUser, user_details }
})
