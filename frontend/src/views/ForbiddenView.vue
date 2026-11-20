<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-surface px-4 text-center">
    <p class="text-sm font-medium text-red-600">403</p>
    <h1 class="mt-1 text-xl font-semibold text-navy">You do not have access to this page</h1>
    <p class="mt-1 text-sm text-slate-600">Ask your Organisation Administrator if you need this permission.</p>
    <router-link :to="{ name: 'dashboard' }" class="btn-primary mt-5">Back to overview</router-link>
  </div>
</template>
