<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, Loader2 } from 'lucide-vue-next'
import FormField from '@/components/FormField.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/notifications'
import { parseError } from '@/services/api'

const auth = useAuthStore()
const toasts = useToastStore()
const router = useRouter()

const form = reactive({ organisation_name: '', full_name: '', email: '', password: '', confirm: '' })
const errors = reactive({ organisation_name: '', full_name: '', email: '', password: '', confirm: '' })
const formError = ref('')
const loading = ref(false)

function validate() {
  errors.organisation_name = form.organisation_name.trim().length >= 2 ? '' : "Enter your organisation's name."
  errors.full_name = form.full_name.trim().length >= 2 ? '' : 'Enter your full name.'
  errors.email = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email) ? '' : 'Enter a valid email address.'
  errors.password =
    form.password.length >= 8 && /[A-Za-z]/.test(form.password) && /\d/.test(form.password)
      ? '' : 'Use at least 8 characters, with letters and numbers.'
  errors.confirm = form.confirm === form.password ? '' : 'Passwords do not match.'
  return Object.values(errors).every((e) => !e)
}

async function submit() {
  formError.value = ''
  if (!validate()) return
  loading.value = true
  try {
    await auth.register({
      organisation_name: form.organisation_name.trim(),
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      password: form.password,
    })
    toasts.success('Organisation created. Welcome to AssetTrack.')
    router.push({ name: 'dashboard' })
  } catch (e) {
    const { message, fields } = parseError(e)
    Object.keys(fields).forEach((k) => { if (k in errors) errors[k] = fields[k] })
    formError.value = message
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
        <h1 class="text-lg font-semibold text-navy">Create your organisation</h1>
        <p class="mb-5 text-sm text-slate-500">You will be the Organisation Administrator and can add other users later.</p>

        <p v-if="formError" class="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{{ formError }}</p>

        <form class="space-y-4" novalidate @submit.prevent="submit">
          <FormField v-model="form.organisation_name" label="Organisation name" :error="errors.organisation_name" />
          <FormField v-model="form.full_name" label="Your full name" autocomplete="name" :error="errors.full_name" />
          <FormField v-model="form.email" label="Work email" type="email" autocomplete="email" :error="errors.email" />
          <FormField v-model="form.password" label="Password" type="password" autocomplete="new-password" :error="errors.password" />
          <FormField v-model="form.confirm" label="Confirm password" type="password" autocomplete="new-password" :error="errors.confirm" />
          <button type="submit" class="btn-primary w-full" :disabled="loading">
            <Loader2 v-if="loading" class="h-4 w-4 animate-spin" aria-hidden="true" />
            {{ loading ? 'Creating…' : 'Create account' }}
          </button>
        </form>

        <p class="mt-5 text-center text-sm text-slate-600">
          Already registered?
          <router-link to="/login" class="font-medium text-teal-700 hover:underline">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
