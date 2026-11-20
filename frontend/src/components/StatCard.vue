<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  hint: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'navy' }, // navy | teal | amber | red
})

const tones = {
  navy: 'bg-navy-50 text-navy',
  teal: 'bg-teal-50 text-teal-700',
  amber: 'bg-amber-50 text-amber-700',
  red: 'bg-red-50 text-red-700',
}
</script>

<template>
  <div class="card flex items-start gap-3 p-4">
    <div v-if="icon" class="rounded-md p-2" :class="tones[tone]">
      <component :is="icon" class="h-5 w-5" aria-hidden="true" />
    </div>
    <div class="min-w-0">
      <p class="text-xs font-medium uppercase tracking-wide text-slate-500">{{ label }}</p>
      <p class="mt-1 truncate text-2xl font-semibold text-navy">{{ value }}</p>
      <p v-if="hint" class="mt-0.5 text-xs text-slate-500">{{ hint }}</p>
    </div>
  </div>
</template>
