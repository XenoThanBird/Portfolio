<script setup>
defineProps({
  role: { type: String, default: '' },
})

const colors = {
  R: 'bg-blue-500 text-white',
  A: 'bg-red-500 text-white',
  C: 'bg-yellow-400 text-yellow-900',
  I: 'bg-green-400 text-green-900',
}
</script>

<template>
  <span v-if="role" :class="['inline-flex w-8 h-8 items-center justify-center rounded-full text-sm font-bold', colors[role]]">
    {{ role }}
  </span>
</template>
