import { defineStore } from 'pinia'
import { ref } from 'vue'
import dashboardApi from '../api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const global = ref(null)
  const projectDash = ref(null)
  const loading = ref(false)

  async function fetchGlobal() {
    loading.value = true
    try {
      const { data } = await dashboardApi.global()
      global.value = data
    } finally { loading.value = false }
  }

  async function fetchProject(projectId) {
    loading.value = true
    try {
      const { data } = await dashboardApi.project(projectId)
      projectDash.value = data
    } finally { loading.value = false }
  }

  return { global, projectDash, loading, fetchGlobal, fetchProject }
})
