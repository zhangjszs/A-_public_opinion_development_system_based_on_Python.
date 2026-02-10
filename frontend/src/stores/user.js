import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('weibo_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('weibo_user') || '{}'))

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')
  const isAdmin = computed(() => userInfo.value?.is_admin === true)

  async function doLogin(username, password) {
    try {
      const res = await login(username, password)
      if (res.code === 200) {
        token.value = res.data.token
        userInfo.value = res.data.user
        localStorage.setItem('weibo_token', token.value)
        localStorage.setItem('weibo_user', JSON.stringify(userInfo.value))
        return { success: true }
      }
      return { success: false, msg: res.msg }
    } catch (error) {
      return { success: false, msg: error.message }
    }
  }

  async function doLogout() {
    try {
      await logout()
    } catch (error) {
      console.error('登出请求失败', error)
    } finally {
      token.value = ''
      userInfo.value = {}
      localStorage.removeItem('weibo_token')
      localStorage.removeItem('weibo_user')
      router.push('/login')
    }
  }

  async function initAuth() {
    if (!token.value) return
    try {
      const res = await getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        localStorage.setItem('weibo_user', JSON.stringify(userInfo.value))
        return
      }
    } catch (e) {
      token.value = ''
      userInfo.value = {}
      localStorage.removeItem('weibo_token')
      localStorage.removeItem('weibo_user')
      const target = router.currentRoute?.value?.fullPath || '/home'
      router.replace(`/login?redirect=${encodeURIComponent(target)}`)
    }
  }

  function updateUserInfo(info) {
    userInfo.value = { ...userInfo.value, ...info }
    localStorage.setItem('weibo_user', JSON.stringify(userInfo.value))
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    username,
    isAdmin,
    doLogin,
    doLogout,
    initAuth,
    updateUserInfo
  }
})
