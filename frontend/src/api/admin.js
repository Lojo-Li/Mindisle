// 后台管理相关API
import request from './index'

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStats() {
  return request({
    url: '/admin/dashboard/stats',
    method: 'get'
  })
}

/**
 * 获取图表数据
 * @param {string} type - 图表类型: user/trend/order/revenue
 */
export function getChartData(type) {
  return request({
    url: '/admin/dashboard/chart',
    method: 'get',
    params: { type }
  })
}

/**
 * 获取待审核咨询师列表
 * @param {Object} params
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getPendingCounselors(params) {
  return request({
    url: '/admin/counselors/pending',
    method: 'get',
    params
  })
}

/**
 * 审核咨询师
 * @param {string} id - 咨询师ID
 * @param {Object} data
 * @param {string} data.action - 操作: approve/reject
 * @param {string} data.reason - 拒绝理由
 */
export function reviewCounselor(id, data) {
  return request({
    url: `/admin/counselor/${id}/review`,
    method: 'post',
    data
  })
}

/**
 * 获取知识文章列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 分类
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getKnowledgeArticles(params) {
  return request({
    url: '/admin/knowledge/list',
    method: 'get',
    params
  })
}

/**
 * 创建/更新知识文章
 * @param {Object} data
 * @param {string} data.id - 文章ID（更新时）
 * @param {string} data.title - 标题
 * @param {string} data.content - 内容
 * @param {string} data.category - 分类
 * @param {string} data.cover - 封面图
 */
export function saveKnowledgeArticle(data) {
  return request({
    url: '/admin/knowledge/save',
    method: 'post',
    data
  })
}

/**
 * 删除知识文章
 * @param {string} id - 文章ID
 */
export function deleteKnowledgeArticle(id) {
  return request({
    url: `/admin/knowledge/${id}`,
    method: 'delete'
  })
}

/**
 * 获取用户列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminUsers(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 封禁用户
 * @param {string} id - 用户ID
 * @param {Object} data
 * @param {boolean} data.banned - 是否封禁
 */
export function banUser(id, data) {
  return request({
    url: `/admin/user/${id}/ban`,
    method: 'post',
    data
  })
}

/**
 * 获取订单列表
 * @param {Object} params
 * @param {string} params.status - 订单状态
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminOrders(params) {
  return request({
    url: '/admin/orders',
    method: 'get',
    params
  })
}

/**
 * 导出订单数据
 */
export function exportOrders() {
  return request({
    url: '/admin/orders/export',
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 获取咨询师列表（管理后台）
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.counselor_status - 状态过滤
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 */
export function getAdminCounselors(params) {
  return request({
    url: '/admin/counselors',
    method: 'get',
    params
  })
}

/**
 * 切换咨询师状态（启用/禁用）
 * @param {string} id - 咨询师ID
 * @param {Object} data
 * @param {boolean} data.active - 是否启用
 */
export function toggleCounselorStatus(id, data) {
  return request({
    url: `/admin/counselor/${id}/status`,
    method: 'put',
    data
  })
}

/**
 * 获取心理测试列表（管理后台）
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminTestList(params) {
  return request({
    url: '/admin/tests',
    method: 'get',
    params
  })
}

/**
 * 获取心理测试详情（管理后台）
 * @param {string} id - 测试ID
 */
export function getAdminTestDetail(id) {
  return request({
    url: `/admin/test/${id}`,
    method: 'get'
  })
}

/**
 * 创建心理测试
 * @param {Object} data
 * @param {string} data.title - 测试标题
 * @param {string} data.description - 测试描述
 * @param {string} data.category - 分类
 * @param {string} data.coverImage - 封面图
 * @param {Array} data.questions - 题目列表
 */
export function createTest(data) {
  return request({
    url: '/admin/test',
    method: 'post',
    data
  })
}

/**
 * 更新心理测试
 * @param {string} id - 测试ID
 * @param {Object} data
 */
export function updateTest(id, data) {
  return request({
    url: `/admin/test/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除心理测试
 * @param {string} id - 测试ID
 */
export function deleteTest(id) {
  return request({
    url: `/admin/test/${id}`,
    method: 'delete'
  })
}

/**
 * 获取测试题目列表
 * @param {string} testId - 测试ID
 */
export function getTestQuestions(testId) {
  return request({
    url: `/admin/test/${testId}/questions`,
    method: 'get'
  })
}

// ==================== 对话管理 ====================

/**
 * 获取对话列表（管理后台）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {string} params.tag - 标签名
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminDialogues(params) {
  return request({
    url: '/admin/dialogues',
    method: 'get',
    params
  })
}

/**
 * 获取对话详情（管理后台）
 * @param {number} id - 对话ID
 */
export function getAdminDialogueDetail(id) {
  return request({
    url: `/admin/dialogue/${id}`,
    method: 'get'
  })
}

/**
 * 删除对话（管理后台）
 * @param {number} id - 对话ID
 */
export function deleteAdminDialogue(id) {
  return request({
    url: `/admin/dialogue/${id}`,
    method: 'delete'
  })
}
