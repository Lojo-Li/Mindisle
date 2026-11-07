// 咨询对话相关API
import request from './index'

/**
 * 获取咨询师订单列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 */
export function getCounselorOrders(params) {
  // 映射前端参数名到后端参数名
  const requestParams = {}
  if (params.status) requestParams.status_filter = params.status
  if (params.page) requestParams.page = params.page
  if (params.page_size) requestParams.page_size = params.page_size
  return request({
    url: '/consultation/counselor/orders',
    method: 'get',
    params: requestParams
  })
}

/**
 * 处理预约订单
 * @param {string} id - 订单ID
 * @param {Object} data
 * @param {string} data.action - 动作: agree/reject
 * @param {string} data.reason - 拒绝理由（可选）
 */
export function handleOrder(id, data) {
  return request({
    url: `/consultation/order/${id}/handle`,
    method: 'post',
    data
  })
}

/**
 * 获取对话消息
 * @param {string} appointmentId - 订单ID
 * @param {number} params.lastId - 最后一条消息ID（用于增量获取）
 */
export function getMessages(appointmentId, params) {
  return request({
    url: `/consultation/${appointmentId}/messages`,
    method: 'get',
    params
  })
}

/**
 * 发送消息
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {string} data.content - 消息内容
 * @param {string} data.type - 消息类型
 */
export function sendMessage(appointmentId, data) {
  return request({
    url: `/consultation/${appointmentId}/message`,
    method: 'post',
    data
  })
}

/**
 * 上传文件
 * @param {File} file - 文件
 */
export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/consultation/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 结束咨询
 * @param {string} appointmentId - 订单ID
 */
export function endConsultation(appointmentId) {
  return request({
    url: `/consultation/${appointmentId}/end`,
    method: 'post'
  })
}

/**
 * 添加咨询备注
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {string} data.note - 备注内容
 */
export function addConsultationNote(appointmentId, data) {
  return request({
    url: `/consultation/${appointmentId}/note`,
    method: 'post',
    data
  })
}

// ── WebRTC 信令消息 ─────────────────────────────────

const SIGNAL_TYPES = ['webrtc_offer', 'webrtc_answer', 'webrtc_ice', 'webrtc_hangup']

export function getSignalMessages(appointmentId, lastId) {
  return request({
    url: `/consultation/${appointmentId}/messages`,
    method: 'get',
    params: { last_id: lastId, limit: 20 }
  })
}

export function sendSignalMessage(appointmentId, messageType, content) {
  return request({
    url: `/consultation/${appointmentId}/message`,
    method: 'post',
    data: { message_type: messageType, content: JSON.stringify(content) }
  })
}

export function isSignalMessage(msg) {
  return msg && SIGNAL_TYPES.includes(msg.message_type)
}

/**
 * 检查预约是否可以进行通话（预约状态验证）
 * @param {string} appointmentId - 订单ID
 */
export function checkAppointmentCallable(appointmentId) {
  return request({
    url: `/consultation/${appointmentId}/callable`,
    method: 'get'
  })
}

export function clearSignals(appointmentId) {
  return request({
    url: `/consultation/${appointmentId}/signals`,
    method: 'delete'
  })
}
