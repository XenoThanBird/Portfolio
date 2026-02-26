<script setup>
const props = defineProps({ assessment: Object })

const gauges = [
  { key: 'data_maturity', label: 'Data Maturity', color: 'bg-blue-500' },
  { key: 'organizational_readiness', label: 'Org Readiness', color: 'bg-purple-500' },
  { key: 'technical_capability', label: 'Tech Capability', color: 'bg-green-500' },
]
</script>

<template>
  <div class="card">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">Readiness Scores</h3>
    <div class="space-y-4">
      <div v-for="g in gauges" :key="g.key">
        <div class="flex justify-between text-sm mb-1">
          <span class="text-gray-600">{{ g.label }}</span>
          <span class="font-medium text-gray-800">{{ Math.round((assessment?.[g.key] || 0) * 100) }}%</span>
        </div>
        <div class="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
          <div :class="['h-full rounded-full transition-all', g.color]" :style="{ width: (assessment?.[g.key] || 0) * 100 + '%' }"></div>
        </div>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t border-gray-100 text-center">
      <p class="text-xs text-gray-500">Readiness Multiplier</p>
      <p class="text-xl font-bold text-gray-800">{{ assessment?.readiness_multiplier || '—' }}</p>
    </div>
  </div>
</template>
