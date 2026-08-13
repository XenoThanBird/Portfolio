<script setup>
import Modal from './Modal.vue'

defineProps({
  show: Boolean,
  title: { type: String, default: 'Confirm' },
  message: { type: String, default: 'Are you sure?' },
  confirmText: { type: String, default: 'Confirm' },
  confirmClass: { type: String, default: 'btn-danger' },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Modal :show="show" :title="title" @close="emit('cancel')">
    <p class="text-sm text-gray-600">{{ message }}</p>
    <template #footer>
      <div class="flex justify-end gap-3">
        <button class="btn-secondary" @click="emit('cancel')">Cancel</button>
        <button :class="confirmClass" @click="emit('confirm')">{{ confirmText }}</button>
      </div>
    </template>
  </Modal>
</template>
