import axios from 'axios'

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
let csrfToken = localStorage.getItem('csrf_token') || null

export async function refreshCsrfToken() {
  const response = await fetch(`${backendUrl}/api/csrf-token`, {
    method: 'GET',
    credentials: 'include',
  })
  if (!response.ok) throw new Error('Unable to initialize secure session')
  const data = await response.json()
  csrfToken = data.csrf_token
  localStorage.setItem('csrf_token', csrfToken)
  return csrfToken
}

export async function secureFetch(input, init = {}) {
  const options = { ...init, credentials: 'include' }
  const method = (options.method || 'GET').toUpperCase()

  if (!csrfToken && method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    await refreshCsrfToken()
  }

  const headers = new Headers(options.headers || {})
  if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    headers.set('X-CSRF-Token', csrfToken)
  }
  options.headers = headers

  let response = await fetch(input, options)
  if (response.status === 403 && method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    await refreshCsrfToken()
    headers.set('X-CSRF-Token', csrfToken)
    response = await fetch(input, options)
  }
  return response
}

axios.defaults.withCredentials = true

axios.interceptors.request.use(async (config) => {
  const method = (config.method || 'get').toUpperCase()
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    if (!csrfToken) await refreshCsrfToken()
    config.headers = config.headers || {}
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})

export default axios
