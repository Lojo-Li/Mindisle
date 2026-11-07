// 个人中心相关API
import request from './index'

/**
 * 获取用户信息
 */
export function getUserProfile() {
  return request({
    url: '/user/profile',
    method: 'get'
  })
}

/**
 * 更新用户信息
 * @param {Object} data
 * @param {string} data.nickname - 昵称
 * @param {string} data.phone - 手机号
 * @param {Date} data.birthDate - 出生日期
 * @param {string} data.gender - 性别
 * @param {string} data.bio - 个人简介
 */
export function updateUserProfile(data) {
  return request({
    url: '/user/profile',
    method: 'put',
    data
  })
}

/**
 * 上传头像
 * @param {File} file - 头像文件
 */
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/user/avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取隐私设置
 */
export function getPrivacySettings() {
  return request({
    url: '/user/privacy',
    method: 'get'
  })
}

/**
 * 更新隐私设置
 * @param {Object} data
 * @param {boolean} data.saveChatHistory - 保存对话历史
 * @param {boolean} data.allowAIAnalysis - 允许AI分析对话
 * @param {boolean} data.chatOnlyVisible - 对话仅自己可见
 * @param {boolean} data.saveTestRecords - 保存测试记录
 * @param {boolean} data.testOnlyVisible - 测试结果仅自己可见
 * @param {boolean} data.allowTrendAnalysis - 允许查看趋势分析
 */
export function updatePrivacySettings(data) {
  return request({
    url: '/user/privacy',
    method: 'put',
    data
  })
}

/**
 * 清除对话记录
 */
export function clearChatHistory() {
  return request({
    url: '/user/chat-history',
    method: 'delete'
  })
}

/**
 * 清除测试记录
 */
export function clearTestRecords() {
  return request({
    url: '/user/test-records',
    method: 'delete'
  })
}

/**
 * 获取用户数据统计
 * @param {Object} params
 * @param {string} params.timeRange - 时间范围（可选）
 */
export function getUserStatistics(params) {
  return request({
    url: '/user/statistics',
    method: 'get',
    params
  })
}

/**
 * 获取活动趋势数据
 * @param {Object} params
 * @param {string} params.timeRange - 时间范围
 */
export function getActivityTrend(params) {
  return request({
    url: '/user/activity-trend',
    method: 'get',
    params
  })
}

/**
 * 获取测试分类分布
 */
export function getTestDistribution() {
  return request({
    url: '/user/test-distribution',
    method: 'get'
  })
}

/**
 * 获取对话主题分布
 */
export function getChatDistribution() {
  return request({
    url: '/user/chat-distribution',
    method: 'get'
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/user/change-password',
    method: 'post',
    data
  })
}

/**
 * 注销账户
 * ⚠️ 危险操作：永久删除账户和所有相关数据
 */
export function deleteAccount() {
  return request({
    url: '/user/delete-account',
    method: 'post',
    data: {}
  })
}
