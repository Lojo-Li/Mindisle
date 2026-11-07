// 心理知识相关API
import request from './index'

/**
 * 获取知识列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 分类筛选
 * @param {string} params.sort - 排序方式
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getKnowledgeList(params) {
  return request({
    url: '/knowledge/list',
    method: 'get',
    params
  })
}

/**
 * 获取知识详情
 * @param {string} id - 知识ID
 */
export function getKnowledgeDetail(id) {
  return request({
    url: `/knowledge/${id}`,
    method: 'get'
  })
}

/**
 * 获取推荐知识
 * @param {string} id - 当前知识ID
 */
export function getRecommendedKnowledge(id) {
  return request({
    url: `/knowledge/${id}/recommended`,
    method: 'get'
  })
}

/**
 * 收藏知识
 * @param {string} id - 知识ID
 */
export function favoriteKnowledge(id) {
  return request({
    url: `/knowledge/${id}/favorite`,
    method: 'post'
  })
}

/**
 * 取消收藏知识
 * @param {string} id - 知识ID
 */
export function unfavoriteKnowledge(id) {
  return request({
    url: `/knowledge/${id}/favorite`,
    method: 'delete'
  })
}

/**
 * 获取当前用户收藏列表
 */
export function getUserFavorites(params) {
  return request({
    url: '/knowledge/user/favorites',
    method: 'get',
    params
  })
}

/**
 * 点赞知识
 * @param {string} id - 知识ID
 */
export function likeKnowledge(id) {
  return request({
    url: `/knowledge/${id}/like`,
    method: 'post'
  })
}

/**
 * 取消点赞知识
 * @param {string} id - 知识ID
 */
export function unlikeKnowledge(id) {
  return request({
    url: `/knowledge/${id}/like`,
    method: 'delete'
  })
}

/**
 * 提交评论
 * @param {string} id - 知识ID
 * @param {Object} data
 * @param {string} data.content - 评论内容
 * @param {number} data.parent_id - 父评论ID（回复时使用）
 */
export function submitComment(id, data) {
  return request({
    url: `/knowledge/${id}/comment`,
    method: 'post',
    data
  })
}

/**
 * 获取文章评论列表
 * @param {string} id - 文章ID
 * @param {Object} params
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 */
export function getComments(id, params) {
  return request({
    url: `/knowledge/${id}/comments`,
    method: 'get',
    params
  })
}

/**
 * 删除评论
 * @param {number} commentId - 评论ID
 */
export function deleteComment(commentId) {
  return request({
    url: `/knowledge/comments/${commentId}`,
    method: 'delete'
  })
}

/**
 * 点赞评论
 * @param {number} commentId - 评论ID
 */
export function likeComment(commentId) {
  return request({
    url: `/knowledge/comments/${commentId}/like`,
    method: 'post'
  })
}

/**
 * 取消点赞评论
 * @param {number} commentId - 评论ID
 */
export function unlikeComment(commentId) {
  return request({
    url: `/knowledge/comments/${commentId}/like`,
    method: 'delete'
  })
}
