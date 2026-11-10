<template>
<section class="view active" data-view="chat" ref="rootEl" @click="onClick">

  <div class="page-head" style="padding-bottom:18px">
    <div>
      <div class="eyebrow">Consultation</div>
      <h1>咨询对话</h1>
      <p v-if="appt.id">{{ counselorName }} · {{ fmtDate(appt.appointment_date) }} · {{ statusText(appt.status) }}</p>
      <p v-else>正在连接咨询室…</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost btn-sm" data-back>返回我的预约</button>
    <button
      v-if="appt.status === 'confirmed' || appt.status === 'in_progress'"
      class="btn btn-primary btn-sm"
      style="margin-left:9px"
      data-end
    >结束咨询</button>
  </div>

  <div class="chat-wrap card">
    <!-- 消息区 -->
    <div class="msg-scroll" ref="scrollEl">
      <div v-if="loadingMsgs" class="chat-empty">正在加载消息…</div>
      <div v-else-if="!messages.length" class="chat-empty">
        <h4>还没有消息</h4>
        <p>发送第一条消息，开始这次对话。</p>
      </div>

      <template v-for="(msg, i) in messages" :key="msg.id || i">
        <!-- 系统消息 -->
        <div v-if="msg.message_type === 'system'" class="sys-msg">
          <span>{{ msg.content }}</span>
        </div>

        <!-- 普通消息 -->
        <div v-else class="msg-row" :class="{ me: msg.sender_type === 'user' }">
          <div class="avatar" :class="msg.sender_type === 'user' ? 'av-a' : 'av-b'">
            {{ msg.sender_type === 'user' ? '我' : (counselorName || '咨').slice(0, 1) }}
          </div>
          <div class="msg-body">
            <div class="msg-meta">
              <span>{{ msg.sender_type === 'user' ? '我' : counselorName }}</span>
              <span class="msg-time">{{ fmtTime(msg.created_at) }}</span>
            </div>
            <div v-if="msg.message_type === 'text'" class="bubble">{{ msg.content }}</div>
            <a v-else-if="msg.message_type === 'image'" class="bubble-img" :href="msg.content" target="_blank">
              <img :src="msg.content" alt="图片消息" />
            </a>
            <a v-else class="bubble file-link" :href="msg.content" target="_blank">
              {{ fileName(msg.content) }}
            </a>
          </div>
        </div>
      </template>
    </div>

    <!-- 输入区 -->
    <div class="composer-bar">
      <button class="icon-btn" title="上传图片" data-upload>
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4.5" width="18" height="15" rx="2.5"/><circle cx="8.5" cy="9.5" r="1.6"/><path d="M21 15l-4.5-4.5L7 20"/>
        </svg>
      </button>
      <input ref="fileEl" type="file" accept="image/*" style="display:none" @change="onFile" />
      <textarea
        class="chat-input"
        v-model="draft"
        rows="1"
        placeholder="说点什么…（Enter 发送，Shift+Enter 换行）"
        @keydown.enter.exact.prevent="doSend"
      ></textarea>
      <button class="btn btn-primary btn-sm" :disabled="sending || !draft.trim()" data-send>
        {{ sending ? '发送中' : '发送' }}
      </button>
    </div>
  </div>

</section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMessages, sendMessage, uploadFile, endConsultation } from '@/api/consultation'
import { getAppointmentDetail } from '@/api/counselor'

const router = useRouter()
const route = useRoute()
const rootEl = ref(null)
const scrollEl = ref(null)
const fileEl = ref(null)

const appt = ref({})
const messages = ref([])
const draft = ref('')
const loadingMsgs = ref(true)
const sending = ref(false)

let pollTimer = null
const appointmentId = route.params.id

const counselorName = computed(() => {
  const c = appt.value.counselor
  return (c && c.name) || appt.value.counselor_name || '咨询师'
})

function statusText(s) {
  const map = {
    pending: '待确认', confirmed: '已确认', in_progress: '进行中',
    completed: '已完成', cancelled: '已取消', refunded: '已退款'
  }
  return map[s] || s || ''
}

