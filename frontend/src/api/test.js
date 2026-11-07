// 心理测试相关API
import request from './index'

/**
 * 获取测试列表
 * @param {Object} params - 查询参数
 * @param {string} params.category - 分类筛选（可选）
 * @param {string} params.sort - 排序方式 hot/latest/rating
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getTestList(params) {
  return request({
    url: '/test/list',
    method: 'get',
    params
  })
}

/**
 * 获取测试详情
 * @param {string} id - 测试ID
 */
export function getTestDetail(id) {
  return request({
    url: `/test/${id}`,
    method: 'get'
  })
}

/**
 * 开始测试（获取测试题目）
 * @param {string} id - 测试ID
 */
export function startTest(id) {
  return request({
    url: `/test/${id}/start`,
    method: 'post'
  })
}

/**
 * 保存答题进度
 * @param {string} testId - 测试ID
 * @param {Object} data
 * @param {Array} data.answers - 答案列表
 */
export function saveProgress(testId, data) {
  return request({
    url: `/test/${testId}/progress`,
    method: 'post',
    data
  })
}

/**
 * 获取答题进度（用于断点续答）
 * @param {string} testId - 测试ID
 */
export function getProgress(testId) {
  return request({
    url: `/test/${testId}/progress`,
    method: 'get'
  })
}

/**
 * 提交测试答案
 * @param {string} testId - 测试ID
 * @param {Object} data
 * @param {Array} data.answers - 答案列表
 */
export function submitTest(testId, data) {
  return request({
    url: `/test/${testId}/submit`,
    method: 'post',
    data
  })
}

/**
 * 获取测试结果
 * @param {string} resultId - 结果ID
 */
export function getTestResult(resultId) {
  return request({
    url: `/test/result/${resultId}`,
    method: 'get'
  })
}

/**
 * 获取用户测试历史
 * @param {Object} params
 * @param {string} params.testId - 测试ID（可选，筛选特定测试）
 * @param {number} params.page - 页码
 */
export function getTestHistory(params) {
  return request({
    url: '/test/history',
    method: 'get',
    params
  })
}

/**
 * 获取测试趋势数据
 * @param {string} testId - 测试ID
 */
export function getTestTrend(testId) {
  return request({
    url: `/test/${testId}/trend`,
    method: 'get'
  })
}

/**
 * 收藏测试结果
 * @param {string} resultId - 结果ID
 */
export function favoriteResult(resultId) {
  return request({
    url: `/test/result/${resultId}/favorite`,
    method: 'post'
  })
}

/**
 * 取消收藏测试结果
 * @param {string} resultId - 结果ID
 */
export function unfavoriteResult(resultId) {
  return request({
    url: `/test/result/${resultId}/favorite`,
    method: 'delete'
  })
}

/**
 * 删除测试结果
 * @param {string} resultId - 结果ID
 */
export function deleteTestResult(resultId) {
  return request({
    url: `/test/result/${resultId}`,
    method: 'delete'
  })
}

/**
 * 获取综合心理分析报告
 * @param {Object} params
 * @param {number} params.days - 分析最近多少天的数据（7-365天，默认90）
 */
export function getComprehensiveAnalysis(params = {}) {
  return request({
    url: '/test/analysis/comprehensive',
    method: 'get',
    params
  })
}
