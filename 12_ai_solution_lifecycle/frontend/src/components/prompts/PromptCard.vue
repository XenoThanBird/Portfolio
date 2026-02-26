<script setup>
defineProps({ prompt: Object })
defineEmits(['edit', 'use'])
</script>

<template>
  <div class="card hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between mb-2">
      <h3 class="font-medium text-gray-800">{{ prompt.name }}</h3>
      <span class="badge bg-primary-100 text-primary-700">v{{ prompt.version }}</span>
    </div>
    <p class="text-xs text-gray-500 mb-3 line-clamp-2 font-mono">{{ prompt.template }}</p>
    <div class="flex flex-wrap gap-1 mb-3">
      <span v-for="tag in (prompt.tags || [])" :key="tag" class="badge bg-gray-100 text-gray-600">{{ tag }}</span>
    </div>
    <div class="flex items-center justify-between text-xs text-gray-400 mb-3">
      <span>{{ prompt.usage_count || 0 }} runs</span>
      <span>{{ prompt.avg_latency_ms || 0 }}ms avg</span>
      <span>{{ Math.round((prompt.success_rate || 0) * 100) }}% success</span>
    </div>
    <div class="flex gap-2">
      <button @click="$emit('use')" class="btn-sm btn-primary flex-1">Use</button>
      <button @click="$emit('edit')" class="btn-sm btn-secondary flex-1">Edit</button>
    </div>
  </div>
</template>
