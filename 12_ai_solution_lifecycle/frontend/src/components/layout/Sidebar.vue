<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => route.params.id)
const isProjectContext = computed(() => !!projectId.value)

const mainNav = [
  { label: 'Dashboard', icon: '⊞', to: '/' },
  { label: 'Projects', icon: '◫', to: '/projects' },
  { label: 'Model Catalog', icon: '⚙', to: '/models' },
]

const projectNav = computed(() => {
  const id = projectId.value
  if (!id) return []
  return [
    { label: 'Overview', icon: '◉', to: `/projects/${id}` },
    { label: 'Documents', icon: '▤', to: `/projects/${id}/documents` },
    { label: 'Prompts', icon: '⟐', to: `/projects/${id}/prompts` },
    { label: 'Playground', icon: '▶', to: `/projects/${id}/playground` },
    { label: 'Milestones', icon: '◧', to: `/projects/${id}/milestones` },
    { label: 'RACI', icon: '⊡', to: `/projects/${id}/raci` },
    { label: 'SLA', icon: '◈', to: `/projects/${id}/sla` },
    { label: 'Alerts', icon: '△', to: `/projects/${id}/alerts` },
    { label: 'Risks', icon: '⚠', to: `/projects/${id}/risks` },
    { label: 'Value', icon: '◆', to: `/projects/${id}/value` },
  ]
})

function isActive(to) {
  return route.path === to
}

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<template>
  <aside class="fixed left-0 top-0 bottom-0 w-64 bg-gray-900 text-gray-300 flex flex-col z-30">
    <div class="px-5 py-5 border-b border-gray-700">
      <h1 class="text-lg font-bold text-white tracking-tight">AI Lifecycle</h1>
      <p class="text-xs text-gray-500 mt-0.5">Solution Platform</p>
    </div>

    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      <RouterLink
        v-for="item in mainNav"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
        :class="isActive(item.to) ? 'bg-primary-600 text-white' : 'hover:bg-gray-800 hover:text-white'"
      >
        <span class="text-base">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>

      <template v-if="isProjectContext">
        <div class="pt-4 pb-2 px-3">
          <p class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Project</p>
        </div>
        <RouterLink
          v-for="item in projectNav"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
          :class="isActive(item.to) ? 'bg-primary-600 text-white' : 'hover:bg-gray-800 hover:text-white'"
        >
          <span class="text-base">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </template>
    </nav>

    <div class="px-3 py-4 border-t border-gray-700">
      <button @click="logout" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm w-full hover:bg-gray-800 hover:text-white transition-colors">
        <span class="text-base">⏻</span>
        Sign Out
      </button>
    </div>
  </aside>
</template>
