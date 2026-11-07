// API 请求封装
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 仅从 sessionStorage 获取 token（标签页隔离）
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data

    // 如果响应码不是200，视为错误
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')

      // 401: 未登录或token过期
      if (res.code === 401) {
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('userInfo')
        window.location.href = '/login'
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  error => {
    console.error('响应错误:', error)

    // 处理网络错误
    if (error.response) {
      const errorData = error.response.data
      // 提取错误信息，支持多种格式
      const errorMessage = errorData?.detail || errorData?.message || errorData?.error || '请求失败'

      switch (error.response.status) {
        case 400:
          // 400错误显示后端返回的具体错误信息
          ElMessage.error(errorMessage)
          break
        case 401:
          // 显示后端返回的具体错误信息（如"邮箱或密码错误"）
          ElMessage.error(errorMessage)
          // 不在登录页时再跳转登录页，避免登录失败也被重定向
          if (!window.location.pathname.includes('/login')) {
            sessionStorage.removeItem('token')
            sessionStorage.removeItem('userInfo')
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error(errorMessage || '没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          // 422错误通常是参数验证失败
          ElMessage.error(errorMessage || '请求参数错误')
          break
        case 500:
          ElMessage.error(errorMessage || '服务器错误')
          break
        default:
          ElMessage.error(errorMessage)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
