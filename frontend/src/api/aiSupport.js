// AI 心理支持相关 API（E 线）
import request from './index'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 流式对话：按事件回调，承载 risk / sources / content / done / title
 *
 * 后端事件序列：
 *   {type:'risk',    risk:{level,label,keywords,actions,hotlines}}
 *   {type:'sources', sources:[{vector_id,title,snippet,score}]}
 *   {content:'...',  done:false}            ← 增量文本
 *   {content:'',     done:true, message_id, crisis_level, source_count}
 *   {type:'title_update', dialogue_title}
 *
 * @param {number|string} chatId
 * @param {string} content
 * @param {Object} handlers
 * @param {(risk:Object)=>void} [handlers.onRisk]
 * @param {(sources:Array)=>void} [handlers.onSources]
 * @param {(chunk:string)=>void} [handlers.onContent]
 * @param {(done:Object)=>void} [handlers.onDone]
 * @param {(title:string)=>void} [handlers.onTitle]
 * @returns {Promise<void>}
 */
export function streamChat(chatId, content, handlers = {}) {
  const token = sessionStorage.getItem('token')
  const ctrl = new AbortController()

  const promise = fetch(`${API_BASE}/chat/${chatId}/message/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 云托管平台代理会占用 Authorization，另用自定义头传递应用 token
      ...(token ? { Authorization: `Bearer ${token}`, 'X-App-Token': token } : {})
    },
    body: JSON.stringify({ content, type: 'text' }),
    signal: ctrl.signal
  }).then(async (resp) => {
    if (!resp.ok) {
      const err = new Error(`HTTP ${resp.status}`)
      err.status = resp.status
      throw err
    }
    if (!resp.body) throw new Error('当前浏览器不支持流式响应')

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const handleChunk = (raw) => {
      if (raw.indexOf('data: ') !== 0) return
      let data
      try { data = JSON.parse(raw.slice(6)) } catch { return }

      if (data.error) throw new Error(data.error)

      if (data.type === 'risk' && data.risk) { handlers.onRisk?.(data.risk); return }
      if (data.type === 'sources') { handlers.onSources?.(data.sources || []); return }
      if (data.type === 'title_update') { handlers.onTitle?.(data.dialogue_title); return }
      if (data.done) { handlers.onDone?.(data); return }
      if (data.content) { handlers.onContent?.(data.content) }
    }

    // 逐块读取，按 \n\n 切分 SSE
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''
      parts.forEach(handleChunk)
    }
    if (buffer.trim()) handleChunk(buffer.trim())
  })

  promise.abort = () => ctrl.abort()
  return promise
}

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
