// 咨询师预约相关API
import request from './index'

/**
 * 获取咨询师列表
 * @param {Object} params - 查询参数
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.specialty - 擅长领域
 * @param {string} params.consultationType - 咨询方式
 * @param {string} params.priceMin - 最低价格
 * @param {string} params.priceMax - 最高价格
 * @param {string} params.sort - 排序方式
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getCounselorList(params) {
  return request({
    url: '/counselor/list',
    method: 'get',
    params
  })
}

/**
 * 获取咨询师详情
 * @param {string} id - 咨询师ID
 */
export function getCounselorDetail(id) {
  return request({
    url: `/counselor/${id}`,
    method: 'get'
  })
}

/**
 * 获取可预约时段
 * @param {string} counselorId - 咨询师ID
 * @param {string} date - 日期
 */
export function getAvailableSlots(counselorId, date) {
  return request({
    url: `/counselor/${counselorId}/slots`,
    method: 'get',
    params: { date }
  })
}

/**
 * 创建预约订单
 * @param {Object} data
 * @param {string} data.counselorId - 咨询师ID
 * @param {string} data.type - 咨询方式
 * @param {string} data.date - 日期
 * @param {string} data.timeSlot - 时段
 * @param {string} data.userName - 用户姓名
 * @param {string} data.contact - 联系方式
 * @param {string} data.description - 问题描述
 */
export function createAppointment(data) {
  return request({
    url: '/appointment/create',
    method: 'post',
    data
  })
}

/**
 * 获取用户预约列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 * @param {number} params.page - 页码
 */
export function getUserAppointments(params) {
  // 映射前端参数名到后端参数名
  const requestParams = {}
  if (params.status) requestParams.status_filter = params.status
  if (params.page) requestParams.page = params.page
  if (params.page_size) requestParams.page_size = params.page_size
  return request({
    url: '/appointment/user/list',
    method: 'get',
    params: requestParams
  })
}

/**
 * 获取咨询师预约列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 * @param {number} params.page - 页码
 */
export function getCounselorAppointments(params) {
  return request({
    url: '/appointment/counselor/list',
    method: 'get',
    params
  })
}

/**
 * 取消预约
 * @param {string} id - 订单ID
 */
export function cancelAppointment(id) {
  return request({
    url: `/appointment/${id}/cancel`,
    method: 'post'
  })
}

/**
 * 获取预约详情
 * @param {string} id - 订单ID
 */
export function getAppointmentDetail(id) {
  return request({
    url: `/appointment/${id}`,
    method: 'get'
  })
}

/**
 * 提交咨询评价
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {number} data.rating - 评分
 * @param {Array} data.tags - 标签
 * @param {string} data.content - 评价内容
 * @param {boolean} data.isAnonymous - 是否匿名
 */
export function submitReview(appointmentId, data) {
  return request({
    url: `/appointment/${appointmentId}/review`,
    method: 'post',
    data
  })
}

/**
 * 获取咨询师评价列表
 * @param {string} counselorId - 咨询师ID
 * @param {Object} params
 * @param {number} params.page - 页码
 */
export function getCounselorReviews(counselorId, params) {
  return request({
    url: `/counselor/${counselorId}/reviews`,
    method: 'get',
    params
  })
}

/**
 * 提交咨询师注册申请
 * @param {Object} data - 申请数据
 * @param {string} data.name - 姓名
 * @param {string} data.gender - 性别
 * @param {string} data.title - 职称
 * @param {Array} data.specialties - 擅长领域
 * @param {Array} data.consultationTypes - 咨询方式
 * @param {number} data.experienceYears - 从业年限
 * @param {string} data.education - 学历
 * @param {string} data.qualifications - 资质证书
 * @param {number} data.priceVideo - 视频咨询价格
 * @param {number} data.priceVoice - 语音咨询价格
 * @param {number} data.priceOffline - 线下咨询价格
 * @param {string} data.bio - 个人简介
 * @param {string} data.approach - 咨询流派
 * @param {string} data.achievements - 成就荣誉
 */
export function submitApplication(data) {
  // 转换字段名为后端要求的格式
  const requestData = {
    name: data.name,
    gender: data.gender,
    title: data.title || undefined,
    specialties: data.specialties,
    consultation_types: data.consultationTypes,
    experience_years: data.experienceYears,
    education: data.education,
    qualifications: data.qualifications,
    price_video: data.priceVideo || undefined,
    price_voice: data.priceVoice || undefined,
    price_offline: data.priceOffline || undefined,
    bio: data.bio,
    approach: data.approach || undefined,
    achievements: data.achievements || undefined
  }

  // 移除undefined的字段
  Object.keys(requestData).forEach(key => {
    if (requestData[key] === undefined) {
      delete requestData[key]
    }
  })

  return request({
    url: '/counselor/apply',
    method: 'post',
    data: requestData
  })
}

/**
 * 获取咨询师申请状态
 */
export function getApplicationStatus() {
  return request({
    url: '/counselor/application/status',
    method: 'get'
  })
}

/**
 * 获取待审核申请列表（管理员）
 * @param {Object} params
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getPendingApplications(params) {
  return request({
    url: '/counselor/application/pending',
    method: 'get',
    params
  })
}

/**
 * 审核咨询师申请（管理员）
 * @param {string} counselorId - 咨询师ID
 * @param {string} action - 审核操作：approve/reject
 * @param {string} reason - 拒绝原因（拒绝时必填）
 */
export function reviewApplication(counselorId, action, reason) {
  return request({
    url: `/counselor/application/${counselorId}/review`,
    method: 'post',
    params: { action, reason }
  })
}

// ── 预约前沟通 ──────────────────────────────────────
export function startInquiry(counselorId) {
  return request({ url: `/inquiry/${counselorId}/start`, method: 'post' })
}

export function getInquiryMessages(inquiryId) {
  return request({ url: `/inquiry/${inquiryId}/messages`, method: 'get' })
}

export function sendInquiryMessage(inquiryId, content) {
  return request({
    url: `/inquiry/${inquiryId}/message`,
    method: 'post',
    data: { content, msg_type: 'text' }
  })
}
