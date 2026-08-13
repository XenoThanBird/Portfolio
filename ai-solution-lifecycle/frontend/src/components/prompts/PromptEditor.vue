<script setup>
import { ref, onMounted } from 'vue'
import promptsApi from '../../api/prompts'

const props = defineProps({ projectId: String, prompt: Object })
const emit = defineEmits(['saved', 'cancel'])

const form = ref({
  name: '', template: '', category: '', tags: '',
})

onMounted(() => {
  if (props.prompt) {
    form.value = {
      name: props.prompt.name,
      template: props.prompt.template,
      category: props.prompt.category || '',
      tags: (props.prompt.tags || []).join(', '),
    }
  }
})

async function save() {
  const payload = {
    name: form.value.name,
    template: form.value.template,
    category: form.value.category || null,
    tags: form.value.tags.split(',').map(t => t.trim()).filter(Boolean),
  }
  if (props.prompt) {
    await promptsApi.update(props.prompt.id, payload)
  } else {
    await promptsApi.create(props.projectId, payload)
  }
  emit('saved')
}
</script>

<template>
  <form @submit.prevent="save" class="space-y-4">
    <div>
      <label class="label">Name</label>
      <input v-model="form.name" class="input" required />
    </div>
    <div>
      <label class="label">Template</label>
      <textarea v-model="form.template" class="input font-mono text-sm" rows="6" placeholder="Use {{variable_name}} for dynamic inputs..." required></textarea>
      <p class="text-xs text-gray-400 mt-1">Variables are auto-extracted from &#123;&#123;variable&#125;&#125; syntax.</p>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="label">Category</label>
        <input v-model="form.category" class="input" placeholder="e.g., document_generation" />
      </div>
      <div>
        <label class="label">Tags (comma-separated)</label>
        <input v-model="form.tags" class="input" placeholder="brd, requirements" />
      </div>
    </div>
    <div class="flex justify-end gap-3 pt-2">
      <button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
      <button type="submit" class="btn-primary">{{ prompt ? 'Update' : 'Create' }}</button>
    </div>
  </form>
</template>
