<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useValueStore } from '../stores/value'
import ROICalculator from '../components/value/ROICalculator.vue'
import RadarChart from '../components/value/RadarChart.vue'
import ReadinessGauge from '../components/value/ReadinessGauge.vue'
import RoadmapTimeline from '../components/value/RoadmapTimeline.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const store = useValueStore()
const editing = ref(false)
const form = ref({
  financial_impact: 50, operational_excellence: 50, strategic_value: 50,
  risk_mitigation: 50, customer_impact: 50, innovation_index: 50,
  data_maturity: 0.5, organizational_readiness: 0.5, technical_capability: 0.5,
})

onMounted(async () => {
  await store.fetchAssessment(projectId)
  if (store.assessment) {
    form.value = {
      financial_impact: store.assessment.financial_impact,
      operational_excellence: store.assessment.operational_excellence,
      strategic_value: store.assessment.strategic_value,
      risk_mitigation: store.assessment.risk_mitigation,
      customer_impact: store.assessment.customer_impact,
      innovation_index: store.assessment.innovation_index,
      data_maturity: store.assessment.data_maturity,
      organizational_readiness: store.assessment.organizational_readiness,
      technical_capability: store.assessment.technical_capability,
    }
  }
  store.fetchRoadmap(projectId).catch(() => {})
})

async function save() {
  await store.saveAssessment(projectId, form.value)
  editing.value = false
}

const classificationColors = {
  Transformational: 'text-green-600 bg-green-50',
  Strategic: 'text-blue-600 bg-blue-50',
  'High Potential': 'text-purple-600 bg-purple-50',
  Operational: 'text-yellow-600 bg-yellow-50',
  Monitor: 'text-gray-600 bg-gray-50',
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Value Assessment</h1>
      <button @click="editing = !editing" class="btn-secondary">
        {{ editing ? 'Cancel' : (store.assessment ? 'Edit Assessment' : 'Create Assessment') }}
      </button>
    </div>

    <LoadingSpinner v-if="store.loading" />

    <!-- Assessment form -->
    <div v-if="editing" class="card mb-6">
      <form @submit.prevent="save" class="space-y-6">
        <h3 class="font-semibold text-gray-800">Value Components (0-100)</h3>
        <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="field in ['financial_impact', 'operational_excellence', 'strategic_value', 'risk_mitigation', 'customer_impact', 'innovation_index']" :key="field">
            <label class="label">{{ field.replace(/_/g, ' ') }}</label>
            <input v-model.number="form[field]" type="range" min="0" max="100" class="w-full" />
            <p class="text-xs text-gray-500 text-right">{{ form[field] }}</p>
          </div>
        </div>

        <h3 class="font-semibold text-gray-800">Readiness Scores (0-1)</h3>
        <div class="grid grid-cols-3 gap-4">
          <div v-for="field in ['data_maturity', 'organizational_readiness', 'technical_capability']" :key="field">
            <label class="label">{{ field.replace(/_/g, ' ') }}</label>
            <input v-model.number="form[field]" type="range" min="0" max="1" step="0.05" class="w-full" />
            <p class="text-xs text-gray-500 text-right">{{ form[field] }}</p>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="editing = false">Cancel</button>
          <button type="submit" class="btn-primary">Save & Calculate</button>
        </div>
      </form>
    </div>

    <!-- Results -->
    <template v-if="store.assessment && !editing">
      <!-- Score + Classification -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div class="card text-center">
          <p class="text-5xl font-bold text-primary-600">{{ store.assessment.final_score }}</p>
          <p class="text-sm text-gray-500 mt-2">Final Value Score</p>
          <div class="mt-3 inline-block px-3 py-1 rounded-full text-sm font-medium" :class="classificationColors[store.assessment.classification] || 'bg-gray-50 text-gray-600'">
            {{ store.assessment.classification }}
          </div>
        </div>

        <RadarChart :assessment="store.assessment" />
        <ReadinessGauge :assessment="store.assessment" />
      </div>

      <!-- Action & Investment -->
      <div class="grid grid-cols-2 gap-6 mb-6">
        <div class="card">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Recommended Action</h3>
          <p class="text-sm text-gray-600">{{ store.assessment.recommended_action }}</p>
        </div>
        <div class="card">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Investment Range</h3>
          <p class="text-sm text-gray-600">{{ store.assessment.investment_range }}</p>
        </div>
      </div>

      <!-- ROI Calculator -->
      <ROICalculator :project-id="projectId" class="mb-6" />

      <!-- Roadmap -->
      <RoadmapTimeline v-if="store.roadmap" :roadmap="store.roadmap" />
    </template>

    <p v-if="!store.assessment && !store.loading && !editing" class="text-sm text-gray-400 text-center py-8">
      No value assessment yet. Click "Create Assessment" to get started.
    </p>
  </div>
</template>
