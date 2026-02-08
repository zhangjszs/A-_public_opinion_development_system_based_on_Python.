<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

onMounted(() => {
  const savedTheme = localStorage.getItem('weibo_theme') || 'light'
  appStore.setTheme(savedTheme)
})
</script>
