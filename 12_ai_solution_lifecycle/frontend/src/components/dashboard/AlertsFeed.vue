<script setup>
import { onMounted } from 'vue'
import { useAlertsStore } from '../../stores/alerts'
import StatusBadge from '../shared/StatusBadge.vue'

const store = useAlertsStore()

onMounted(() => store.fetchUnacknowledged())
</script>

<template>
  <div class="card">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">Unacknowledged Alerts</h3>
    <div v-if="!store.unacknowledged.length" class="text-sm text-gray-400">All clear.</div>
    <div v-else class="space-y-3 max-h-64 overflow-y-auto">
      <div v-for="a in store.unacknowledged" :key="a.id" class="flex items-start justify-between gap-3 p-3 rounded-lg bg-gray-50">
        <div>
          <p class="text-sm font-medium text-gray-800">{{ a.title }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ new Date(a.triggered_at).toLocaleString() }}</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <StatusBadge :status="a.severity" />
          <button @click="store.acknowledge(a.id)" class="btn-sm btn-secondary">Ack</button>
        </div>
      </div>
    </div>
  </div>
</template>
