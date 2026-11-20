<script setup>
import { Hammer } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="card flex flex-col items-center p-10 text-center">
    <div class="rounded-full bg-slate-100 p-3"><Hammer class="h-6 w-6 text-slate-500" aria-hidden="true" /></div>
    <h2 class="mt-4 text-base font-semibold text-navy">{{ route.meta.title }} is not built yet</h2>
    <p class="mt-1 max-w-md text-sm text-slate-600">{{ route.meta.blurb }}</p>
    <p class="mt-3 text-xs font-medium uppercase tracking-wide text-slate-500">Planned for Stage {{ route.meta.stage }}</p>
  </div>
</template>