function fmtDate(v) {
  if (!v) return ''
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v).replace('T', ' ').slice(0, 16)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function fmtTime(v) {
  if (!v) return ''
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return ''
  const p = n => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}`
}

function fileName(url) {
  try { return decodeURIComponent(String(url).split('/').pop() || '附件') } catch { return '附件' }
}

onMounted(async () => {
  if (!appointmentId) {
    ElMessage.error('缺少预约信息')
    router.push('/workspace/booking?tab=mine')
    return
  }
  try {
    const res = await getAppointmentDetail(appointmentId)
    appt.value = (res && res.data) || {}
  } catch (e) {
    ElMessage.error('预约信息加载失败')
  }
  await loadMessages()
  pollTimer = setInterval(loadMessages, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function loadMessages() {
  try {
    const has = messages.value.length > 0
    const params = has
      ? { last_id: messages.value[messages.value.length - 1].id }
      : { limit: 2000 }
    const res = await getMessages(appointmentId, params)
    const items = (res && res.data && res.data.items) || []
    if (items.length) {
      messages.value = has ? [...messages.value, ...items] : items
      scrollBottom()
    }
  } catch (e) {
    // 轮询失败不打扰用户，下次再试
  } finally {
    loadingMsgs.value = false
  }
}

function scrollBottom() {
  nextTick(() => {
    const el = scrollEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function doSend() {
  const text = draft.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    await sendMessage(appointmentId, { content: text, message_type: 'text' })
    draft.value = ''
    await loadMessages()
    // 发送后状态可能由 confirmed 推进到 in_progress，刷新一次头部
    try {
      const res = await getAppointmentDetail(appointmentId)
      appt.value = (res && res.data) || appt.value
    } catch { /* 忽略 */ }
  } catch (e) {
    const d = e && e.response && e.response.data && e.response.data.detail
    ElMessage.error(typeof d === 'string' ? d : '发送失败，请重试')
  } finally {
    sending.value = false
  }
}

async function onFile(ev) {
  const f = ev.target.files && ev.target.files[0]
  ev.target.value = ''
  if (!f) return
  if (f.size > 10 * 1024 * 1024) {
    ElMessage.warning('图片不能超过 10MB')
    return
  }
  try {
    const res = await uploadFile(f)
    const url = (res && res.data && res.data.file_url) || ''
    if (!url) throw new Error('上传返回缺少地址')
    await sendMessage(appointmentId, { content: url, message_type: 'image' })
    await loadMessages()
  } catch (e) {
    ElMessage.error('图片上传失败')
  }
}

async function doEnd() {
  try {
    await ElMessageBox.confirm('结束后将无法继续发送消息，确认结束这次咨询吗？', '结束咨询', {
      confirmButtonText: '确认结束',
      cancelButtonText: '再想想',
      type: 'warning'
    })
  } catch { return }
  try {
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/workspace/booking?tab=mine')
  } catch (e) {
    const d = e && e.response && e.response.data && e.response.data.detail
    ElMessage.error(typeof d === 'string' ? d : '结束失败，请重试')
  }
}

function onClick(e) {
  if (e.target.closest('[data-back]')) { router.push('/workspace/booking?tab=mine'); return }
  if (e.target.closest('[data-upload]')) { if (fileEl.value) fileEl.value.click(); return }
  if (e.target.closest('[data-end]')) { doEnd(); return }
  if (e.target.closest('[data-send]')) { doSend(); return }
}
</script>

<style scoped>
.chat-wrap {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 250px);
  min-height: 420px;
  overflow: hidden;
  padding: 0 !important;
}

.msg-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--surface-2);
}

.chat-empty {
  margin: auto;
  text-align: center;
  color: var(--ink-3);
}
.chat-empty h4 { font-size: 14px; font-weight: 590; color: var(--ink-2); }
.chat-empty p { font-size: 13px; margin-top: 6px; }

/* 系统消息 */
.sys-msg {
  text-align: center;
  font-size: 12px;
  color: var(--ink-3);
}
.sys-msg span {
  display: inline-block;
  background: var(--sand);
  color: #8A7A62;
  padding: 4px 12px;
  border-radius: 20px;
}

/* 气泡 */
.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.me { flex-direction: row-reverse; }

.msg-body { max-width: 72%; display: flex; flex-direction: column; }
.msg-row.me .msg-body { align-items: flex-end; }

.msg-meta {
  display: flex; gap: 8px; align-items: baseline;
  font-size: 11.5px; color: var(--ink-3);
  margin-bottom: 5px;
}
.msg-time { font-variant-numeric: tabular-nums; }

.bubble {
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 10px 14px;
  border-radius: 13px 13px 13px 4px;
  font-size: 13.5px;
  line-height: 1.72;
  color: var(--ink);
  white-space: pre-wrap;
  word-break: break-word;
}
.msg-row.me .bubble {
  background: linear-gradient(160deg, #357B74, #22524E);
  border-color: transparent;
  color: #fff;
  border-radius: 13px 13px 4px 13px;
}

.bubble-img { display: block; max-width: 240px; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }
.bubble-img img { display: block; width: 100%; height: auto; }

.file-link {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--sea-deep); text-decoration: underline;
  text-underline-offset: 3px;
}

/* 输入区 */
.composer-bar {
  display: flex; align-items: flex-end; gap: 10px;
  padding: 14px 18px;
  border-top: 1px solid var(--line);
  background: var(--surface);
}

.icon-btn {
  width: 36px; height: 36px; flex: 0 0 36px;
  border-radius: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--ink-3);
  transition: all .16s var(--ease);
}
.icon-btn:hover { background: var(--sea-soft); color: var(--sea-deep); }

.chat-input {
  flex: 1;
  min-height: 38px;
  max-height: 120px;
  border: 1px solid var(--line);
  border-radius: 11px;
  padding: 9px 13px;
  font-family: inherit;
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--ink);
  background: var(--surface-2);
  resize: none;
  outline: none;
  transition: border-color .18s var(--ease), background .18s var(--ease);
}
.chat-input:focus { border-color: var(--sea); background: var(--surface); }
.chat-input::placeholder { color: var(--ink-3); }

@media (max-width: 860px) {
  .chat-wrap { height: calc(100vh - 220px); }
  .msg-body { max-width: 84%; }
}
</style>
