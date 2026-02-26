<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAlertsStore } from '../stores/alerts'
import StatusBadge from '../components/shared/StatusBadge.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const store = useAlertsStore()

onMounted(() => {
  store.fetchRules(projectId)
  store.fetchEvents(projectId)
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Alerts</h1>
      <button @click="store.evaluate(projectId)" class="btn-primary">Evaluate Rules</button>
    </div>

    <!-- Rules -->
    <div class="card mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Alert Rules ({{ store.rules.length }})</h3>
      <div class="space-y-2">
        <div v-for="rule in store.rules" :key="rule.id" class="flex items-center justify-between p-3 rounded-lg bg-gray-50">
          <div>
            <span class="text-sm font-medium text-gray-800">{{ rule.alert_type.replace(/_/g, ' ') }}</span>
            <StatusBadge :status="rule.severity" class="ml-2" />
          </div>
          <span class="badge" :class="rule.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
            {{ rule.is_active ? 'Active' : 'Disabled' }}
          </span>
        </div>
        <p v-if="!store.rules.length" class="text-sm text-gray-400">No alert rules configured.</p>
      </div>
    </div>

    <!-- Events -->
    <div class="card">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Alert Events</h3>
      <LoadingSpinner v-if="store.loading" />
      <div v-else class="space-y-3">
        <div
          v-for="event in store.events"
          :key="event.id"
          class="flex items-start justify-between p-4 rounded-lg"
          :class="event.acknowledged ? 'bg-gray-50' : 'bg-red-50 border border-red-200'"
        >
          <div>
            <div class="flex items-center gap-2">
              <p class="text-sm font-medium" :class="event.acknowledged ? 'text-gray-600' : 'text-gray-800'">{{ event.title }}</p>
              <StatusBadge :status="event.severity" />
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ event.message }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ new Date(event.triggered_at).toLocaleString() }}</p>
          </div>
          <button
            v-if="!event.acknowledged"
            @click="store.acknowledge(event.id)"
            class="btn-sm btn-secondary shrink-0"
          >Acknowledge</button>
          <span v-else class="text-xs text-gray-400 shrink-0">Acknowledged</span>
        </div>
        <p v-if="!store.events.length" class="text-sm text-gray-400 text-center py-4">No alert events.</p>
      </div>
    </div>
  </div>
</template>
