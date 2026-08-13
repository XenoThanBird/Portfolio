<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '../stores/projects'
import { useDashboardStore } from '../stores/dashboard'
import StatusBadge from '../components/shared/StatusBadge.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const route = useRoute()
const projectId = route.params.id
const projects = useProjectsStore()
const dash = useDashboardStore()

onMounted(() => {
  projects.fetchOne(projectId)
  dash.fetchProject(projectId)
})

const tabs = [
  { label: 'Documents', to: `/projects/${projectId}/documents` },
  { label: 'Prompts', to: `/projects/${projectId}/prompts` },
  { label: 'Milestones', to: `/projects/${projectId}/milestones` },
  { label: 'RACI', to: `/projects/${projectId}/raci` },
  { label: 'SLA', to: `/projects/${projectId}/sla` },
  { label: 'Alerts', to: `/projects/${projectId}/alerts` },
  { label: 'Risks', to: `/projects/${projectId}/risks` },
  { label: 'Value', to: `/projects/${projectId}/value` },
]
</script>

<template>
  <div>
    <LoadingSpinner v-if="projects.loading" />

    <template v-else-if="projects.current">
      <div class="mb-6">
        <div class="flex items-center gap-3 mb-2">
          <h1 class="page-title">{{ projects.current.name }}</h1>
          <StatusBadge :status="projects.current.status" />
        </div>
        <p class="text-sm text-gray-500">{{ projects.current.description }}</p>
      </div>

      <!-- Quick stats -->
      <div v-if="dash.projectDash" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        <div class="card text-center !p-4">
          <p class="text-2xl font-bold text-gray-800">{{ dash.projectDash.total_milestones }}</p>
          <p class="text-xs text-gray-500">Milestones</p>
        </div>
        <div class="card text-center !p-4">
          <p class="text-2xl font-bold text-gray-800">{{ dash.projectDash.document_count }}</p>
          <p class="text-xs text-gray-500">Documents</p>
        </div>
        <div class="card text-center !p-4">
          <p class="text-2xl font-bold" :class="dash.projectDash.open_risks > 0 ? 'text-red-600' : 'text-green-600'">{{ dash.projectDash.open_risks }}</p>
          <p class="text-xs text-gray-500">Open Risks</p>
        </div>
        <div class="card text-center !p-4">
          <p class="text-2xl font-bold" :class="dash.projectDash.unacknowledged_alerts > 0 ? 'text-yellow-600' : 'text-green-600'">{{ dash.projectDash.unacknowledged_alerts }}</p>
          <p class="text-xs text-gray-500">Alerts</p>
        </div>
        <div class="card text-center !p-4">
          <p class="text-2xl font-bold text-primary-600">{{ dash.projectDash.value_score ?? '—' }}</p>
          <p class="text-xs text-gray-500">Value Score</p>
        </div>
        <div class="card text-center !p-4">
          <p class="text-sm font-semibold text-gray-700">{{ dash.projectDash.value_classification ?? '—' }}</p>
          <p class="text-xs text-gray-500">Classification</p>
        </div>
      </div>

      <!-- Milestone breakdown -->
      <div v-if="dash.projectDash" class="card mb-6">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Milestone Progress</h3>
        <div class="flex gap-2 h-4 rounded-full overflow-hidden bg-gray-100">
          <div class="bg-green-500 transition-all" :style="{ width: (dash.projectDash.milestones.done / Math.max(dash.projectDash.total_milestones, 1)) * 100 + '%' }" :title="`Done: ${dash.projectDash.milestones.done}`"></div>
          <div class="bg-blue-500 transition-all" :style="{ width: (dash.projectDash.milestones.in_progress / Math.max(dash.projectDash.total_milestones, 1)) * 100 + '%' }" :title="`In Progress: ${dash.projectDash.milestones.in_progress}`"></div>
          <div class="bg-purple-500 transition-all" :style="{ width: (dash.projectDash.milestones.review / Math.max(dash.projectDash.total_milestones, 1)) * 100 + '%' }" :title="`Review: ${dash.projectDash.milestones.review}`"></div>
        </div>
        <div class="flex gap-4 mt-2 text-xs text-gray-500">
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500"></span> Done {{ dash.projectDash.milestones.done }}</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-blue-500"></span> In Progress {{ dash.projectDash.milestones.in_progress }}</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-purple-500"></span> Review {{ dash.projectDash.milestones.review }}</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-gray-300"></span> Backlog {{ dash.projectDash.milestones.backlog }}</span>
        </div>
      </div>

      <!-- Tab nav -->
      <div class="flex flex-wrap gap-2">
        <RouterLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          class="btn-secondary"
        >
          {{ tab.label }}
        </RouterLink>
      </div>
    </template>
  </div>
</template>
