import axios from 'axios'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import router from '@/router'

// 加载状态管理
let loadingInstance = null
let loadingCount = 0

const showLoading = (options = {}) => {
  if (loadingCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: options.text || '加载中...',
      background: 'rgba(0, 0, 0, 0.7)',
      ...options
    })
  }
  loadingCount++
}

const hideLoading = () => {
  if (loadingCount > 0) {
    loadingCount--
  }
  if (loadingCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

const request = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('weibo_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 显示加载动画（如果配置中未禁用）
    if (!config.hideLoading) {
      showLoading(config.loadingOptions)
    }
    
    return config
  },
  (error) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    hideLoading()
    const res = response.data
    
    if (res.code === 200) {
      return res
    } else {
      // 业务错误处理
      const errorMsg = res.msg || '请求失败'
      
      // 根据错误码处理
      switch (res.code) {
        case 401:
          ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            localStorage.removeItem('weibo_token')
            localStorage.removeItem('weibo_user')
            router.push('/login')
          })
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
        default:
          ElMessage.error(errorMsg)
      }
      
      return Promise.reject(new Error(errorMsg))
    }
  },
  (error) => {
    hideLoading()
    
    // 网络错误处理
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            localStorage.removeItem('weibo_token')
            localStorage.removeItem('weibo_user')
            router.push('/login')
          })
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 408:
          ElMessage.error('请求超时，请检查网络连接')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        case 502:
          ElMessage.error('网关错误，请稍后重试')
          break
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          ElMessage.error(data?.msg || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请检查网络连接')
      } else {
        ElMessage.error('网络错误，请检查网络连接')
      }
    } else {
      // 请求配置错误
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 封装请求方法
export const http = {
  get(url, config = {}) {
    return request.get(url, config)
  },
  
  post(url, data, config = {}) {
    return request.post(url, data, config)
  },
  
  put(url, data, config = {}) {
    return request.put(url, data, config)
  },
  
  delete(url, config = {}) {
    return request.delete(url, config)
  },
  
  // 带加载提示的请求
  request(config) {
    return request(config)
  }
}

export default request
