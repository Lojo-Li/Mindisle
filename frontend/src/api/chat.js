// 智能问答相关API
import { getToken } from '@/utils/storage'
import request from './index'

// 获取API基础URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

/**
 * 获取对话列表
 * @param {Object} params - 查询参数
 * @param {string} params.tag - 标签筛选（可选）
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getChatList(params) {
  return request({
    url: '/chat/list',
    method: 'get',
    params
  })
}

/**
 * 获取对话详情
 * @param {string} id - 对话ID
 */
export function getChatDetail(id) {
  return request({
    url: `/chat/${id}`,
    method: 'get'
  })
}

/**
 * 创建新对话
 * @param {Object} data
 * @param {string} data.title - 对话标题（可选）
 */
export function createChat(data) {
  return request({
    url: '/chat/create',
    method: 'post',
    data
  })
}

/**
 * 发送消息
 * @param {string} chatId - 对话ID
 * @param {Object} data
 * @param {string} data.content - 消息内容
 * @param {string} data.type - 消息类型 text/voice
 */
export function sendMessage(chatId, data) {
  return request({
    url: `/chat/${chatId}/message`,
    method: 'post',
    data
  })
}

/**
 * 发送消息（流式输出）
 * @param {string} chatId - 对话ID
 * @param {Object} data
 * @param {string} data.content - 消息内容
 * @param {string} data.type - 消息类型 text/voice
 * @param {Function} onMessage - 接收流式消息的回调
 * @param {Function} onComplete - 完成时的回调
 * @param {Function} onError - 错误时的回调
 */
export function sendMessageStream(chatId, data, onMessage, onComplete, onError) {
  const token = getToken()

  return fetch(`${BASE_URL}/chat/${chatId}/message/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  }).then(async (response) => {
    if (!response.ok) {
      throw new Error('网络响应失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 处理SSE格式的数据
      const lines = buffer.split('\n\n')
      buffer = lines.pop() // 保留不完整的数据

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.error) {
              onError?.(new Error(data.error))
              return
            }
            if (data.done) {
              onComplete?.(data.message_id)
              return
            }
            if (data.content) {
              onMessage?.(data.content)
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e)
          }
        }
      }
    }
  }).catch((error) => {
    onError?.(error)
  })
}

/**
 * 删除对话
 * @param {string} id - 对话ID
 */
export function deleteChat(id) {
  return request({
    url: `/chat/${id}`,
    method: 'delete'
  })
}

/**
 * 更新对话标题
 * @param {string} id - 对话ID
 * @param {string} title - 新标题
 */
export function updateChatTitle(id, title) {
  return request({
    url: `/chat/${id}/title`,
    method: 'put',
    data: { title }
  })
}

/**
 * 获取所有标签
 */
export function getTags() {
  return request({
    url: '/chat/tags',
    method: 'get'
  })
}

/**
 * 为对话添加标签
 * @param {string} chatId - 对话ID
 * @param {string} tagId - 标签ID
 */
export function addTagToChat(chatId, tagId) {
  return request({
    url: `/chat/${chatId}/tag`,
    method: 'post',
    params: { tag_id: tagId }
  })
}

/**
 * 移除对话的标签
 * @param {string} chatId - 对话ID
 * @param {string} tagId - 标签ID
 */
export function removeTagFromChat(chatId, tagId) {
  return request({
    url: `/chat/${chatId}/tag/${tagId}`,
    method: 'delete'
  })
}

/**
 * 创建自定义标签
 * @param {Object} data
 * @param {string} data.name - 标签名称
 * @param {string} data.color - 标签颜色
 */
export function createTag(data) {
  return request({
    url: '/chat/tag',
    method: 'post',
    data
  })
}

/**
 * 删除自定义标签
 * @param {string} tagId - 标签ID
 */
export function deleteTag(tagId) {
  return request({
    url: `/chat/tag/${tagId}`,
    method: 'delete'
  })
}

/**
 * 语音转文字
 * @param {File} file - 音频文件
 */
export function voiceToText(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/chat/voice-to-text',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
