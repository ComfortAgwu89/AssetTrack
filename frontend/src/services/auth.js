import api from './api'

export const authService = {
  login: (payload) => api.post('/auth/login', payload).then((r) => r.data.user),
  register: (payload) => api.post('/auth/register', payload).then((r) => r.data.user),
  me: () => api.get('/auth/me').then((r) => r.data.user),
  logout: () => api.post('/auth/logout'),
}
