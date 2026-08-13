<script setup>
defineProps({
  label: String,
  value: [String, Number],
  unit: { type: String, default: '' },
})
</script>

<template>
  <div class="text-center">
    <p class="text-2xl font-bold text-gray-800">{{ value }}<span v-if="unit" class="text-sm text-gray-400">{{ unit }}</span></p>
    <p class="text-xs text-gray-500">{{ label }}</p>
  </div>
</template>
