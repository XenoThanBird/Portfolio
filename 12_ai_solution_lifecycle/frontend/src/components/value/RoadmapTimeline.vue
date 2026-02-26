<script setup>
defineProps({ roadmap: Object })

const phaseColors = ['bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500']
</script>

<template>
  <div class="card">
    <h3 class="font-semibold text-gray-800 mb-2">Implementation Roadmap</h3>
    <p class="text-xs text-gray-500 mb-6">
      {{ roadmap.maturity_progression }}
      &middot; {{ roadmap.total_duration_months }} months
      &middot; ${{ roadmap.total_budget_millions }}M total
      &middot; {{ roadmap.success_probability }} success probability
    </p>

    <div class="relative">
      <!-- Timeline line -->
      <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

      <div v-for="(phase, i) in roadmap.phases" :key="i" class="relative pl-12 pb-8 last:pb-0">
        <!-- Dot -->
        <div :class="['absolute left-2.5 w-3 h-3 rounded-full ring-2 ring-white', phaseColors[i % phaseColors.length]]"></div>

        <div class="card !p-4">
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-medium text-gray-800">{{ phase.phase }}</h4>
            <span class="text-xs text-gray-500">{{ phase.duration_months }} months</span>
          </div>
          <p class="text-sm text-gray-600 mb-2">{{ phase.focus }}</p>
          <div v-if="phase.key_deliverables?.length" class="text-xs text-gray-500">
            <span class="font-medium">Deliverables: </span>
            {{ phase.key_deliverables.join(', ') }}
          </div>
          <div v-if="phase.budget_allocation" class="text-xs text-gray-400 mt-1">
            Budget: ${{ phase.budget_allocation }}M
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
