<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const appStore = useAppStore()
const userStore = useUserStore()

onMounted(() => {
  const savedTheme = localStorage.getItem('weibo_theme') || 'light'
  appStore.setTheme(savedTheme)
  userStore.initAuth()
})
</script>
