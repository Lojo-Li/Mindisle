// 用户状态管理
import { getUserInfo, login, logout, register } from '@/api/auth'
import { defineStore } from 'pinia'

// 仅使用 sessionStorage，实现标签页完全隔离
const getStorage = (key, defaultValue = '') => {
  try {
    return sessionStorage.getItem(key) ?? defaultValue
  } catch {
    return defaultValue
  }
}

const setStorage = (key, value) => {
  try {
    sessionStorage.setItem(key, value)
  } catch (e) {
    console.error('Storage error:', e)
  }
}

const removeStorage = (key) => {
  try {
    sessionStorage.removeItem(key)
  } catch (e) {
    console.error('Storage error:', e)
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getStorage('token'),
    userInfo: JSON.parse(getStorage('userInfo', 'null')),
    isLoggedIn: !!getStorage('token')
  }),

  getters: {
    // 用户角色
    userRole: (state) => state.userInfo?.role || 'user',

    // 用户昵称
    nickname: (state) => state.userInfo?.nickname || '未登录',

    // 用户头像
    avatar: (state) => state.userInfo?.avatar || '',

    // 是否是咨询师
    isCounselor: (state) => state.userInfo?.role === 'counselor',

    // 是否是管理员
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },

  actions: {
    // 设置token
    setToken(token) {
      this.token = token
      this.isLoggedIn = !!token
      if (token) {
        setStorage('token', token)
      } else {
        removeStorage('token')
      }
    },

    // 设置用户信息
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      if (userInfo) {
        setStorage('userInfo', JSON.stringify(userInfo))
        setStorage('userRole', userInfo.role || 'user')
      } else {
        removeStorage('userInfo')
        removeStorage('userRole')
      }
    },

    // 登录
    async login(loginData) {
      try {
        const res = await login(loginData)
        this.setToken(res.data.token)
        this.setUserInfo(res.data.userInfo)

        return res.data
      } catch (error) {
        throw error
      }
    },

    // 注册
    async register(registerData) {
      try {
        const res = await register(registerData)
        // 注册后自动登录
        this.setToken(res.data.token)
        this.setUserInfo(res.data.userInfo)
        return res
      } catch (error) {
        throw error
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        const res = await getUserInfo()
        this.setUserInfo(res.data)
        return res
      } catch (error) {
        throw error
      }
    },

    // 退出登录
    async logout() {
      try {
        await logout()
      } catch (error) {
        console.error('退出登录失败:', error)
      } finally {
        // 清除所有sessionStorage数据
        sessionStorage.clear()
        // 清除状态
        this.token = ''
        this.userInfo = null
        this.isLoggedIn = false
        // 跳转到登录页并强制刷新，避免缓存问题
        window.location.href = '/login?t=' + Date.now()
      }
    }
  }
})
