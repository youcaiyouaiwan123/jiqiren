<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(async () => {
  if (!auth.token) return
  try {
    await auth.fetchProfile()
  } catch {
    auth.logout()
  }
})
</script>

<template>
  <RouterView />
</template>
