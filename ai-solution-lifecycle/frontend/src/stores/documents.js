import { defineStore } from 'pinia'
import { ref } from 'vue'
import docsApi from '../api/documents'

export const useDocumentsStore = defineStore('documents', () => {
  const documents = ref([])
  const current = ref(null)
  const loading = ref(false)
  const generating = ref(false)

  async function fetchAll(projectId) {
    loading.value = true
    try {
      const { data } = await docsApi.list(projectId)
      documents.value = data
    } finally { loading.value = false }
  }

  async function generate(projectId, payload) {
    generating.value = true
    try {
      const { data } = await docsApi.generate(projectId, payload)
      documents.value.unshift(data)
      return data
    } finally { generating.value = false }
  }

  async function update(docId, payload) {
    const { data } = await docsApi.update(docId, payload)
    const idx = documents.value.findIndex(d => d.id === docId)
    if (idx >= 0) documents.value[idx] = data
    return data
  }

  return { documents, current, loading, generating, fetchAll, generate, update }
})
