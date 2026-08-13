<script setup>
import { computed } from 'vue'

const props = defineProps({
  avgScore: { type: Number, default: 0 },
  slaCompliance: { type: Number, default: 100 },
})

const scoreColor = computed(() => {
  if (props.avgScore >= 70) return 'text-green-600'
  if (props.avgScore >= 45) return 'text-yellow-600'
  return 'text-red-600'
})

const slaColor = computed(() => {
  if (props.slaCompliance >= 95) return 'text-green-600'
  if (props.slaCompliance >= 80) return 'text-yellow-600'
  return 'text-red-600'
})
</script>

<template>
  <div class="card">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">Platform Health</h3>
    <div class="grid grid-cols-2 gap-6">
      <div class="text-center">
        <p class="text-3xl font-bold" :class="scoreColor">{{ avgScore }}</p>
        <p class="text-xs text-gray-500 mt-1">Avg Value Score</p>
      </div>
      <div class="text-center">
        <p class="text-3xl font-bold" :class="slaColor">{{ slaCompliance }}%</p>
        <p class="text-xs text-gray-500 mt-1">SLA Compliance</p>
      </div>
    </div>
  </div>
</template>
