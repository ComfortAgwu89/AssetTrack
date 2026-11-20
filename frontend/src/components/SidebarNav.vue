<script setup>
import { computed } from 'vue'
import { X, ShieldCheck } from 'lucide-vue-next'
import { navItems } from '@/navigation'
import { useAuthStore } from '@/stores/auth'

defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const auth = useAuthStore()
const items = computed(() => navItems.filter((i) => auth.can(i.perm)))
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-30 bg-slate-900/50 lg:hidden" @click="emit('close')"></div>
  <aside
    class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-navy text-slate-200 transition-transform lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
    aria-label="Main navigation"
  >
    <div class="flex h-16 items-center justify-between px-5">
      <router-link to="/app/dashboard" class="flex items-center gap-2 text-white">
        <ShieldCheck class="h-6 w-6 text-teal" aria-hidden="true" />
        <span class="text-lg font-semibold tracking-tight">AssetTrack</span>
      </router-link>
      <button class="rounded p-1 text-slate-300 hover:bg-navy-700 lg:hidden" aria-label="Close menu" @click="emit('close')">
        <X class="h-5 w-5" />
      </button>
    </div>
    <nav class="flex-1 overflow-y-auto px-3 pb-4">
      <router-link
        v-for="item in items"
        :key="item.name"
        :to="{ name: item.name }"
        class="mb-0.5 flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-navy-700 hover:text-white"
        active-class="!bg-navy-600 !text-white"
        @click="emit('close')"
      >
        <component :is="item.icon" class="h-4 w-4 shrink-0" aria-hidden="true" />
        {{ item.label }}
      </router-link>
    </nav>
    <p class="px-5 py-3 text-[11px] leading-snug text-slate-400">Fixed Asset Management and Accountability System</p>
  </aside>
</template>
