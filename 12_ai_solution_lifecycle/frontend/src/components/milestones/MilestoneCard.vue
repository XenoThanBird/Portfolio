<script setup>
import { computed } from 'vue'
import StatusBadge from '../shared/StatusBadge.vue'

const props = defineProps({ milestone: Object, currentStatus: String })
const emit = defineEmits(['move'])

const priorityColors = {
  critical: 'border-l-red-500',
  high: 'border-l-orange-500',
  medium: 'border-l-yellow-500',
  low: 'border-l-green-500',
}

const statusFlow = ['backlog', 'in_progress', 'review', 'done']

const canMoveRight = computed(() => {
  const idx = statusFlow.indexOf(props.currentStatus)
  return idx < statusFlow.length - 1
})

const canMoveLeft = computed(() => {
  const idx = statusFlow.indexOf(props.currentStatus)
  return idx > 0
})

const isOverdue = computed(() => {
  if (!props.milestone.due_date || props.currentStatus === 'done') return false
  return new Date(props.milestone.due_date) < new Date()
})
</script>

<template>
  <div :class="['bg-white rounded-lg p-3 shadow-sm border-l-4', priorityColors[milestone.priority] || 'border-l-gray-300']">
    <h4 class="text-sm font-medium text-gray-800 mb-1">{{ milestone.title }}</h4>
    <div class="flex items-center gap-2 mb-2">
      <StatusBadge :status="milestone.priority" />
      <span v-if="isOverdue" class="badge bg-red-100 text-red-700">Overdue</span>
    </div>
    <div class="flex items-center justify-between text-xs text-gray-400">
      <span>{{ milestone.owner_email }}</span>
      <span v-if="milestone.due_date">{{ new Date(milestone.due_date).toLocaleDateString() }}</span>
    </div>
    <div class="flex gap-1 mt-2">
      <button v-if="canMoveLeft" @click="emit('move', statusFlow[statusFlow.indexOf(currentStatus) - 1])" class="btn-sm btn-secondary text-xs flex-1">&larr;</button>
      <button v-if="canMoveRight" @click="emit('move', statusFlow[statusFlow.indexOf(currentStatus) + 1])" class="btn-sm btn-primary text-xs flex-1">&rarr;</button>
    </div>
  </div>
</template>
