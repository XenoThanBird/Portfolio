<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const pageTitle = computed(() => {
  const name = route.name || ''
  const titles = {
    Dashboard: 'Dashboard',
    Projects: 'Projects',
    ProjectDetail: 'Project Overview',
    Documents: 'Documents',
    Prompts: 'Prompt Library',
    Playground: 'Prompt Playground',
    Milestones: 'Milestones',
    RACI: 'RACI Matrix',
    SLA: 'SLA Tracking',
    Alerts: 'Alerts',
    Risks: 'Risk Register',
    ModelCatalog: 'AI Model Catalog',
    Value: 'Value Assessment',
  }
  return titles[name] || name
})

const userEmail = computed(() => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return ''
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || ''
  } catch {
    return ''
  }
})
</script>

<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
    <h2 class="text-lg font-semibold text-gray-800">{{ pageTitle }}</h2>
    <div class="flex items-center gap-4">
      <span class="text-sm text-gray-500">{{ userEmail }}</span>
      <div class="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-medium">
        {{ userEmail.charAt(0).toUpperCase() }}
      </div>
    </div>
  </header>
</template>
