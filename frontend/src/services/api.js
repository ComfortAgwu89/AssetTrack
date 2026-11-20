import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  withCredentials: true, // send the httpOnly auth cookie
})

function readCookie(name) {
  const match = document.cookie.split('; ').find((row) => row.startsWith(name + '='))
  return match ? decodeURIComponent(match.split('=')[1]) : null
}

// Double-submit CSRF: echo the readable CSRF cookie in a header on state-changing requests.
api.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()
  if (!['get', 'head', 'options'].includes(method)) {
    const token = readCookie('csrf_access_token')
    if (token) config.headers['X-CSRF-TOKEN'] = token
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || ''
    if (error.response?.status === 401 && !url.includes('/auth/')) {
      window.dispatchEvent(new Event('auth:expired'))
    }
    return Promise.reject(error)
  },
)

/** Turn an axios error into { message, fields } for display. */
export function parseError(error) {
  const body = error.response?.data?.error
  if (body) return { message: body.message, fields: typeof body.details === 'object' ? body.details : {} }
  if (error.request) return { message: 'Cannot reach the server. Check that the API is running.', fields: {} }
  return { message: 'Something went wrong. Please try again.', fields: {} }
}

export default api
