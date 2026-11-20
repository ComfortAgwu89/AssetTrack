<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Chart } from 'chart.js/auto'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  type: { type: String, default: 'bar' },
  labels: { type: Array, default: () => [] },
  datasets: { type: Array, default: () => [] },
  options: { type: Object, default: () => ({}) },
  height: { type: Number, default: 260 },
})

const canvas = ref(null)
let chart = null

function render() {
  chart?.destroy()
  chart = null
  if (!props.labels.length || !canvas.value) return
  chart = new Chart(canvas.value, {
    type: props.type,
    data: { labels: props.labels, datasets: props.datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: props.datasets.length > 1 || props.type === 'doughnut', position: 'bottom' } },
      ...props.options,
    },
  })
}

onMounted(render)
watch(() => [props.labels, props.datasets, props.type], render, { deep: true })
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <section class="card p-4">
    <h3 class="text-sm font-semibold text-navy">{{ title }}</h3>
    <p v-if="subtitle" class="text-xs text-slate-500">{{ subtitle }}</p>
    <div class="mt-3" :style="{ height: height + 'px' }">
      <canvas v-show="labels.length" ref="canvas" :aria-label="title" role="img"></canvas>
      <div v-if="!labels.length" class="flex h-full items-center justify-center rounded-md bg-slate-50 text-sm text-slate-500">
        No data for the current selection.
      </div>
    </div>
  </section>
</template>
