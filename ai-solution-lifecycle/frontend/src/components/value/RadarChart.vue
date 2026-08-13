<script setup>
import { computed } from 'vue'

const props = defineProps({ assessment: Object })

const dimensions = [
  { key: 'financial_impact', label: 'Financial' },
  { key: 'operational_excellence', label: 'Operational' },
  { key: 'strategic_value', label: 'Strategic' },
  { key: 'risk_mitigation', label: 'Risk Mitigation' },
  { key: 'customer_impact', label: 'Customer' },
  { key: 'innovation_index', label: 'Innovation' },
]

const center = 100
const radius = 80

const points = computed(() => {
  return dimensions.map((dim, i) => {
    const angle = (Math.PI * 2 * i) / dimensions.length - Math.PI / 2
    const value = (props.assessment?.[dim.key] || 0) / 100
    return {
      x: center + radius * value * Math.cos(angle),
      y: center + radius * value * Math.sin(angle),
      label: dim.label,
      value: props.assessment?.[dim.key] || 0,
      labelX: center + (radius + 20) * Math.cos(angle),
      labelY: center + (radius + 20) * Math.sin(angle),
    }
  })
})

const polygonPoints = computed(() => points.value.map(p => `${p.x},${p.y}`).join(' '))

const gridLines = computed(() => [0.25, 0.5, 0.75, 1].map(scale => {
  return dimensions.map((_, i) => {
    const angle = (Math.PI * 2 * i) / dimensions.length - Math.PI / 2
    return `${center + radius * scale * Math.cos(angle)},${center + radius * scale * Math.sin(angle)}`
  }).join(' ')
}))
</script>

<template>
  <div class="card">
    <h3 class="text-sm font-semibold text-gray-700 mb-3">Value Dimensions</h3>
    <svg viewBox="0 0 200 200" class="w-full max-w-[250px] mx-auto">
      <!-- Grid -->
      <polygon v-for="(grid, i) in gridLines" :key="i" :points="grid" fill="none" stroke="#e5e7eb" stroke-width="0.5" />
      <!-- Axes -->
      <line v-for="(p, i) in points" :key="'axis-'+i" :x1="center" :y1="center" :x2="center + radius * Math.cos((Math.PI * 2 * i) / dimensions.length - Math.PI / 2)" :y2="center + radius * Math.sin((Math.PI * 2 * i) / dimensions.length - Math.PI / 2)" stroke="#e5e7eb" stroke-width="0.5" />
      <!-- Data polygon -->
      <polygon :points="polygonPoints" fill="rgba(59, 130, 246, 0.2)" stroke="#3b82f6" stroke-width="1.5" />
      <!-- Data points -->
      <circle v-for="(p, i) in points" :key="'dot-'+i" :cx="p.x" :cy="p.y" r="3" fill="#3b82f6" />
      <!-- Labels -->
      <text v-for="(p, i) in points" :key="'label-'+i" :x="p.labelX" :y="p.labelY" text-anchor="middle" dominant-baseline="middle" class="text-[6px] fill-gray-500">{{ p.label }}</text>
    </svg>
  </div>
</template>
