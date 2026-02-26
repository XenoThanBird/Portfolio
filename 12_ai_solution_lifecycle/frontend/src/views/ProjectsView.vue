<script setup>
import { onMounted, ref } from 'vue'
import { useProjectsStore } from '../stores/projects'
import StatusBadge from '../components/shared/StatusBadge.vue'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const store = useProjectsStore()
const showCreate = ref(false)
const form = ref({ name: '', description: '', owner_email: '', budget_millions: 1, data_maturity_level: 1 })

onMounted(() => store.fetchAll())

async function create() {
  await store.create(form.value)
  showCreate.value = false
  form.value = { name: '', description: '', owner_email: '', budget_millions: 1, data_maturity_level: 1 }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Projects</h1>
      <button @click="showCreate = true" class="btn-primary">New Project</button>
    </div>

    <LoadingSpinner v-if="store.loading" />

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <RouterLink
        v-for="p in store.projects"
        :key="p.id"
        :to="`/projects/${p.id}`"
        class="card hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between mb-3">
          <h3 class="font-semibold text-gray-800">{{ p.name }}</h3>
          <StatusBadge :status="p.status" />
        </div>
        <p class="text-sm text-gray-500 line-clamp-2 mb-3">{{ p.description }}</p>
        <div class="flex items-center justify-between text-xs text-gray-400">
          <span>{{ p.owner_email }}</span>
          <span v-if="p.budget_millions">${{ p.budget_millions }}M</span>
        </div>
      </RouterLink>
    </div>

    <Modal :show="showCreate" title="Create Project" @close="showCreate = false">
      <form @submit.prevent="create" class="space-y-4">
        <div>
          <label class="label">Name</label>
          <input v-model="form.name" class="input" required />
        </div>
        <div>
          <label class="label">Description</label>
          <textarea v-model="form.description" class="input" rows="3"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Owner Email</label>
            <input v-model="form.owner_email" type="email" class="input" required />
          </div>
          <div>
            <label class="label">Budget ($M)</label>
            <input v-model.number="form.budget_millions" type="number" step="0.1" class="input" />
          </div>
        </div>
        <div>
          <label class="label">Data Maturity Level (1-5)</label>
          <input v-model.number="form.data_maturity_level" type="number" min="1" max="5" class="input" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="btn-secondary" @click="showCreate = false">Cancel</button>
          <button type="submit" class="btn-primary">Create</button>
        </div>
      </form>
    </Modal>
  </div>
</template>
