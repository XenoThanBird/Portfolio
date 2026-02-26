<script setup>
import { computed } from 'vue'

const props = defineProps({ data: Object })
const emit = defineEmits(['cell-click'])

const roleColors = {
  R: 'bg-blue-500 text-white',
  A: 'bg-red-500 text-white',
  C: 'bg-yellow-400 text-yellow-900',
  I: 'bg-green-400 text-green-900',
}

function getRole(deliverable, person) {
  if (!props.data?.matrix?.[deliverable]) return ''
  return props.data.matrix[deliverable][person] || ''
}
</script>

<template>
  <div class="card overflow-x-auto">
    <table class="min-w-full">
      <thead>
        <tr>
          <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase bg-gray-50">Deliverable</th>
          <th v-for="person in data.people" :key="person" class="px-3 py-2 text-center text-xs font-medium text-gray-500 bg-gray-50 min-w-[100px]">
            {{ person.split('@')[0] }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="del in data.deliverables" :key="del" class="border-t border-gray-100">
          <td class="px-3 py-2 text-sm font-medium text-gray-700">{{ del }}</td>
          <td
            v-for="person in data.people"
            :key="person"
            class="px-3 py-2 text-center cursor-pointer hover:bg-gray-50"
            @click="emit('cell-click', del, person, getRole(del, person))"
          >
            <span v-if="getRole(del, person)" :class="['inline-flex w-8 h-8 items-center justify-center rounded-full text-sm font-bold', roleColors[getRole(del, person)]]">
              {{ getRole(del, person) }}
            </span>
            <span v-else class="inline-flex w-8 h-8 items-center justify-center rounded-full text-gray-300 border border-dashed border-gray-300 text-xs">+</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="flex gap-4 mt-4 text-xs text-gray-500">
      <span class="flex items-center gap-1"><span class="w-5 h-5 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold">R</span> Responsible</span>
      <span class="flex items-center gap-1"><span class="w-5 h-5 rounded-full bg-red-500 text-white flex items-center justify-center text-xs font-bold">A</span> Accountable</span>
      <span class="flex items-center gap-1"><span class="w-5 h-5 rounded-full bg-yellow-400 text-yellow-900 flex items-center justify-center text-xs font-bold">C</span> Consulted</span>
      <span class="flex items-center gap-1"><span class="w-5 h-5 rounded-full bg-green-400 text-green-900 flex items-center justify-center text-xs font-bold">I</span> Informed</span>
    </div>
  </div>
</template>
