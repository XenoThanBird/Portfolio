<script setup>
import { onMounted, ref } from 'vue'
import modelsApi from '../api/models'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const models = ref([])
const loading = ref(false)
const showRecommend = ref(false)
const recForm = ref({ use_case_description: '', project_id: '' })
const recommendations = ref(null)
const recommending = ref(false)

async function fetchModels() {
  loading.value = true
  try {
    const { data } = await modelsApi.list()
    models.value = data
  } finally { loading.value = false }
}

async function getRecommendations() {
  recommending.value = true
  try {
    const { data } = await modelsApi.recommend(recForm.value)
    recommendations.value = data.recommendations
  } finally { recommending.value = false }
}

onMounted(fetchModels)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">AI Model Catalog</h1>
      <button @click="showRecommend = true" class="btn-primary">Get Recommendations</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="m in models" :key="m.id" class="card">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-800">{{ m.name }}</h3>
            <p class="text-xs text-gray-500">{{ m.provider }} &middot; {{ m.model_type }}</p>
          </div>
          <span v-if="m.cost_per_1k_tokens" class="badge bg-green-100 text-green-700">${{ m.cost_per_1k_tokens }}/1K</span>
        </div>
        <p class="text-sm text-gray-600 mb-3">{{ m.description }}</p>
        <div class="flex flex-wrap gap-1">
          <span v-for="cap in (m.capabilities || [])" :key="cap" class="badge bg-gray-100 text-gray-600">{{ cap }}</span>
        </div>
        <div v-if="m.max_context_length" class="mt-3 text-xs text-gray-400">
          Context: {{ (m.max_context_length / 1000).toFixed(0) }}K tokens
        </div>
      </div>
    </div>

    <Modal :show="showRecommend" title="AI Model Recommendation" max-width="max-w-2xl" @close="showRecommend = false; recommendations = null">
      <div class="space-y-4">
        <div>
          <label class="label">Describe Your Use Case</label>
          <textarea v-model="recForm.use_case_description" class="input" rows="3" placeholder="e.g., Real-time customer support chatbot with sentiment analysis..."></textarea>
        </div>
        <div>
          <label class="label">Project ID (optional)</label>
          <input v-model="recForm.project_id" class="input" placeholder="Link to a project for saved mappings" />
        </div>
        <button @click="getRecommendations" :disabled="recommending || !recForm.use_case_description" class="btn-primary">
          {{ recommending ? 'Analyzing...' : 'Get Recommendations' }}
        </button>

        <div v-if="recommendations" class="mt-6 space-y-3">
          <h3 class="text-sm font-semibold text-gray-700">Recommended Models</h3>
          <div v-for="(rec, i) in recommendations" :key="i" class="p-4 rounded-lg bg-gray-50">
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-gray-800">{{ rec.model_name || rec.model_id }}</h4>
              <span class="badge bg-primary-100 text-primary-700">{{ Math.round((rec.confidence || 0) * 100) }}% match</span>
            </div>
            <p class="text-sm text-gray-600">{{ rec.rationale }}</p>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>
