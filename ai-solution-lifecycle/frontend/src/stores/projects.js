import { defineStore } from 'pinia'
import { ref } from 'vue'
import projectsApi from '../api/projects'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([])
  const current = ref(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await projectsApi.list()
      projects.value = data
    } finally { loading.value = false }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await projectsApi.get(id)
      current.value = data
    } finally { loading.value = false }
  }

  async function create(payload) {
    const { data } = await projectsApi.create(payload)
    projects.value.push(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await projectsApi.update(id, payload)
    const idx = projects.value.findIndex(p => p.id === id)
    if (idx >= 0) projects.value[idx] = data
    if (current.value?.id === id) current.value = data
    return data
  }

  async function remove(id) {
    await projectsApi.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  return { projects, current, loading, fetchAll, fetchOne, create, update, remove }
})
