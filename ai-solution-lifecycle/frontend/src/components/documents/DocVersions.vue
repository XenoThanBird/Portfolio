<script setup>
import { onMounted, ref } from 'vue'
import docsApi from '../../api/documents'

const props = defineProps({ docId: String })
const versions = ref([])

onMounted(async () => {
  const { data } = await docsApi.versions(props.docId)
  versions.value = data
})
</script>

<template>
  <div class="space-y-2">
    <h4 class="text-sm font-semibold text-gray-700">Version History</h4>
    <div v-for="v in versions" :key="v.id" class="p-3 bg-gray-50 rounded-lg">
      <div class="flex justify-between text-xs text-gray-500">
        <span>v{{ v.version }}</span>
        <span>{{ new Date(v.created_at).toLocaleString() }}</span>
      </div>
      <p v-if="v.change_summary" class="text-xs text-gray-600 mt-1">{{ v.change_summary }}</p>
    </div>
    <p v-if="!versions.length" class="text-xs text-gray-400">No version history.</p>
  </div>
</template>
