import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { navItems } from '@/navigation'

const moduleRoutes = navItems.map((item) =>
  item.name === 'dashboard'
    ? {
        path: item.path,
        name: item.name,
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: item.label, permission: item.perm },
      }
    : {
        path: item.path,
        name: item.name,
        component: () => import('@/views/ModulePlaceholderView.vue'),
        meta: { title: item.label, permission: item.perm, stage: item.stage, blurb: item.blurb },
      },
)

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: () => import('@/views/LandingView.vue') },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { guestOnly: true } },
    { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { guestOnly: true } },
    {
      path: '/app',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      redirect: { name: 'dashboard' },
      children: moduleRoutes,
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (to.meta.permission && !auth.can(to.meta.permission)) {
    return { name: 'forbidden' }
  }
})

router.addRoute({ path: '/forbidden', name: 'forbidden', component: () => import('@/views/ForbiddenView.vue'), meta: { requiresAuth: true } })

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · AssetTrack` : 'AssetTrack'
})

export default router
