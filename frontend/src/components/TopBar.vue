<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, LogOut, CalendarDays } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/notifications'

const emit = defineEmits(['toggle-menu'])
const auth = useAuthStore()
const toasts = useToastStore()
const router = useRouter()

const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
const initials = computed(() =>
  (auth.user?.full_name || '').split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase(),
)

const menuOpen = ref(false)
const menu = ref(null)
const closeOnOutside = (e) => { if (menu.value && !menu.value.contains(e.target)) menuOpen.value = false }
onMounted(() => document.addEventListener('click', closeOnOutside))
onBeforeUnmount(() => document.removeEventListener('click', closeOnOutside))

async function signOut() {
  await auth.logout()
  toasts.success('You have been signed out.')
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:px-6">
    <button class="rounded p-2 text-slate-600 hover:bg-slate-100 lg:hidden" aria-label="Open menu" @click="emit('toggle-menu')">
      <Menu class="h-5 w-5" />
    </button>
    <div class="min-w-0">
      <p class="truncate text-sm font-semibold text-navy">{{ auth.organisation?.name }}</p>
      <p class="hidden items-center gap-1 text-xs text-slate-500 sm:flex">
        <CalendarDays class="h-3.5 w-3.5" aria-hidden="true" /> {{ today }}
      </p>
    </div>

    <div ref="menu" class="relative ml-auto">
      <button
        class="flex items-center gap-2 rounded-md p-1.5 hover:bg-slate-100"
        :aria-expanded="menuOpen"
        aria-haspopup="menu"
        @click.stop="menuOpen = !menuOpen"
      >
        <span class="flex h-8 w-8 items-center justify-center rounded-full bg-navy text-xs font-semibold text-white">{{ initials }}</span>
        <span class="hidden text-left sm:block">
          <span class="block text-sm font-medium leading-tight text-slate-800">{{ auth.user?.full_name }}</span>
          <span class="block text-xs leading-tight text-slate-500">{{ auth.user?.role.name }}</span>
        </span>
      </button>
      <div v-if="menuOpen" role="menu" class="absolute right-0 mt-2 w-56 rounded-md border border-slate-200 bg-white py-1 shadow-lg">
        <p class="truncate px-3 py-2 text-xs text-slate-500">{{ auth.user?.email }}</p>
        <button role="menuitem" class="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" @click="signOut">
          <LogOut class="h-4 w-4" aria-hidden="true" /> Sign out
        </button>
      </div>
    </div>
  </header>
</template>
