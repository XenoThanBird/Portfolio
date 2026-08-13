<script setup>
defineProps({
  show: Boolean,
  title: { type: String, default: '' },
  maxWidth: { type: String, default: 'max-w-lg' },
})
const emit = defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="emit('close')"></div>
        <div :class="['relative bg-white rounded-xl shadow-2xl w-full mx-4', maxWidth]">
          <div v-if="title" class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold">{{ title }}</h3>
            <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
          <div class="p-6">
            <slot />
          </div>
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
