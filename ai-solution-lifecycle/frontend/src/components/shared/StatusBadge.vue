<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const colors = {
  active: 'bg-green-100 text-green-800',
  planning: 'bg-blue-100 text-blue-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  archived: 'bg-gray-100 text-gray-800',
  done: 'bg-green-100 text-green-800',
  in_progress: 'bg-blue-100 text-blue-800',
  backlog: 'bg-gray-100 text-gray-600',
  review: 'bg-purple-100 text-purple-800',
  open: 'bg-red-100 text-red-800',
  mitigated: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-600',
  approved: 'bg-green-100 text-green-800',
  draft: 'bg-yellow-100 text-yellow-800',
  submitted: 'bg-blue-100 text-blue-800',
  under_review: 'bg-purple-100 text-purple-800',
  rejected: 'bg-red-100 text-red-800',
  implemented: 'bg-green-100 text-green-800',
  critical: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
  high: 'bg-red-100 text-red-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-green-100 text-green-800',
}

const colorClass = computed(() => colors[props.status] || 'bg-gray-100 text-gray-700')
const label = computed(() => props.status.replace(/_/g, ' '))
</script>

<template>
  <span class="badge capitalize" :class="colorClass">{{ label }}</span>
</template>
