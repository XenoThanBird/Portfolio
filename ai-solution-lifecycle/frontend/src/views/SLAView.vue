<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import slaApi from '../api/sla'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const slas = ref([])
const dashboard = ref(null)
const loading = ref(false)
const showCreate = ref(false)
const showMetric = ref(false)
const selectedSla = ref(null)
const form = ref({ name: '', metric_type: 'response_time', target_value: 0, target_unit: 'ms', warning_threshold: 0, breach_threshold: 0 })
const metricForm = ref({ measured_value: 0, notes: '' })

async function fetchAll() {
  loading.value = true
  try {
    const [slasRes, dashRes] = await Promise.all([slaApi.list(projectId), slaApi.dashboard(projectId)])
    slas.value = slasRes.data
    dashboard.value = dashRes.data
  } finally { loading.value = false }
}

async function createSla() {
  await slaApi.create(projectId, form.value)
  showCreate.value = false
  await fetchAll()
}

function openAddMetric(sla) {
  selectedSla.value = sla
  metricForm.value = { measured_value: 0, notes: '' }
  showMetric.value = true
}

async function addMetric() {
  await slaApi.addMetric(selectedSla.value.id, metricForm.value)
  showMetric.value = false
  await fetchAll()
}

onMounted(fetchAll)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">SLA Tracking</h1>
      <button @click="showCreate = true" class="btn-primary">New SLA</button>
    </div>

    <!-- Dashboard stats -->
    <div v-if="dashboard" class="grid grid-cols-3 gap-4 mb-6">
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold" :class="dashboard.overall_compliance >= 95 ? 'text-green-600' : dashboard.overall_compliance >= 80 ? 'text-yellow-600' : 'text-red-600'">
          {{ dashboard.overall_compliance }}%
        </p>
        <p class="text-xs text-gray-500">Overall Compliance</p>
      </div>
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold text-gray-800">{{ dashboard.total_slas }}</p>
        <p class="text-xs text-gray-500">Total SLAs</p>
      </div>
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold text-gray-800">{{ dashboard.total_measurements }}</p>
        <p class="text-xs text-gray-500">Measurements</p>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="space-y-4">
      <div v-for="s in slas" :key="s.id" class="card">
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-800">{{ s.name }}</h3>
            <p class="text-xs text-gray-500">{{ s.metric_type }} &middot; Target: {{ s.target_value }} {{ s.target_unit }}</p>
          </div>
          <button @click="openAddMetric(s)" class="btn-sm btn-secondary">Add Metric</button>
        </div>
        <div class="flex gap-4 text-sm">
          <span class="text-yellow-600">Warning: {{ s.warning_threshold }}</span>
          <span class="text-red-600">Breach: {{ s.breach_threshold }}</span>
        </div>
      </div>
    </div>

    <Modal :show="showCreate" title="New SLA Definition" @close="showCreate = false">
      <form @submit.prevent="createSla" class="space-y-4">
        <div>
          <label class="label">Name</label>
          <input v-model="form.name" class="input" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Metric Type</label>
            <select v-model="form.metric_type" class="input">
              <option value="response_time">Response Time</option>
              <option value="uptime">Uptime</option>
              <option value="throughput">Throughput</option>
              <option value="error_rate">Error Rate</option>
              <option value="resolution_time">Resolution Time</option>
            </select>
          </div>
          <div>
            <label class="label">Target Unit</label>
            <input v-model="form.target_unit" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Target</label>
            <input v-model.number="form.target_value" type="number" step="0.01" class="input" />
          </div>
          <div>
            <label class="label">Warning</label>
            <input v-model.number="form.warning_threshold" type="number" step="0.01" class="input" />
          </div>
          <div>
            <label class="label">Breach</label>
            <input v-model.number="form.breach_threshold" type="number" step="0.01" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="btn-secondary" @click="showCreate = false">Cancel</button>
          <button type="submit" class="btn-primary">Create</button>
        </div>
      </form>
    </Modal>

    <Modal :show="showMetric" title="Record SLA Metric" @close="showMetric = false">
      <form @submit.prevent="addMetric" class="space-y-4">
        <div>
          <label class="label">Measured Value</label>
          <input v-model.number="metricForm.measured_value" type="number" step="0.01" class="input" required />
        </div>
        <div>
          <label class="label">Notes</label>
          <input v-model="metricForm.notes" class="input" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="btn-secondary" @click="showMetric = false">Cancel</button>
          <button type="submit" class="btn-primary">Record</button>
        </div>
      </form>
    </Modal>
  </div>
</template>
