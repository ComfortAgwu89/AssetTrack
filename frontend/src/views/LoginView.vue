<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShieldCheck, Loader2 } from 'lucide-vue-next'
import FormField from '@/components/FormField.vue'
import { useAuthStore } from '@/stores/auth'
import { parseError } from '@/services/api'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const formError = ref(route.query.expired ? 'Your session has expired. Please sign in again.' : '')
const loading = ref(false)

// Development convenience only: fills the form with a seeded demo account.
const demoAccounts = import.meta.env.DEV
  ? [
      ['Organisation Admin', 'admin@harbourview.example'],
      ['Accountant', 'accountant@harbourview.example'],
      ['Asset Manager', 'manager@harbourview.example'],
      ['Department Head', 'depthead@harbourview.example'],
      ['Custodian', 'custodian@harbourview.example'],
      ['Super Admin', 'superadmin@harbourview.example'],
    ]
  : []

function validate() {
  errors.email = !form.email.trim()
    ? 'Enter your email address.'
    : /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email) ? '' : 'Enter a valid email address.'
  errors.password = form.password ? '' : 'Enter your password.'
  return !errors.email && !errors.password
}

async function submit() {
  formError.value = ''
  if (!validate()) return
  loading.value = true
  try {
    await auth.login({ email: form.email.trim(), password: form.password })
    router.push(route.query.redirect || { name: 'dashboard' })
  } catch (e) {
    formError.value = parseError(e).message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-surface px-4 py-10">
    <div class="w-full max-w-md">
      <router-link to="/" class="mb-6 flex items-center justify-center gap-2 text-navy">
        <ShieldCheck class="h-7 w-7 text-teal" aria-hidden="true" />
        <span class="text-2xl font-semibold tracking-tight">AssetTrack</span>
      </router-link>
      <div class="card p-6">
        <h1 class="text-lg font-semibold text-navy">Sign in</h1>
        <p class="mb-5 text-sm text-slate-500">Access your organisation's asset records.</p>

        <p v-if="formError" class="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{{ formError }}</p>

        <form class="space-y-4" novalidate @submit.prevent="submit">
          <FormField v-model="form.email" label="Email" type="email" autocomplete="username" :error="errors.email" />
          <FormField v-model="form.password" label="Password" type="password" autocomplete="current-password" :error="errors.password" />
          <button type="submit" class="btn-primary w-full" :disabled="loading">
            <Loader2 v-if="loading" class="h-4 w-4 animate-spin" aria-hidden="true" />
            {{ loading ? 'Signing in…' : 'Sign in' }}
          </button>
        </form>

        <p class="mt-5 text-center text-sm text-slate-600">
          New organisation?
          <router-link to="/register" class="font-medium text-teal-700 hover:underline">Create an account</router-link>
        </p>
      </div>

      <div v-if="demoAccounts.length" class="card mt-4 p-4">
        <p class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Demo accounts (development only)</p>
        <div class="flex flex-wrap gap-2">
          <button v-for="[label, email] in demoAccounts" :key="email" type="button" class="btn-secondary !px-2.5 !py-1 text-xs" @click="form.email = email">
            {{ label }}
          </button>
        </div>
        <p class="mt-2 text-xs text-slate-500">Click a role to fill the email, then enter the demo password from the README.</p>
      </div>
    </div>
  </div>
</template>
