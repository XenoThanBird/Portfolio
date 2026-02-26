import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import milestonesApi from '../api/milestones'

export const useMilestonesStore = defineStore('milestones', () => {
  const raw = ref({ backlog: [], in_progress: [], review: [], done: [] })
  const loading = ref(false)

  const allMilestones = computed(() =>
    [...raw.value.backlog, ...raw.value.in_progress, ...raw.value.review, ...raw.value.done]
  )

  async function fetchAll(projectId) {
    loading.value = true
    try {
      const { data } = await milestonesApi.list(projectId)
      raw.value = data
    } finally { loading.value = false }
  }

  async function create(projectId, payload) {
    const { data } = await milestonesApi.create(projectId, payload)
    const status = data.status || 'backlog'
    if (raw.value[status]) raw.value[status].push(data)
    return data
  }

  async function update(milestoneId, payload) {
    const { data } = await milestonesApi.update(milestoneId, payload)
    // Remove from old column and add to new
    for (const col of Object.keys(raw.value)) {
      raw.value[col] = raw.value[col].filter(m => m.id !== milestoneId)
    }
    const status = data.status || 'backlog'
    if (raw.value[status]) raw.value[status].push(data)
    return data
  }

  async function remove(milestoneId) {
    await milestonesApi.delete(milestoneId)
    for (const col of Object.keys(raw.value)) {
      raw.value[col] = raw.value[col].filter(m => m.id !== milestoneId)
    }
  }

  return { raw, loading, allMilestones, fetchAll, create, update, remove }
})
