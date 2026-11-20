<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import TopBar from '@/components/TopBar.vue'

const sidebarOpen = ref(false)
const route = useRoute()
</script>

<template>
  <div class="min-h-screen">
    <SidebarNav :open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="lg:pl-64">
      <TopBar @toggle-menu="sidebarOpen = !sidebarOpen" />
      <main class="p-4 lg:p-6">
        <h1 class="page-title mb-4">{{ route.meta.title }}</h1>
        <router-view />
      </main>
    </div>
  </div>
</template>
