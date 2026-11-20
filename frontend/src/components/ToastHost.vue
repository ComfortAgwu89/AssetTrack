<script setup>
import { CheckCircle2, AlertCircle, X } from 'lucide-vue-next'
import { useToastStore } from '@/stores/notifications'

const toasts = useToastStore()
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-50 flex w-full max-w-sm flex-col gap-2" aria-live="polite">
    <div
      v-for="t in toasts.items"
      :key="t.id"
      role="status"
      class="pointer-events-auto flex items-start gap-3 rounded-lg border bg-white p-3 shadow-lg"
      :class="t.type === 'error' ? 'border-red-200' : 'border-teal-100'"
    >
      <AlertCircle v-if="t.type === 'error'" class="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
      <CheckCircle2 v-else class="mt-0.5 h-5 w-5 shrink-0 text-teal" />
      <p class="flex-1 text-sm text-slate-700">{{ t.message }}</p>
      <button class="text-slate-400 hover:text-slate-600" aria-label="Dismiss" @click="toasts.dismiss(t.id)">
        <X class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
