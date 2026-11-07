// 格式化工具函数
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

/**
 * 格式化相对时间
 * @param {string|Date} timestamp - 时间戳
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(timestamp) {
  return dayjs(timestamp).fromNow()
}

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期
 * @param {string} format - 格式化模板
 * @returns {string} 格式化后的日期
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @returns {string} 格式化后的日期
 */
export function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param {string|Date} date - 日期
 * @returns {string} 格式化后的时间
 */
export function formatTime(date) {
  return dayjs(date).format('HH:mm:ss')
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 截断文本
 * @param {string} text - 文本
 * @param {number} length - 最大长度
 * @param {string} suffix - 后缀
 * @returns {string} 截断后的文本
 */
export function truncateText(text, length = 100, suffix = '...') {
  if (text.length <= length) return text
  return text.substring(0, length) + suffix
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间
 * @returns {Function} 节流后的函数
 */
export function throttle(func, wait = 300) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), wait)
    }
  }
}
