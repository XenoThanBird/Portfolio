<script setup>
import { ref } from 'vue'
import { useDocumentsStore } from '../../stores/documents'

const props = defineProps({ projectId: String })
const emit = defineEmits(['generated'])
const store = useDocumentsStore()

const form = ref({ doc_type: 'brd', prompt: '' })

const docTypes = [
  { value: 'brd', label: 'Business Requirements (BRD)' },
  { value: 'trd', label: 'Technical Requirements (TRD)' },
  { value: 'functional', label: 'Functional Specification' },
  { value: 'design_schematic', label: 'Design Schematic' },
  { value: 'user_schematic', label: 'User Schematic' },
]

async function generate() {
  const doc = await store.generate(props.projectId, form.value)
  emit('generated', doc)
}
</script>

<template>
  <div class="card border-primary-200 bg-primary-50/30">
    <h3 class="font-semibold text-gray-800 mb-4">AI Document Generator</h3>
    <form @submit.prevent="generate" class="space-y-4">
      <div>
        <label class="label">Document Type</label>
        <select v-model="form.doc_type" class="input">
          <option v-for="dt in docTypes" :key="dt.value" :value="dt.value">{{ dt.label }}</option>
        </select>
      </div>
      <div>
        <label class="label">Describe what you need</label>
        <textarea v-model="form.prompt" class="input" rows="4" placeholder="Describe the project context, objectives, and any specific requirements..." required minlength="10"></textarea>
      </div>
      <button type="submit" class="btn-primary" :disabled="store.generating">
        {{ store.generating ? 'Generating...' : 'Generate Document' }}
      </button>
    </form>
  </div>
</template>
