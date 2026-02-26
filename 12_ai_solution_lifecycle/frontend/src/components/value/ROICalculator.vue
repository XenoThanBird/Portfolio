<script setup>
import { ref } from 'vue'
import { useValueStore } from '../../stores/value'

const props = defineProps({ projectId: String })
const store = useValueStore()

const form = ref({
  total_benefits: 5.0,
  total_costs: 2.5,
  time_horizon_years: 3,
  discount_rate: 0.08,
})

async function calculate() {
  await store.calculateRoi(props.projectId, form.value)
}
</script>

<template>
  <div class="card">
    <h3 class="font-semibold text-gray-800 mb-4">ROI Calculator</h3>

    <form @submit.prevent="calculate" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div>
        <label class="label">Benefits ($M)</label>
        <input v-model.number="form.total_benefits" type="number" step="0.1" class="input" />
      </div>
      <div>
        <label class="label">Costs ($M)</label>
        <input v-model.number="form.total_costs" type="number" step="0.1" class="input" />
      </div>
      <div>
        <label class="label">Time Horizon (yr)</label>
        <input v-model.number="form.time_horizon_years" type="number" min="1" max="10" class="input" />
      </div>
      <div>
        <label class="label">Discount Rate</label>
        <input v-model.number="form.discount_rate" type="number" step="0.01" min="0" max="1" class="input" />
      </div>
      <div class="col-span-full">
        <button type="submit" class="btn-primary">Calculate ROI</button>
      </div>
    </form>

    <div v-if="store.roi" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="text-center p-4 bg-green-50 rounded-lg">
        <p class="text-2xl font-bold text-green-600">{{ store.roi.roi_percent }}%</p>
        <p class="text-xs text-gray-500">ROI</p>
      </div>
      <div class="text-center p-4 bg-blue-50 rounded-lg">
        <p class="text-2xl font-bold text-blue-600">${{ store.roi.npv_millions }}M</p>
        <p class="text-xs text-gray-500">NPV</p>
      </div>
      <div class="text-center p-4 bg-purple-50 rounded-lg">
        <p class="text-2xl font-bold text-purple-600">{{ store.roi.payback_years }}yr</p>
        <p class="text-xs text-gray-500">Payback</p>
      </div>
      <div class="text-center p-4 bg-yellow-50 rounded-lg">
        <p class="text-2xl font-bold text-yellow-600">{{ store.roi.risk_adjusted_roi }}%</p>
        <p class="text-xs text-gray-500">Risk-Adjusted ROI</p>
      </div>
    </div>
  </div>
</template>
