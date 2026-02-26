<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: Boolean,
  emptyMessage: { type: String, default: 'No data found.' },
})
defineEmits(['row-click'])
</script>

<template>
  <div class="overflow-x-auto border border-gray-200 rounded-lg">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            :class="col.class"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-if="loading">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-sm text-gray-500">Loading...</td>
        </tr>
        <tr v-else-if="!rows.length">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-sm text-gray-500">{{ emptyMessage }}</td>
        </tr>
        <tr
          v-else
          v-for="(row, i) in rows"
          :key="row.id || i"
          class="hover:bg-gray-50 cursor-pointer transition-colors"
          @click="$emit('row-click', row)"
        >
          <td v-for="col in columns" :key="col.key" class="px-4 py-3 text-sm text-gray-700" :class="col.cellClass">
            <slot :name="col.key" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
