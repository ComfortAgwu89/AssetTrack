import { defineStore } from 'pinia'

let nextId = 1

export const useToastStore = defineStore('toasts', {
  state: () => ({ items: [] }),
  actions: {
    push(type, message, timeout = 5000) {
      const id = nextId++
      this.items.push({ id, type, message })
      if (timeout) setTimeout(() => this.dismiss(id), timeout)
    },
    success(message) { this.push('success', message) },
    error(message) { this.push('error', message, 8000) },
    dismiss(id) { this.items = this.items.filter((t) => t.id !== id) },
  },
})
