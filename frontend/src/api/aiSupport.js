// AI 心理支持相关 API（E 线）
import request from './index'

/**
 * 查询某条 AI 回答的引用来源
 * @param {number|string} messageId
 */
export function getMessageSources(messageId) {
  return request({
    url: `/ai/sources/${messageId}`,
    method: 'get'
  })
}

/**
 * 提交答案反馈
 * @param {Object} data
 * @param {number} data.message_id
 * @param {number} data.rating  1 有用 / -1 没用
 * @param {string} [data.reason]
 */
export function submitFeedback(data) {
  return request({
    url: '/ai/feedback',
    method: 'post',
    data
  })
}

/**
 * 风险工单列表（后台）
 */
export function getRiskEvents(params) {
  return request({
    url: '/ai/risk/events',
    method: 'get',
    params
  })
}

/**
 * 处置风险事件（后台）
 */
export function handleRiskEvent(eventId, data) {
  return request({
    url: `/ai/risk/events/${eventId}`,
    method: 'put',
    data
  })
}

/**
 * 风险事件统计（后台）
 */
export function getRiskStats() {
  return request({
    url: '/ai/risk/stats',
    method: 'get'
  })
}
