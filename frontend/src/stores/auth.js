import { defineStore } from 'pinia'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, ready: false }),
  getters: {
    isAuthenticated: (s) => !!s.user,
    organisation: (s) => s.user?.organisation ?? null,
  },
  actions: {
    /** Restore the session from the cookie once per page load. */
    async init() {
      if (this.ready) return
      try {
        this.user = await authService.me()
      } catch {
        this.user = null
      }
      this.ready = true
    },
    async login(payload) {
      this.user = await authService.login(payload)
      this.ready = true
    },
    async register(payload) {
      this.user = await authService.register(payload)
      this.ready = true
    },
    async logout() {
      try {
        await authService.logout()
      } finally {
        this.clear()
      }
    },
    clear() {
      this.user = null
      this.ready = true
    },
    can(permission) {
      return !permission || !!this.user?.permissions.includes(permission)
    },
  },
})
