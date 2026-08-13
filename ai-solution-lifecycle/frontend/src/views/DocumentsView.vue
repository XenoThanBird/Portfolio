<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDocumentsStore } from '../stores/documents'
import StatusBadge from '../components/shared/StatusBadge.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import DocGenerator from '../components/documents/DocGenerator.vue'
import DocViewer from '../components/documents/DocViewer.vue'

const route = useRoute()
const projectId = route.params.id
const store = useDocumentsStore()
const showGenerator = ref(false)
const selectedDoc = ref(null)

onMounted(() => store.fetchAll(projectId))

function onGenerated(doc) {
  showGenerator.value = false
  selectedDoc.value = doc
}

const docTypeLabels = { brd: 'BRD', trd: 'TRD', functional: 'Functional', design_schematic: 'Design', user_schematic: 'User' }
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="page-title">Documents</h1>
      <button @click="showGenerator = !showGenerator" class="btn-primary">
        {{ showGenerator ? 'Close Generator' : 'Generate Document' }}
      </button>
    </div>

    <DocGenerator v-if="showGenerator" :project-id="projectId" @generated="onGenerated" class="mb-6" />

    <DocViewer v-if="selectedDoc" :doc="selectedDoc" @close="selectedDoc = null" class="mb-6" />

    <LoadingSpinner v-if="store.loading" />

    <div v-else class="space-y-3">
      <div
        v-for="doc in store.documents"
        :key="doc.id"
        class="card flex items-center justify-between cursor-pointer hover:shadow-md transition-shadow"
        @click="selectedDoc = doc"
      >
        <div>
          <div class="flex items-center gap-2">
            <span class="badge bg-primary-100 text-primary-700">{{ docTypeLabels[doc.doc_type] || doc.doc_type }}</span>
            <h3 class="font-medium text-gray-800">{{ doc.title }}</h3>
          </div>
          <p class="text-xs text-gray-500 mt-1">v{{ doc.version }} &middot; {{ doc.llm_model_used || 'manual' }}</p>
        </div>
        <StatusBadge :status="doc.status" />
      </div>

      <p v-if="!store.documents.length && !store.loading" class="text-sm text-gray-400 text-center py-8">
        No documents yet. Use the generator to create your first document.
      </p>
    </div>
  </div>
</template>
