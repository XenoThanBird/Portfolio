<script setup>
defineProps({
  size: { type: String, default: 'md' },
  message: { type: String, default: '' },
})
const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }
</script>

<template>
  <div class="flex flex-col items-center justify-center py-8 gap-3">
    <div :class="['animate-spin rounded-full border-2 border-gray-300 border-t-primary-600', sizes[size]]"></div>
    <p v-if="message" class="text-sm text-gray-500">{{ message }}</p>
  </div>
</template>
