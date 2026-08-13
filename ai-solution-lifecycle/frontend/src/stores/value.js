import { defineStore } from 'pinia'
import { ref } from 'vue'
import valueApi from '../api/value'

export const useValueStore = defineStore('value', () => {
  const assessment = ref(null)
  const roi = ref(null)
  const roadmap = ref(null)
  const loading = ref(false)

  async function fetchAssessment(projectId) {
    loading.value = true
    try {
      const { data } = await valueApi.get(projectId)
      assessment.value = data
    } catch (e) {
      if (e.response?.status === 404) assessment.value = null
      else throw e
    } finally { loading.value = false }
  }

  async function saveAssessment(projectId, payload) {
    const { data } = await valueApi.createOrUpdate(projectId, payload)
    assessment.value = data
    return data
  }

  async function calculateRoi(projectId, payload) {
    const { data } = await valueApi.calculateRoi(projectId, payload)
    roi.value = data
    return data
  }

  async function fetchRoadmap(projectId) {
    const { data } = await valueApi.getRoadmap(projectId)
    roadmap.value = data
    return data
  }

  return { assessment, roi, roadmap, loading, fetchAssessment, saveAssessment, calculateRoi, fetchRoadmap }
})
