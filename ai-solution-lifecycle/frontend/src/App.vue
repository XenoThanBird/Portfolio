<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/layout/Sidebar.vue'
import Topbar from './components/layout/Topbar.vue'

const route = useRoute()
const isPublic = computed(() => route.meta.public)
</script>

<template>
  <div v-if="isPublic" class="min-h-screen">
    <RouterView />
  </div>
  <div v-else class="min-h-screen flex">
    <Sidebar />
    <div class="flex-1 flex flex-col ml-64">
      <Topbar />
      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
