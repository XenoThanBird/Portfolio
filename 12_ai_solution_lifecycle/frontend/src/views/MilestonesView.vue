<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMilestonesStore } from '../stores/milestones'
import KanbanColumn from '../components/milestones/KanbanColumn.vue'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const store = useMilestonesStore()
const showCreate = ref(false)
const form = ref({ title: '', priority: 'medium', owner_email: '', due_date: '' })

onMounted(() => store.fetchAll(projectId))

const columns = [
  { key: 'backlog', label: 'Backlog', color: 'bg-gray-200' },
  { key: 'in_progress', label: 'In Progress', color: 'bg-blue-200' },
  { key: 'review', label: 'Review', color: 'bg-purple-200' },
  { key: 'done', label: 'Done', color: 'bg-green-200' },
]

async function create() {
  await store.create(projectId, form.value)
  showCreate.value = false
  form.value = { title: '', priority: 'medium', owner_email: '', due_date: '' }
}

async function moveToStatus(milestoneId, newStatus) {
  await store.update(milestoneId, { status: newStatus })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Milestones</h1>
      <button @click="showCreate = true" class="btn-primary">Add Milestone</button>
    </div>

    <LoadingSpinner v-if="store.loading" />

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KanbanColumn
        v-for="col in columns"
        :key="col.key"
        :title="col.label"
        :color="col.color"
        :items="store.raw[col.key]"
        :status="col.key"
        @move="moveToStatus"
      />
    </div>

    <Modal :show="showCreate" title="New Milestone" @close="showCreate = false">
      <form @submit.prevent="create" class="space-y-4">
        <div>
          <label class="label">Title</label>
          <input v-model="form.title" class="input" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Priority</label>
            <select v-model="form.priority" class="input">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label class="label">Due Date</label>
            <input v-model="form.due_date" type="date" class="input" />
          </div>
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
  </div>
</template>
