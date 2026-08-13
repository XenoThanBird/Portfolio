<script setup>
defineProps({ data: Object })

const probLabels = ['almost_certain', 'likely', 'possible', 'unlikely', 'rare']
const impactLabels = ['negligible', 'minor', 'moderate', 'major', 'catastrophic']

function cellColor(prob, impact) {
  const pIdx = probLabels.indexOf(prob)
  const iIdx = impactLabels.indexOf(impact)
  const score = (probLabels.length - pIdx) * (iIdx + 1)
  if (score >= 15) return 'bg-red-500 text-white'
  if (score >= 10) return 'bg-orange-400 text-white'
  if (score >= 5) return 'bg-yellow-300 text-yellow-900'
  return 'bg-green-200 text-green-800'
}
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold text-gray-700">Risk Matrix ({{ data.total_risks }} open risks)</h3>
      <span class="text-sm text-gray-500">Avg Score: {{ data.avg_score }}</span>
    </div>
    <div class="overflow-x-auto">
      <table class="min-w-full">
        <thead>
          <tr>
            <th class="px-2 py-1 text-xs text-gray-500"></th>
            <th v-for="imp in impactLabels" :key="imp" class="px-2 py-1 text-xs text-gray-500 capitalize text-center">{{ imp }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prob in probLabels" :key="prob">
            <td class="px-2 py-1 text-xs text-gray-500 capitalize whitespace-nowrap">{{ prob.replace('_', ' ') }}</td>
            <td v-for="imp in impactLabels" :key="imp" class="px-1 py-1 text-center">
              <div :class="['w-10 h-10 rounded flex items-center justify-center text-sm font-bold mx-auto', cellColor(prob, imp)]">
                {{ data.matrix?.[prob]?.[imp] || 0 }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="flex items-center justify-between mt-3 text-xs text-gray-400">
      <span>&larr; Impact &rarr;</span>
      <span>&uarr; Probability</span>
    </div>
  </div>
</template>
