<script setup>
import { computed } from 'vue'

const props = defineProps({ value: { type: String, required: true } })

const styles = {
  in_use: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  in_storage: 'bg-slate-100 text-slate-700 ring-slate-200',
  under_maintenance: 'bg-amber-50 text-amber-800 ring-amber-200',
  missing: 'bg-red-50 text-red-700 ring-red-200',
  disposed: 'bg-slate-100 text-slate-500 ring-slate-200',
  new: 'bg-teal-50 text-teal-700 ring-teal-100',
  good: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  fair: 'bg-amber-50 text-amber-800 ring-amber-200',
  poor: 'bg-orange-50 text-orange-700 ring-orange-200',
  damaged: 'bg-red-50 text-red-700 ring-red-200',
  pending: 'bg-amber-50 text-amber-800 ring-amber-200',
  in_progress: 'bg-blue-50 text-blue-700 ring-blue-200',
  completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
}

const classes = computed(() => styles[props.value] || 'bg-slate-100 text-slate-700 ring-slate-200')
const label = computed(() => props.value.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase()))
</script>

<template>
  <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset" :class="classes">
    {{ label }}
  </span>
</template>
