// 用户认证相关API
import request from './index'

/**
 * 发送邮箱验证码
 * @param {string} email - 邮箱地址
 * @param {string} purpose - 验证码用途（register/reset）
 */
export function sendEmailCode(email, purpose) {
  return request({
    url: '/auth/send-code',
    method: 'post',
    data: { email, purpose }
  })
}

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.email - 邮箱
 * @param {string} data.code - 验证码
 * @param {string} data.password - 密码
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 忘记密码 - 验证邮箱
 * @param {Object} data
 * @param {string} data.email - 邮箱
 * @param {string} data.code - 验证码
 */
export function verifyEmailForReset(data) {
  return request({
    url: '/auth/verify-email-reset',
    method: 'post',
    data
  })
}

/**
 * 重置密码
 * @param {Object} data
 * @param {string} data.email - 邮箱
 * @param {string} data.newPassword - 新密码
 */
export function resetPassword(data) {
  return request({
    url: '/auth/reset-password',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return request({
    url: '/auth/user-info',
    method: 'get'
  })
}

/**
 * 退出登录
 */
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}
