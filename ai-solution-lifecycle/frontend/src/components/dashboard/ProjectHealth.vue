<script setup>
import StatusBadge from '../shared/StatusBadge.vue'

defineProps({
  projects: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="card">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">Active Projects</h3>
    <div v-if="!projects.length" class="text-sm text-gray-400">No projects yet.</div>
    <div v-else class="space-y-3">
      <RouterLink
        v-for="p in projects"
        :key="p.id"
        :to="`/projects/${p.id}`"
        class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <div>
          <p class="text-sm font-medium text-gray-800">{{ p.name }}</p>
          <p class="text-xs text-gray-500">{{ p.owner_email }}</p>
        </div>
        <StatusBadge :status="p.status" />
      </RouterLink>
    </div>
  </div>
</template>
