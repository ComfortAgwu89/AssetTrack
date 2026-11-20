import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// When the API reports an expired/invalid session, return to the sign-in page.
window.addEventListener('auth:expired', () => {
  const auth = useAuthStore()
  auth.clear()
  if (router.currentRoute.value.meta.requiresAuth) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath, expired: '1' } })
  }
})

app.mount('#app')
