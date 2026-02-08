import { ref, onMounted, onUnmounted } from 'vue'

export function useDebounce(fn, delay = 300) {
  let timer = null
  
  const debouncedFn = (...args) => {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn(...args)
    }, delay)
  }
  
  const cancel = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }
  
  onUnmounted(cancel)
  
  return {
    debouncedFn,
    cancel
  }
}

export function useThrottle(fn, delay = 300) {
  let lastTime = 0
  
  const throttledFn = (...args) => {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn(...args)
      lastTime = now
    }
  }
  
  return throttledFn
}

export function useClickOutside(targetRef, callback) {
  const isClickOutside = ref(false)
  
  const handleClick = (event) => {
    if (targetRef.value) {
      isClickOutside.value = !targetRef.value.contains(event.target)
      if (isClickOutside.value) {
        callback(event)
      }
    }
  }
  
  onMounted(() => {
    document.addEventListener('click', handleClick)
  })
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClick)
  })
  
  return {
    isClickOutside
  }
}

export function useCopyToClipboard() {
  const copied = ref(false)
  
  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
      return true
    } catch (error) {
      console.error('复制失败:', error)
      return false
    }
  }
  
  return {
    copied,
    copy
  }
}

export function useLocalStorage() {
  const get = (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.error('读取 localStorage 失败:', error)
      return defaultValue
    }
  }
  
  const set = (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('写入 localStorage 失败:', error)
      return false
    }
  }
  
  const remove = (key) => {
    try {
      localStorage.removeItem(key)
      return true
    } catch (error) {
      console.error('删除 localStorage 失败:', error)
      return false
    }
  }
  
  return {
    get,
    set,
    remove
  }
}

export function useNumberFormat() {
  const format = (num, decimals = 2) => {
    if (num === null || num === undefined) return '-'
    
    if (num >= 100000000) {
      return (num / 100000000).toFixed(decimals) + '亿'
    }
    if (num >= 10000) {
      return (num / 10000).toFixed(decimals) + '万'
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(decimals) + 'k'
    }
    
    return num.toLocaleString()
  }
  
  const formatPercent = (value, decimals = 2) => {
    if (value === null || value === undefined) return '-%'
    return (value * 100).toFixed(decimals) + '%'
  }
  
  return {
    format,
    formatPercent
  }
}

export function useDateFormat() {
  const format = (date, pattern = 'YYYY-MM-DD HH:mm:ss') => {
    if (!date) return '-'
    
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hour = String(d.getHours()).padStart(2, '0')
    const minute = String(d.getMinutes()).padStart(2, '0')
    const second = String(d.getSeconds()).padStart(2, '0')
    
    return pattern
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hour)
      .replace('mm', minute)
      .replace('ss', second)
  }
  
  const formatRelative = (date) => {
    if (!date) return '-'
    
    const now = new Date()
    const target = new Date(date)
    const diff = now - target
    
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    if (seconds < 60) {
      return '刚刚'
    }
    if (minutes < 60) {
      return `${minutes}分钟前`
    }
    if (hours < 24) {
      return `${hours}小时前`
    }
    if (days < 7) {
      return `${days}天前`
    }
    
    return format(date, 'YYYY-MM-DD')
  }
  
  return {
    format,
    formatRelative
  }
}
