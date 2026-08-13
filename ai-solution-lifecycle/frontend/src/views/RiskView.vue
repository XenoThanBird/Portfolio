<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRisksStore } from '../stores/risks'
import RiskMatrix from '../components/risk/RiskMatrix.vue'
import RiskCard from '../components/risk/RiskCard.vue'
import ChangeRequestModal from '../components/risk/ChangeRequestModal.vue'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const store = useRisksStore()
const showCreate = ref(false)
const showCR = ref(false)
const form = ref({
  title: '', description: '', category: 'technical',
  probability: 'possible', impact: 'moderate', mitigation_plan: '', owner_email: '',
})

onMounted(() => {
  store.fetchRisks(projectId)
  store.fetchMatrix(projectId)
  store.fetchChangeRequests(projectId)
})

async function createRisk() {
  await store.createRisk(projectId, form.value)
  showCreate.value = false
  form.value = { title: '', description: '', category: 'technical', probability: 'possible', impact: 'moderate', mitigation_plan: '', owner_email: '' }
  store.fetchMatrix(projectId)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Risk Register</h1>
      <div class="flex gap-2">
        <button @click="showCR = true" class="btn-secondary">Change Requests ({{ store.changeRequests.length }})</button>
        <button @click="showCreate = true" class="btn-primary">Add Risk</button>
      </div>
    </div>

    <LoadingSpinner v-if="store.loading" />

    <template v-else>
      <!-- Risk Matrix -->
      <RiskMatrix v-if="store.matrix" :data="store.matrix" class="mb-6" />

      <!-- Risk list -->
      <div class="space-y-4">
        <RiskCard v-for="risk in store.risks" :key="risk.id" :risk="risk" @updated="store.fetchRisks(projectId); store.fetchMatrix(projectId)" />
      </div>
      <p v-if="!store.risks.length" class="text-sm text-gray-400 text-center py-8">No risks recorded.</p>
    </template>

    <!-- Create Risk Modal -->
    <Modal :show="showCreate" title="New Risk" @close="showCreate = false">
      <form @submit.prevent="createRisk" class="space-y-4">
        <div>
          <label class="label">Title</label>
          <input v-model="form.title" class="input" required />
        </div>
        <div>
          <label class="label">Description</label>
          <textarea v-model="form.description" class="input" rows="2"></textarea>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Category</label>
            <select v-model="form.category" class="input">
              <option value="technical">Technical</option>
              <option value="operational">Operational</option>
              <option value="financial">Financial</option>
              <option value="compliance">Compliance</option>
              <option value="strategic">Strategic</option>
            </select>
          </div>
          <div>
            <label class="label">Probability</label>
            <select v-model="form.probability" class="input">
              <option value="rare">Rare</option>
              <option value="unlikely">Unlikely</option>
              <option value="possible">Possible</option>
              <option value="likely">Likely</option>
              <option value="almost_certain">Almost Certain</option>
            </select>
          </div>
          <div>
            <label class="label">Impact</label>
            <select v-model="form.impact" class="input">
              <option value="negligible">Negligible</option>
              <option value="minor">Minor</option>
              <option value="moderate">Moderate</option>
              <option value="major">Major</option>
              <option value="catastrophic">Catastrophic</option>
            </select>
          </div>
        </div>
        <div>
          <label class="label">Mitigation Plan</label>
          <textarea v-model="form.mitigation_plan" class="input" rows="2"></textarea>
        </div>
        <div>
          <label class="label">Owner Email</label>
          <input v-model="form.owner_email" type="email" class="input" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="btn-secondary" @click="showCreate = false">Cancel</button>
          <button type="submit" class="btn-primary">Create</button>
        </div>
      </form>
    </Modal>

    <!-- Change Requests -->
    <ChangeRequestModal
      :show="showCR"
      :project-id="projectId"
      :change-requests="store.changeRequests"
      @close="showCR = false"
      @created="store.fetchChangeRequests(projectId)"
    />
  </div>
</template>
