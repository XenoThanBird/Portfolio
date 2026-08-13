<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import raciApi from '../api/raci'
import RACIMatrix from '../components/raci/RACIMatrix.vue'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const matrixData = ref(null)
const loading = ref(false)
const showAdd = ref(false)
const form = ref({ deliverable: '', person_name: '', person_email: '', role_type: 'R' })

async function fetchMatrix() {
  loading.value = true
  try {
    const { data } = await raciApi.getMatrix(projectId)
    matrixData.value = data
  } finally { loading.value = false }
}

async function addEntry() {
  await raciApi.create(projectId, form.value)
  showAdd.value = false
  form.value = { deliverable: '', person_name: '', person_email: '', role_type: 'R' }
  await fetchMatrix()
}

async function onCellClick(deliverable, person, currentRole) {
  const roles = ['R', 'A', 'C', 'I', '']
  const idx = roles.indexOf(currentRole)
  const nextRole = roles[(idx + 1) % roles.length]

  // Find existing entry
  const entry = matrixData.value?.entries?.find(e => e.deliverable === deliverable && e.person_email === person)
  if (entry && !nextRole) {
    await raciApi.delete(entry.id)
  } else if (entry) {
    await raciApi.update(entry.id, { role_type: nextRole })
  } else if (nextRole) {
    await raciApi.create(projectId, { deliverable, person_name: person, person_email: person, role_type: nextRole })
  }
  await fetchMatrix()
}

onMounted(fetchMatrix)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">RACI Matrix</h1>
      <button @click="showAdd = true" class="btn-primary">Add Entry</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <RACIMatrix v-else-if="matrixData" :data="matrixData" @cell-click="onCellClick" />
    <p v-else class="text-sm text-gray-400 text-center py-8">No RACI entries yet.</p>

    <Modal :show="showAdd" title="Add RACI Entry" @close="showAdd = false">
      <form @submit.prevent="addEntry" class="space-y-4">
        <div>
          <label class="label">Deliverable</label>
          <input v-model="form.deliverable" class="input" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Person Name</label>
            <input v-model="form.person_name" class="input" required />
          </div>
          <div>
            <label class="label">Person Email</label>
            <input v-model="form.person_email" type="email" class="input" required />
          </div>
        </div>
        <div>
          <label class="label">Role</label>
          <select v-model="form.role_type" class="input">
            <option value="R">Responsible</option>
            <option value="A">Accountable</option>
            <option value="C">Consulted</option>
            <option value="I">Informed</option>
          </select>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="btn-secondary" @click="showAdd = false">Cancel</button>
          <button type="submit" class="btn-primary">Add</button>
        </div>
      </form>
    </Modal>
  </div>
</template>
