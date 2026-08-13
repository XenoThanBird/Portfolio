<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('admin@demo.com')
const password = ref('demo')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally { loading.value = false }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-primary-900">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-white">AI Solution Lifecycle</h1>
        <p class="text-gray-400 mt-2">Platform Login</p>
      </div>
      <form @submit.prevent="handleLogin" class="card space-y-5">
        <div>
          <label class="label">Email</label>
          <input v-model="email" type="email" class="input" placeholder="name@demo.com" required />
        </div>
        <div>
          <label class="label">Password</label>
          <input v-model="password" type="password" class="input" placeholder="Any password" required />
        </div>
        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <p class="text-xs text-center text-gray-400">Demo: use any @demo.com email</p>
      </form>
    </div>
  </div>
</template>
