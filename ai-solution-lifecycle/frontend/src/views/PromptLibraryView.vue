<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import promptsApi from '../api/prompts'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import PromptCard from '../components/prompts/PromptCard.vue'
import PromptEditor from '../components/prompts/PromptEditor.vue'

const route = useRoute()
const projectId = route.params.id
const prompts = ref([])
const loading = ref(false)
const search = ref('')
const category = ref('')
const showEditor = ref(false)
const editingPrompt = ref(null)

const categories = computed(() => {
  const cats = new Set(prompts.value.map(p => p.category).filter(Boolean))
  return ['', ...cats]
})

const filtered = computed(() => {
  let list = prompts.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || p.tags?.some(t => t.toLowerCase().includes(q)))
  }
  if (category.value) list = list.filter(p => p.category === category.value)
  return list
})

async function fetchPrompts() {
  loading.value = true
  try {
    const { data } = await promptsApi.list(projectId)
    prompts.value = data
  } finally { loading.value = false }
}

function openCreate() {
  editingPrompt.value = null
  showEditor.value = true
}

function openEdit(prompt) {
  editingPrompt.value = prompt
  showEditor.value = true
}

async function onSaved() {
  showEditor.value = false
  await fetchPrompts()
}

onMounted(fetchPrompts)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Prompt Library</h1>
      <button @click="openCreate" class="btn-primary">New Prompt</button>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold text-gray-800">{{ prompts.length }}</p>
        <p class="text-xs text-gray-500">Total Prompts</p>
      </div>
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold text-gray-800">{{ prompts.reduce((s, p) => s + (p.usage_count || 0), 0) }}</p>
        <p class="text-xs text-gray-500">Total Runs</p>
      </div>
      <div class="card text-center !p-4">
        <p class="text-2xl font-bold text-gray-800">{{ Math.round(prompts.reduce((s, p) => s + (p.success_rate || 0), 0) / Math.max(prompts.length, 1) * 100) }}%</p>
        <p class="text-xs text-gray-500">Avg Success Rate</p>
      </div>
    </div>

    <!-- Search + filter -->
    <div class="flex gap-4 mb-6">
      <input v-model="search" class="input flex-1" placeholder="Search prompts..." />
      <select v-model="category" class="input w-48">
        <option value="">All Categories</option>
        <option v-for="cat in categories.filter(c => c)" :key="cat" :value="cat">{{ cat }}</option>
      </select>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <PromptCard
        v-for="p in filtered"
        :key="p.id"
        :prompt="p"
        @edit="openEdit(p)"
        @use="$router.push(`/projects/${projectId}/playground?prompt=${p.id}`)"
      />
    </div>

    <Modal :show="showEditor" :title="editingPrompt ? 'Edit Prompt' : 'New Prompt'" max-width="max-w-2xl" @close="showEditor = false">
      <PromptEditor :project-id="projectId" :prompt="editingPrompt" @saved="onSaved" @cancel="showEditor = false" />
    </Modal>
  </div>
</template>
