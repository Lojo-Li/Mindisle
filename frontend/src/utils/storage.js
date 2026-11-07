/**
 * 存储工具 - 标签页隔离
 * 仅使用 sessionStorage，每个标签页独立存储，互不干扰
 */

/**
 * 获取存储值
 * @param {string} key - 存储键名
 * @param {string} defaultValue - 默认值
 * @returns {string} 存储的值
 */
export function getStorage(key, defaultValue = '') {
  try {
    return sessionStorage.getItem(key) ?? defaultValue
  } catch {
    return defaultValue
  }
}

/**
 * 设置存储值
 * @param {string} key - 存储键名
 * @param {string} value - 要存储的值
 */
export function setStorage(key, value) {
  try {
    sessionStorage.setItem(key, value)
  } catch (e) {
    console.error('Storage error:', e)
  }
}

/**
 * 移除存储值
 * @param {string} key - 存储键名
 */
export function removeStorage(key) {
  try {
    sessionStorage.removeItem(key)
  } catch (e) {
    console.error('Storage error:', e)
  }
}

/**
 * 获取 token
 * @returns {string} token
 */
export function getToken() {
  return getStorage('token')
}

/**
 * 设置 token
 * @param {string} token - token 值
 */
export function setToken(token) {
  setStorage('token', token)
}

/**
 * 移除 token
 */
export function removeToken() {
  removeStorage('token')
}

/**
 * 清除所有用户相关数据
 */
export function clearUserData() {
  const keys = ['token', 'userInfo', 'userRole', 'adminToken', 'adminInfo']
  keys.forEach(key => removeStorage(key))
}
