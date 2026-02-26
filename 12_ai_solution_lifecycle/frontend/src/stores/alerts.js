import { defineStore } from 'pinia'
import { ref } from 'vue'
import alertsApi from '../api/alerts'

export const useAlertsStore = defineStore('alerts', () => {
  const rules = ref([])
  const events = ref([])
  const unacknowledged = ref([])
  const loading = ref(false)

  async function fetchRules(projectId) {
    const { data } = await alertsApi.listRules(projectId)
    rules.value = data
  }

  async function fetchEvents(projectId) {
    loading.value = true
    try {
      const { data } = await alertsApi.listEvents(projectId)
      events.value = data
    } finally { loading.value = false }
  }

  async function fetchUnacknowledged() {
    const { data } = await alertsApi.unacknowledged()
    unacknowledged.value = data
  }

  async function acknowledge(eventId) {
    await alertsApi.acknowledge(eventId)
    events.value = events.value.map(e => e.id === eventId ? { ...e, acknowledged: true } : e)
    unacknowledged.value = unacknowledged.value.filter(e => e.id !== eventId)
  }

  async function evaluate(projectId) {
    const { data } = await alertsApi.evaluate(projectId)
    if (data.events_created > 0) await fetchEvents(projectId)
    return data
  }

  return { rules, events, unacknowledged, loading, fetchRules, fetchEvents, fetchUnacknowledged, acknowledge, evaluate }
})
