import { defineStore } from 'pinia'
import { ref } from 'vue'
import risksApi from '../api/risks'

export const useRisksStore = defineStore('risks', () => {
  const risks = ref([])
  const matrix = ref(null)
  const changeRequests = ref([])
  const loading = ref(false)

  async function fetchRisks(projectId) {
    loading.value = true
    try {
      const { data } = await risksApi.list(projectId)
      risks.value = data
    } finally { loading.value = false }
  }

  async function fetchMatrix(projectId) {
    const { data } = await risksApi.matrix(projectId)
    matrix.value = data
  }

  async function createRisk(projectId, payload) {
    const { data } = await risksApi.create(projectId, payload)
    risks.value.unshift(data)
    return data
  }

  async function updateRisk(riskId, payload) {
    const { data } = await risksApi.update(riskId, payload)
    const idx = risks.value.findIndex(r => r.id === riskId)
    if (idx >= 0) risks.value[idx] = data
    return data
  }

  async function fetchChangeRequests(projectId) {
    const { data } = await risksApi.listChangeRequests(projectId)
    changeRequests.value = data
  }

  async function createChangeRequest(projectId, payload) {
    const { data } = await risksApi.createChangeRequest(projectId, payload)
    changeRequests.value.unshift(data)
    return data
  }

  return { risks, matrix, changeRequests, loading, fetchRisks, fetchMatrix, createRisk, updateRisk, fetchChangeRequests, createChangeRequest }
})
