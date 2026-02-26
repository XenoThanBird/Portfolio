<script setup>
import MilestoneCard from './MilestoneCard.vue'

defineProps({
  title: String,
  color: String,
  items: { type: Array, default: () => [] },
  status: String,
})
defineEmits(['move'])
</script>

<template>
  <div class="bg-gray-50 rounded-xl p-4 min-h-[400px]">
    <div class="flex items-center gap-2 mb-4">
      <div :class="['w-3 h-3 rounded-full', color]"></div>
      <h3 class="text-sm font-semibold text-gray-700">{{ title }}</h3>
      <span class="badge bg-gray-200 text-gray-600">{{ items.length }}</span>
    </div>
    <div class="space-y-3">
      <MilestoneCard
        v-for="item in items"
        :key="item.id"
        :milestone="item"
        :current-status="status"
        @move="(newStatus) => $emit('move', item.id, newStatus)"
      />
    </div>
    <p v-if="!items.length" class="text-xs text-gray-400 text-center py-8">No items</p>
  </div>
</template>
