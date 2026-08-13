<script setup>
import StatusBadge from '../shared/StatusBadge.vue'

defineProps({ risk: Object })
defineEmits(['updated'])

const classColors = {
  critical: 'border-l-red-500',
  high: 'border-l-orange-500',
  medium: 'border-l-yellow-500',
  low: 'border-l-green-500',
}
</script>

<template>
  <div :class="['card border-l-4', classColors[risk.classification] || 'border-l-gray-300']">
    <div class="flex items-start justify-between mb-2">
      <div>
        <h4 class="font-medium text-gray-800">{{ risk.title }}</h4>
        <p class="text-xs text-gray-500 mt-0.5">{{ risk.category }} &middot; Score: {{ risk.risk_score }}</p>
      </div>
      <div class="flex items-center gap-2">
        <StatusBadge :status="risk.classification" />
        <StatusBadge :status="risk.status" />
      </div>
    </div>
    <p v-if="risk.description" class="text-sm text-gray-600 mb-2">{{ risk.description }}</p>
    <div v-if="risk.mitigation_plan" class="bg-gray-50 p-3 rounded-lg text-sm text-gray-600">
      <span class="font-medium text-gray-700">Mitigation: </span>{{ risk.mitigation_plan }}
    </div>
    <div class="flex items-center justify-between mt-3 text-xs text-gray-400">
      <span>{{ risk.probability?.replace('_', ' ') }} × {{ risk.impact }}</span>
      <span>{{ risk.owner_email }}</span>
    </div>
  </div>
</template>
