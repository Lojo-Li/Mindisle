// API 请求封装
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
// 默认走相对路径 /api，由 Vite devServer 代理到后端 8000 端口，
// 这样可避免跨域问题，也便于团队协作时统一入口。
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
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

/**
 * A 线维护的公共错误契约（G8）：
 * 后端成功响应为 {code:200, message, data}，失败响应由 api_contract 统一为
 * {code, message, data:null, detail} 且 HTTP 状态码为 4xx/5xx。
 * 这里把「HTTP 层」与「body 层」两条错误路径归一成同一个错误对象，
 * 保证 B/C/D/E 的 catch 拿到一致的 {message, code, status, raw}。
 */
function createApiError(message, code, status, raw, original) {
  const err = new Error(message || '请求失败')
  err.code = code
  err.status = status
  err.raw = raw
  // 向后兼容：部分业务线仍在 catch 中读取 axios 原生字段
  // （如 error.response.data.detail），原样挂载避免其错误提示退化。
  if (original) {
    err.response = original.response
    err.request = original.request
    err.config = original.config
  }
  return err
}

function pickMessage(raw, fallback = '请求失败') {
  const value = raw?.message ?? raw?.detail ?? raw?.error
  if (typeof value === 'string' && value) return value
  if (value && typeof value === 'object' && typeof value.message === 'string') return value.message
  return fallback
}

// 401 = 未认证（清登录态并跳登录页）；403 = 已登录但无权（只提示，不清态、不跳转）
function handleAuthError(code, status) {
  if (code === 401 || status === 401) {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userInfo')
    const path = window.location.pathname
    // 根路径与 /login 均为登录页，避免登录失败时被重复重定向
    if (path !== '/' && !path.includes('/login')) {
      window.location.href = '/login'
    }
  }
}

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data

    // 仅当响应体显式带 code 字段时才按业务码判定；
    // 无 code 的裸数据响应（部分模块既有接口）一律视为成功，避免误报。
    const hasBizCode = res && typeof res === 'object' && !Array.isArray(res)
      && Object.prototype.hasOwnProperty.call(res, 'code')

    if (hasBizCode && res.code !== 200) {
      const message = pickMessage(res)
      ElMessage.error(message)
      handleAuthError(res.code, response.status)
      return Promise.reject(createApiError(message, res.code, response.status, res))
    }

    return res
  },
  error => {
    const status = error.response?.status
    const raw = error.response?.data
    // 新契约为 body.code，旧接口只有 detail，用 HTTP 状态码兜底
    const code = (raw && typeof raw === 'object' && typeof raw.code === 'number')
      ? raw.code
      : status
    let message = pickMessage(raw)

    if (error.response) {
      switch (status) {
        case 400:
          // 400 显示后端返回的具体错误信息
          ElMessage.error(message)
          break
        case 401:
          // /admin/login 的 401 由登录页区分「入口不匹配」与「账号密码错误」后自行提示，
          // 避免全局拦截器与页面各弹一次
          if (!error.config?.url?.includes('/admin/login')) ElMessage.error(message)
          handleAuthError(code, status)
          break
        case 403:
          ElMessage.error(message === '请求失败' ? '没有权限访问' : message)
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          ElMessage.error(message === '请求失败' ? '请求参数错误' : message)
          break
        case 500:
          ElMessage.error(message === '请求失败' ? '服务器错误' : message)
          break
        default:
          ElMessage.error(message)
      }
    } else if (error.request) {
      // 区分「真的连不上」和「连上了但服务器太久没回」
      const isTimeout = error.code === 'ECONNABORTED' || /timeout/i.test(error.message || '')
      message = isTimeout
        ? '请求超时，服务器处理较慢，请稍后重试'
        : '无法连接服务，请确认后端已启动'
      ElMessage.error(message)
    } else {
      message = error.message || '请求配置错误'
      ElMessage.error(message)
    }

    return Promise.reject(createApiError(message, code, status, raw ?? error.message, error))
  }
)

export default request
