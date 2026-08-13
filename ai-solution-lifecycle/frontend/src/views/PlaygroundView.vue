<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import promptsApi from '../api/prompts'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const prompts = ref([])
const selectedId = ref(route.query.prompt || '')
const inputs = ref({})
const model = ref('gpt-4o')
const output = ref(null)
const running = ref(false)
const rating = ref(0)

const selectedPrompt = computed(() => prompts.value.find(p => p.id === selectedId.value))
const variables = computed(() => selectedPrompt.value?.variables || [])

async function fetchPrompts() {
  const { data } = await promptsApi.list(projectId)
  prompts.value = data
}

function onSelectPrompt() {
  inputs.value = {}
  output.value = null
  rating.value = 0
  variables.value.forEach(v => { inputs.value[v] = '' })
}

async function runPrompt() {
  running.value = true
  output.value = null
  try {
    const { data } = await promptsApi.run(selectedId.value, { model: model.value, inputs: inputs.value })
    output.value = data
  } catch (e) {
    output.value = { output: `Error: ${e.response?.data?.detail || e.message}`, latency_ms: 0, tokens: 0, cost: 0 }
  } finally { running.value = false }
}

async function submitRating(stars) {
  rating.value = stars
  if (output.value?.id) {
    await promptsApi.feedback(output.value.id, { user_rating: stars })
  }
}

onMounted(fetchPrompts)
</script>

<template>
  <div>
    <h1 class="page-title mb-6">Prompt Playground</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Input panel -->
      <div class="space-y-4">
        <div class="card">
          <label class="label">Select Prompt</label>
          <select v-model="selectedId" @change="onSelectPrompt" class="input">
            <option value="">Choose a prompt...</option>
            <option v-for="p in prompts" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div v-if="selectedPrompt" class="card">
          <p class="text-xs text-gray-500 mb-3 font-mono whitespace-pre-wrap bg-gray-50 p-3 rounded-lg">{{ selectedPrompt.template }}</p>

          <div v-for="v in variables" :key="v" class="mb-3">
            <label class="label">{{ v }}</label>
            <input v-model="inputs[v]" class="input" :placeholder="`Enter ${v}...`" />
          </div>

          <div class="flex items-center gap-4">
            <div class="flex-1">
              <label class="label">Model</label>
              <select v-model="model" class="input">
                <option value="gpt-4o">GPT-4o</option>
                <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                <option value="llama-3.1-70b">Llama 3.1 70B</option>
              </select>
            </div>
            <button @click="runPrompt" :disabled="running" class="btn-primary mt-6">
              {{ running ? 'Running...' : 'Run' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Output panel -->
      <div class="space-y-4">
        <div class="card min-h-[300px]">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Output</h3>
          <LoadingSpinner v-if="running" message="Generating response..." />
          <template v-else-if="output">
            <div class="prose prose-sm max-w-none whitespace-pre-wrap bg-gray-50 p-4 rounded-lg mb-4 max-h-96 overflow-y-auto">{{ output.output }}</div>
            <div class="flex items-center justify-between text-xs text-gray-500">
              <div class="flex gap-4">
                <span>{{ output.latency_ms }}ms</span>
                <span>{{ output.tokens }} tokens</span>
                <span>${{ output.cost?.toFixed(4) }}</span>
              </div>
              <div class="flex gap-1">
                <button
                  v-for="star in 5"
                  :key="star"
                  @click="submitRating(star)"
                  class="text-lg transition-colors"
                  :class="star <= rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'"
                >&#9733;</button>
              </div>
            </div>
          </template>
          <p v-else class="text-sm text-gray-400 text-center mt-20">Select a prompt and click Run to see output.</p>
        </div>
      </div>
    </div>
  </div>
</template>
