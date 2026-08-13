<script setup>
import { ref } from 'vue'
import Modal from '../shared/Modal.vue'
import StatusBadge from '../shared/StatusBadge.vue'
import risksApi from '../../api/risks'

const props = defineProps({
  show: Boolean,
  projectId: String,
  changeRequests: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'created'])

const showForm = ref(false)
const form = ref({ title: '', description: '', justification: '', impact_assessment: '', priority: 'medium' })

async function create() {
  await risksApi.createChangeRequest(props.projectId, form.value)
  showForm.value = false
  form.value = { title: '', description: '', justification: '', impact_assessment: '', priority: 'medium' }
  emit('created')
}
</script>

<template>
  <Modal :show="show" title="Change Requests" max-width="max-w-3xl" @close="emit('close')">
    <div class="mb-4">
      <button @click="showForm = !showForm" class="btn-sm btn-primary">
        {{ showForm ? 'Cancel' : 'New Request' }}
      </button>
    </div>

    <form v-if="showForm" @submit.prevent="create" class="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg">
      <div>
        <label class="label">Title</label>
        <input v-model="form.title" class="input" required />
      </div>
      <div>
        <label class="label">Description</label>
        <textarea v-model="form.description" class="input" rows="2"></textarea>
      </div>
      <div>
        <label class="label">Justification</label>
        <textarea v-model="form.justification" class="input" rows="2"></textarea>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Impact Assessment</label>
          <textarea v-model="form.impact_assessment" class="input" rows="2"></textarea>
        </div>
        <div>
          <label class="label">Priority</label>
          <select v-model="form.priority" class="input">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>
      <button type="submit" class="btn-primary">Submit</button>
    </form>

    <div class="space-y-3">
      <div v-for="cr in changeRequests" :key="cr.id" class="p-4 border border-gray-200 rounded-lg">
        <div class="flex items-start justify-between mb-2">
          <h4 class="font-medium text-gray-800">{{ cr.title }}</h4>
          <StatusBadge :status="cr.status" />
        </div>
        <p v-if="cr.justification" class="text-sm text-gray-600 mb-1">{{ cr.justification }}</p>
        <p class="text-xs text-gray-400">{{ cr.requested_by }} &middot; {{ new Date(cr.created_at).toLocaleDateString() }}</p>
      </div>
      <p v-if="!changeRequests.length" class="text-sm text-gray-400 text-center py-4">No change requests.</p>
    </div>
  </Modal>
</template>
