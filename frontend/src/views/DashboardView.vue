<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Box, Banknote, Landmark, CheckCircle2, Wrench, AlertTriangle, SearchX, Hourglass, Loader2, RefreshCw } from 'lucide-vue-next'
import StatCard from '@/components/StatCard.vue'
import ChartCard from '@/components/ChartCard.vue'
import { dashboardService } from '@/services/dashboard'
import { parseError } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useFormat } from '@/composables/useFormat'

const auth = useAuthStore()
const fmt = useFormat(auth.organisation?.currency_symbol || '₦')

const data = ref(null)
const loading = ref(true)
const error = ref('')
const filters = reactive({ department_id: '', category_id: '' })

const palette = ['#0B1F3A', '#0E8F8B', '#4A6FA5', '#7FB7B5', '#8A9BB5', '#1B3A6B', '#5AA9A6', '#B8C4D6', '#2E4A7A']
const statusColours = {
  in_use: '#0E8F8B', in_storage: '#8A9BB5', under_maintenance: '#D9A441', missing: '#C0392B', disposed: '#B8C4D6',
}
const titleCase = (s) => s.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.department_id) params.department_id = filters.department_id
    if (filters.category_id) params.category_id = filters.category_id
    data.value = await dashboardService.get(params)
  } catch (e) {
    error.value = parseError(e).message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => [filters.department_id, filters.category_id], load)

const k = computed(() => data.value?.kpis)
const cards = computed(() =>
  k.value
    ? [
        { label: 'Registered assets', value: fmt.count(k.value.total_assets), icon: Box, tone: 'navy' },
        { label: 'Acquisition cost', value: fmt.moneyCompact(k.value.total_acquisition_cost), hint: fmt.money(k.value.total_acquisition_cost), icon: Banknote, tone: 'navy' },
        { label: 'Net book value', value: fmt.moneyCompact(k.value.net_book_value), hint: `Accumulated depreciation ${fmt.moneyCompact(k.value.accumulated_depreciation)}`, icon: Landmark, tone: 'teal' },
        { label: 'In use', value: fmt.count(k.value.assets_in_use), icon: CheckCircle2, tone: 'teal' },
        { label: 'Under maintenance', value: fmt.count(k.value.under_maintenance), icon: Wrench, tone: 'amber' },
        { label: 'Damaged', value: fmt.count(k.value.damaged), icon: AlertTriangle, tone: 'red' },
        { label: 'Missing', value: fmt.count(k.value.missing), icon: SearchX, tone: 'red' },
        { label: 'Fully depreciated', value: fmt.count(k.value.fully_depreciated), icon: Hourglass, tone: 'amber' },
      ]
    : [],
)

const byDepartment = computed(() => ({
  labels: data.value?.by_department.map((r) => r.label) ?? [],
  datasets: [{ label: 'Assets', data: data.value?.by_department.map((r) => r.value) ?? [], backgroundColor: '#0B1F3A', borderRadius: 4 }],
}))
const byCategory = computed(() => ({
  labels: data.value?.by_category.map((r) => r.label) ?? [],
  datasets: [{ data: data.value?.by_category.map((r) => r.value) ?? [], backgroundColor: palette }],
}))
const byStatus = computed(() => ({
  labels: data.value?.by_status.map((r) => titleCase(r.label)) ?? [],
  datasets: [{ data: data.value?.by_status.map((r) => r.value) ?? [], backgroundColor: data.value?.by_status.map((r) => statusColours[r.label] || '#8A9BB5') ?? [] }],
}))
const depreciation = computed(() => ({
  labels: data.value?.depreciation_by_category.map((r) => r.category) ?? [],
  datasets: [
    { label: 'Acquisition cost', data: data.value?.depreciation_by_category.map((r) => r.cost) ?? [], backgroundColor: '#8A9BB5', borderRadius: 4 },
    { label: 'Net book value', data: data.value?.depreciation_by_category.map((r) => r.nbv) ?? [], backgroundColor: '#0E8F8B', borderRadius: 4 },
  ],
}))

const moneyAxis = { scales: { y: { ticks: { callback: (v) => fmt.moneyCompact(v) } } }, plugins: { tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmt.money(c.parsed.y)}` } } } }
const horizontal = { indexAxis: 'y', scales: { x: { ticks: { precision: 0 } } } }
</script>

<template>
  <div>
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div>
        <label for="f-dept" class="label">Department</label>
        <select id="f-dept" v-model="filters.department_id" class="input min-w-[12rem]">
          <option value="">All departments</option>
          <option v-for="d in data?.filters.departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
      <div>
        <label for="f-cat" class="label">Category</label>
        <select id="f-cat" v-model="filters.category_id" class="input min-w-[12rem]">
          <option value="">All categories</option>
          <option v-for="c in data?.filters.categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <button v-if="filters.department_id || filters.category_id" class="btn-secondary" @click="filters.department_id = ''; filters.category_id = ''">
        Clear filters
      </button>
      <p v-if="data" class="ml-auto text-xs text-slate-500">Figures as at {{ data.as_of }}</p>
    </div>

    <div v-if="error" class="card flex flex-col items-center p-8 text-center" role="alert">
      <p class="text-sm text-red-700">{{ error }}</p>
      <button class="btn-secondary mt-3" @click="load"><RefreshCw class="h-4 w-4" aria-hidden="true" /> Try again</button>
    </div>

    <div v-else-if="loading && !data" class="flex items-center justify-center p-16 text-slate-500">
      <Loader2 class="mr-2 h-5 w-5 animate-spin" aria-hidden="true" /> Loading dashboard…
    </div>

    <template v-else-if="data">
      <div v-if="data.kpis.total_assets === 0" class="card mb-4 p-6 text-center text-sm text-slate-600">
        No assets match this selection yet. Registered assets will appear here once they are added.
      </div>

      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" :class="{ 'opacity-60': loading }">
        <StatCard v-for="c in cards" :key="c.label" v-bind="c" />
      </div>

      <div class="mt-4 grid gap-4 lg:grid-cols-2" :class="{ 'opacity-60': loading }">
        <ChartCard title="Assets by department" type="bar" :labels="byDepartment.labels" :datasets="byDepartment.datasets" :options="horizontal" />
        <ChartCard title="Assets by category" type="doughnut" :labels="byCategory.labels" :datasets="byCategory.datasets" />
        <ChartCard title="Depreciation summary" subtitle="Cost against net book value by category" type="bar" :labels="depreciation.labels" :datasets="depreciation.datasets" :options="moneyAxis" />
        <ChartCard title="Assets by status" type="doughnut" :labels="byStatus.labels" :datasets="byStatus.datasets" />
      </div>

      <section v-if="auth.can('dashboard.activity')" class="card mt-4 p-4">
        <h3 class="text-sm font-semibold text-navy">Recent activity</h3>
        <p v-if="!data.recent_activity.length" class="mt-3 text-sm text-slate-500">No activity recorded yet.</p>
        <ul v-else class="mt-3 divide-y divide-slate-100">
          <li v-for="a in data.recent_activity" :key="a.id" class="flex flex-wrap items-baseline justify-between gap-2 py-2 text-sm">
            <span class="text-slate-700">{{ a.summary || a.action }}</span>
            <span class="text-xs text-slate-500">{{ a.user }} · {{ fmt.dateTime(a.created_at) }}</span>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
