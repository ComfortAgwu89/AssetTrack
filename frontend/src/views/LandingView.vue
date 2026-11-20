<script setup>
import { ShieldCheck, Box, ArrowLeftRight, TrendingDown, History, FileText, Wrench } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const features = [
  { icon: Box, title: 'One asset register', text: 'Every asset with a unique number, location, custodian and condition.' },
  { icon: ArrowLeftRight, title: 'Accountable transfers', text: 'Moves between departments or custodians need approval and leave a trail.' },
  { icon: TrendingDown, title: 'Transparent depreciation', text: 'Straight-line and reducing-balance calculations you can trace and verify.' },
  { icon: Wrench, title: 'Maintenance and verification', text: 'Track repairs, flag missing assets and confirm what physically exists.' },
  { icon: History, title: 'Tamper-resistant audit trail', text: 'See who changed what and when. Ordinary users cannot edit history.' },
  { icon: FileText, title: 'Reports that reconcile', text: 'Reports are built from the same records as the register.' },
]
</script>

<template>
  <div class="min-h-screen bg-white">
    <header class="border-b border-slate-200">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <div class="flex items-center gap-2 text-navy">
          <ShieldCheck class="h-6 w-6 text-teal" aria-hidden="true" />
          <span class="text-lg font-semibold tracking-tight">AssetTrack</span>
        </div>
        <nav class="flex items-center gap-2">
          <router-link v-if="auth.isAuthenticated" :to="{ name: 'dashboard' }" class="btn-primary">Open dashboard</router-link>
          <template v-else>
            <router-link to="/login" class="btn-secondary">Sign in</router-link>
            <router-link to="/register" class="btn-primary">Get started</router-link>
          </template>
        </nav>
      </div>
    </header>

    <section class="bg-navy text-white">
      <div class="mx-auto max-w-6xl px-4 py-16 sm:py-24">
        <p class="text-sm font-medium uppercase tracking-wide text-teal-100">Fixed Asset Management and Accountability System</p>
        <h1 class="mt-3 max-w-2xl text-3xl font-semibold leading-tight sm:text-4xl">Know what you own, where it is, and who is responsible for it.</h1>
        <p class="mt-4 max-w-2xl text-slate-300">
          AssetTrack helps universities, hospitals, NGOs and businesses manage the full lifecycle of their physical assets, from acquisition to disposal.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <router-link to="/register" class="btn-accent">Create your organisation</router-link>
          <router-link to="/login" class="btn border border-slate-500 text-white hover:bg-navy-700">Sign in</router-link>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-6xl px-4 py-14">
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="f in features" :key="f.title" class="card p-5">
          <component :is="f.icon" class="h-6 w-6 text-teal" aria-hidden="true" />
          <h2 class="mt-3 font-semibold text-navy">{{ f.title }}</h2>
          <p class="mt-1 text-sm text-slate-600">{{ f.text }}</p>
        </div>
      </div>
    </section>

    <footer class="border-t border-slate-200 py-6 text-center text-xs text-slate-500">
      Depreciation figures and reports are management information, not audited financial statements.
    </footer>
  </div>
</template>
