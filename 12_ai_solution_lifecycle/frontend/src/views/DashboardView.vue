<script setup>
import { onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard'
import KPICard from '../components/dashboard/KPICard.vue'
import ProjectHealth from '../components/dashboard/ProjectHealth.vue'
import AlertsFeed from '../components/dashboard/AlertsFeed.vue'
import ValueChart from '../components/dashboard/ValueChart.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const dash = useDashboardStore()
onMounted(() => dash.fetchGlobal())
</script>

<template>
  <div>
    <h1 class="page-title mb-6">Dashboard</h1>

    <LoadingSpinner v-if="dash.loading" message="Loading dashboard..." />

    <template v-else-if="dash.global">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard label="Total Projects" :value="dash.global.total_projects" color="primary" />
        <KPICard label="Active Projects" :value="dash.global.active_projects" color="success" />
        <KPICard label="Open Alerts" :value="dash.global.unacknowledged_alerts" :color="dash.global.unacknowledged_alerts > 0 ? 'danger' : 'success'" />
        <KPICard label="Avg Value Score" :value="dash.global.avg_value_score" color="primary" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ProjectHealth :projects="dash.global.projects" class="lg:col-span-2" />
        <div class="space-y-6">
          <ValueChart :avg-score="dash.global.avg_value_score" :sla-compliance="dash.global.sla_compliance_pct" />
          <AlertsFeed />
        </div>
      </div>
    </template>
  </div>
</template>
