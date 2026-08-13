<script setup>
defineProps({
  label: String,
  value: [String, Number],
  sublabel: { type: String, default: '' },
  color: { type: String, default: 'primary' },
})
const colors = {
  primary: 'bg-primary-50 text-primary-700',
  success: 'bg-green-50 text-green-700',
  warning: 'bg-yellow-50 text-yellow-700',
  danger: 'bg-red-50 text-red-700',
}
</script>

<template>
  <div class="card flex items-center gap-4">
    <div :class="['w-12 h-12 rounded-lg flex items-center justify-center text-lg font-bold', colors[color]]">
      {{ typeof value === 'number' && value > 99 ? '99+' : value }}
    </div>
    <div>
      <p class="text-2xl font-bold text-gray-900">{{ value }}</p>
      <p class="text-sm text-gray-500">{{ label }}</p>
      <p v-if="sublabel" class="text-xs text-gray-400">{{ sublabel }}</p>
    </div>
  </div>
</template>
