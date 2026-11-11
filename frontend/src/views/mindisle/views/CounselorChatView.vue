<template>
<section class="view active" data-view="cchat" ref="rootEl">

  <!-- 加载中 -->
  <div v-if="loading" class="card">
    <div class="empty">
      <div class="empty-mark">◌</div>
      <div>正在进入会话…</div>
    </div>
  </div>

  <!-- 加载失败 -->
  <div v-else-if="loadError" class="card">
    <div class="empty">
      <div class="empty-mark">!</div>
      <div class="empty-title">无法进入会话</div>
      <div class="empty-sub">{{ loadError }}</div>
      <button class="btn btn-ghost btn-sm" style="margin-top:14px" @click="goBack">返回咨询会话</button>
    </div>
  </div>

  <!-- 会话主体：左侧对话 + 右侧学生信息 -->
  <div v-else class="cchat-layout">

    <div class="chat-shell">
      <!-- 头部 -->
      <div class="chat-head">
        <div class="chat-peer">
          <div class="chat-avatar">{{ initialOf(studentName) }}</div>
          <div class="chat-peer-text">
            <h3>
              {{ studentName }}
              <span class="tag" :class="statusClass(appt.status)">{{ statusLabel(appt.status) }}</span>
            </h3>
            <div class="chat-peer-meta">
              <span class="online-dot on" />
              <span>咨询中</span>
              <span class="dot-sep">·</span>
              <span>{{ typeLabel(appt.consultation_type) }}</span>
              <span class="dot-sep">·</span>
              <span class="tag sea">公益免费</span>
            </div>
          </div>
        </div>

        <div class="chat-head-actions">
          <div v-if="activeNow" class="timer-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="12" r="9"/><path d="M12 7.5v5l3 1.8"/>
            </svg>
            <span>{{ formatDuration(elapsedTime) }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="openNote">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" style="margin-right:5px">
              <path d="M4 4.5h11l5 5v10a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19.5z"/><path d="M8 12h8M8 16h5"/>
            </svg>
            添加备注
          </button>
          <button v-if="activeNow" class="btn btn-ghost btn-sm" @click="handleEndConsultation">结束咨询</button>
        </div>
      </div>

      <!-- 消息区 -->
      <div ref="messagesEl" class="chat-body">
        <div v-if="!visibleMessages.length" class="chat-empty">
          <div class="empty-mark">✧</div>
          <div class="empty-title">等待学生发言</div>
          <div class="empty-sub">学生发送消息后会显示在这里。</div>
        </div>

        <template v-for="(msg, idx) in visibleMessages" :key="msg.id">
          <div v-if="showDateDivider(idx)" class="date-sep">
            <span>{{ fmtDateDivider(msg.created_at) }}</span>
          </div>

          <div v-if="msg.message_type === 'system'" class="system-line">
            <span>{{ msg.content }}</span>
          </div>

          <div v-else class="bubble-row" :class="{ self: msg.sender_type === 'counselor' }">
            <div class="bubble-avatar">{{ msg.sender_type === 'counselor' ? '我' : initialOf(studentName) }}</div>
            <div class="bubble-main">
              <div class="bubble-meta">
                <span v-if="msg.sender_type !== 'counselor'">{{ studentName }}</span>
                <span class="bubble-time">{{ fmtTime(msg.created_at) }}</span>
              </div>

              <div v-if="msg.message_type === 'text'" class="bubble">{{ msg.content }}</div>

              <div v-else-if="msg.message_type === 'image'" class="bubble-img-wrap">
                <img :src="msg.content" class="bubble-img" @click="previewSrc = msg.content" alt="图片消息" />
              </div>

              <div v-else-if="msg.message_type === 'file'" class="bubble-file">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                  <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>
                </svg>
                <span class="file-name">{{ msg.file_name || fileNameOf(msg.content) }}</span>
                <button class="btn btn-ghost btn-sm" @click="downloadFile(msg.file_url || msg.content)">下载</button>
              </div>

              <div v-else class="bubble">{{ msg.content }}</div>
            </div>
          </div>
        </template>
      </div>

      <!-- 快捷回复 -->
      <div v-if="activeNow" class="quick-row">
        <span class="quick-label">快捷回复</span>
        <button
          v-for="(r, i) in QUICK_REPLIES"
          :key="i"
          class="quick-chip"
          :title="r"
          @click="inputContent = r"
        >{{ r }}</button>
      </div>

      <!-- 输入区 -->
      <div v-if="activeNow" class="chat-input">
        <div class="input-tools">
          <label class="tool-btn" title="发送图片">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><circle cx="8.5" cy="9.5" r="1.6"/><path d="M20 16l-4.5-4.5L7 20"/>
            </svg>
            <input type="file" accept="image/*" hidden @change="onPickImage" />
          </label>
          <label class="tool-btn" title="发送文件">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <path d="M3.5 7.5a2 2 0 0 1 2-2h3.6l2 2h7.4a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>
            </svg>
            <input type="file" hidden @change="onPickFile" />
          </label>
          <span v-if="uploading" class="upload-hint">上传中…</span>
        </div>

        <div class="input-row">
          <textarea
            v-model="inputContent"
            class="input-textarea"
            rows="3"
            placeholder="回复学生…（Enter 发送，Shift + Enter 换行）"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            class="btn btn-primary send-btn"
            :disabled="!inputContent.trim() || sending"
            @click="sendMessage"
          >{{ sending ? '发送中…' : '发送' }}</button>
        </div>
      </div>

      <div v-else class="chat-closed">
        <span>本次咨询已{{ statusLabel(appt.status) }}</span>
        <button class="btn btn-ghost btn-sm" @click="goBack">返回咨询会话</button>
      </div>
    </div>

    <!-- 右侧学生信息 -->
    <aside class="side-panel">
      <div class="side-card">
        <div class="side-head">
          <h4>学生信息</h4>
        </div>
        <div class="side-body">
          <div class="side-row">
            <span class="side-label">昵称</span>
            <span class="side-value">{{ studentName }}</span>
          </div>
          <div v-if="studentEmail" class="side-row">
            <span class="side-label">邮箱</span>
            <span class="side-value mono">{{ studentEmail }}</span>
          </div>
          <div class="side-row">
            <span class="side-label">咨询方式</span>
            <span class="side-value">{{ typeLabel(appt.consultation_type) }}</span>
          </div>
          <div class="side-row">
            <span class="side-label">预约时间</span>
            <span class="side-value">{{ fmtDate(appt.appointment_date) }}</span>
          </div>
          <div class="side-row">
            <span class="side-label">订单号</span>
            <span class="side-value mono">{{ appt.appointment_no || '—' }}</span>
          </div>
          <div class="side-row">
            <span class="side-label">状态</span>
            <span class="side-value">
              <span class="tag" :class="statusClass(appt.status)">{{ statusLabel(appt.status) }}</span>
            </span>
          </div>
        </div>
      </div>

      <div class="side-card">
        <div class="side-head">
          <h4>学生诉求</h4>
        </div>
        <div class="side-body">
          <p class="side-desc">{{ appt.problem_description || '学生未填写诉求描述。' }}</p>
        </div>
      </div>

      <div class="side-card">
        <div class="side-head">
          <h4>我的备注</h4>
          <button class="side-edit" @click="openNote">编辑</button>
        </div>
        <div class="side-body">
          <p class="side-desc">{{ noteText || '还没有添加备注。备注仅你自己可见。' }}</p>
        </div>
      </div>
    </aside>
  </div>

  <!-- 图片预览 -->
  <div v-if="previewSrc" class="preview-mask" @click.self="previewSrc = ''">
    <img :src="previewSrc" class="preview-img" alt="预览" />
  </div>
</section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMessages, sendMessage as sendMessageApi, uploadFile,
  endConsultation, addConsultationNote, getCounselorOrders, isSignalMessage
} from '@/api/consultation'
import { consultTypeText } from '../workspace'

const route = useRoute()
const router = useRouter()

const appointmentId = route.params.id
const rootEl = ref(null)
const messagesEl = ref(null)

const loading = ref(true)
const loadError = ref('')
const appt = ref({})
const messages = ref([])
const inputContent = ref('')
const sending = ref(false)
const uploading = ref(false)
const previewSrc = ref('')
const elapsedTime = ref(0)
const noteText = ref('')

let pollTimer = null
let tickTimer = null

const QUICK_REPLIES = [
  '您好，我已准备好，请开始讲述您的情况。',
  '我理解您的感受，能详细说说吗？',
  '这个问题很重要，我们深入探讨一下。',
  '您的进步很明显，继续保持！',
  '今天的咨询时间差不多了，我们总结一下讨论的内容。'
]

// ---------- 计算 ----------
const studentName = computed(() =>
  appt.value?.user_info?.nickname || appt.value?.user_name || '学生'
)
const studentEmail = computed(() => appt.value?.user_info?.email || '')
const activeNow = computed(() => ['confirmed', 'in_progress'].includes(appt.value?.status))
const visibleMessages = computed(() => messages.value.filter(m => !isSignalMessage(m)))

// ---------- 展示 ----------
const STATUS_LABEL = {
  pending: '待确认', confirmed: '已确认', in_progress: '进行中',
  completed: '已完成', cancelled: '已取消'
}

function statusLabel(s) { return STATUS_LABEL[s] || s || '' }
function statusClass(s) {
  if (s === 'pending') return 'lamp'
  if (s === 'cancelled') return 'rose'
  return 'sea'
}
function typeLabel(t) {
  return consultTypeText(t)
}
function initialOf(n) { return String(n || '学').slice(0, 1) }

function parseDate(v) {
  if (!v) return null
  const d = new Date(String(v).replace(' ', 'T'))
  return isNaN(d.getTime()) ? null : d
}
function fmtDate(v) {
  const d = parseDate(v)
  if (!d) return '—'
  const w = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${w} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
function fmtTime(v) {
  const d = parseDate(v)
  if (!d) return ''
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
function fmtDateDivider(v) {
  const d = parseDate(v)
  if (!d) return ''
  if (d.toDateString() === new Date().toDateString()) return '今天'
  const w = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${w}`
}
function showDateDivider(idx) {
  if (idx === 0) return true
  const a = parseDate(visibleMessages.value[idx]?.created_at)
  const b = parseDate(visibleMessages.value[idx - 1]?.created_at)
  if (!a || !b) return false
  return a.toDateString() !== b.toDateString()
}
function fileNameOf(url) {
  if (!url) return '附件'
  try {
    const p = String(url).split('?')[0].split('/')
    return decodeURIComponent(p[p.length - 1] || '附件')
  } catch (e) { return '附件' }
}
function formatDuration(sec) {
  const s = Math.max(0, Number(sec) || 0)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const r = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`
}

// ---------- 数据 ----------
async function loadAppointment() {
  const res = await getCounselorOrders({ page: 1, page_size: 100 })
  const items = res?.data?.items || []
  const cur = items.find(o => String(o.id) === String(appointmentId))
  if (!cur) throw new Error('订单不存在，或不属于你')
  appt.value = cur
  noteText.value = cur.counselor_notes || ''
  document.title = `与学生${studentName.value}的咨询 - 心屿 Mindisle`
}

async function loadMessages() {
  try {
    const has = messages.value.length > 0
    const params = has
      ? { last_id: messages.value[messages.value.length - 1].id }
      : { limit: 2000 }
    const res = await getMessages(appointmentId, params)
    const items = res?.data?.items || []
    if (has) {
      if (items.length) messages.value = [...messages.value, ...items]
    } else {
      messages.value = items
    }
    await nextTick()
    scrollToBottom()
  } catch (e) { /* 轮询失败静默 */ }
}

function scrollToBottom() {
  const el = messagesEl.value
  if (el) el.scrollTop = el.scrollHeight
}

function startTimers() {
  stopTimers()
  pollTimer = setInterval(() => loadMessages(), 3000)
  tickTimer = setInterval(() => {
    if (activeNow.value) elapsedTime.value += 1
  }, 1000)
}
function stopTimers() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  if (tickTimer) { clearInterval(tickTimer); tickTimer = null }
}

onMounted(async () => {
  try {
    await loadAppointment()
    await loadMessages()
    startTimers()
  } catch (e) {
    loadError.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
})

onUnmounted(stopTimers)

// ---------- 动作 ----------
async function sendMessage() {
  const text = inputContent.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    await sendMessageApi(appointmentId, { content: text, message_type: 'text' })
    inputContent.value = ''
    await loadMessages()
    await loadAppointment()
  } catch (e) {
    ElMessage.error('发送失败，请重试')
  } finally {
    sending.value = false
  }
}

async function uploadAndSend(file, type) {
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('文件不能超过 10MB')
    return
  }
  uploading.value = true
  try {
    const res = await uploadFile(file)
    const url = res?.data?.file_url || res?.data?.url
    if (!url) throw new Error('no url')
    await sendMessageApi(appointmentId, { content: url, message_type: type })
    await loadMessages()
  } catch (e) {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

function onPickImage(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  uploadAndSend(f, 'image')
}
function onPickFile(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  uploadAndSend(f, 'file')
}

function downloadFile(url) {
  if (url) window.open(url, '_blank')
}

async function openNote() {
  try {
    const { value } = await ElMessageBox.prompt('记录本次咨询的要点（仅你自己可见）', '添加备注', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputValue: noteText.value || '',
      inputPlaceholder: '例如：学生主要困扰、后续跟进方向…'
    })
    await addConsultationNote(appointmentId, { note: value || '' })
    noteText.value = value || ''
    ElMessage.success('备注已保存')
  } catch (e) { /* 取消 */ }
}

async function handleEndConsultation() {
  try {
    await ElMessageBox.confirm(
      '确定要结束本次咨询吗？结束后学生可以进行评价。',
      '结束咨询',
      { confirmButtonText: '确定结束', cancelButtonText: '继续咨询', type: 'warning' }
    )
  } catch (e) { return }
  try {
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/counselor/dashboard/sessions')
  } catch (e) {
    ElMessage.error('操作失败，请重试')
  }
}

function goBack() {
  router.push('/counselor/dashboard/sessions')
}
</script>

<style scoped>
/* 挂载在 MindisleShell 布局下，心屿变量与通用类由 .mi-portal 提供 */
.view[data-view="cchat"] {
  display: flex;
  flex-direction: column;
  padding-bottom: 24px;
}

.cchat-layout {
  display: flex;
  gap: 16px;
  height: calc(100vh - 120px);
  min-height: 480px;
}

.chat-shell {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-s);
  overflow: hidden;
}

/* ---------- 右侧信息栏 ---------- */
.side-panel {
  flex: 0 0 268px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.side-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-s);
  padding: 15px 17px;
}

.side-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 11px;
}

.side-head h4 {
  font-size: 13px;
  font-weight: 590;
  color: var(--ink);
  letter-spacing: .2px;
}

.side-edit {
  margin-left: auto;
  font-size: 11.5px;
  color: var(--sea);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}
.side-edit:hover { text-decoration: underline }

.side-body {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.side-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 12.5px;
}

.side-label {
  flex: 0 0 58px;
  color: var(--ink-3);
}

.side-value {
  flex: 1 1 auto;
  color: var(--ink);
  word-break: break-all;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
  color: var(--ink-2);
}

.side-desc {
  font-size: 12.5px;
  line-height: 1.85;
  color: var(--ink-2);
  white-space: pre-wrap;
  word-break: break-word;
}

/* ---------- 头部 ---------- */
.chat-head {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 15px 20px;
  border-bottom: 1px solid var(--line);
  background: var(--surface-2);
  flex-wrap: wrap;
  flex: 0 0 auto;
}

.chat-peer { display: flex; align-items: center; gap: 12px; min-width: 0 }

.chat-avatar {
  flex: 0 0 auto;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(160deg, #B9B0A0, #9A9081);
}

.chat-peer-text h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: .2px;
  line-height: 1.4;
}

.chat-peer-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--ink-3);
  flex-wrap: wrap;
}

.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C3CFCE;
  flex: 0 0 auto;
}
.online-dot.on {
  background: #4E9A6A;
  box-shadow: 0 0 0 3px rgba(78, 154, 106, .14);
}
.dot-sep { opacity: .45 }

.chat-head-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.timer-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 11px;
  border-radius: 9px;
  background: var(--sea-soft);
  color: var(--sea-deep);
  font-size: 12.5px;
  font-weight: 560;
  font-variant-numeric: tabular-nums;
}

/* ---------- 消息区 ---------- */
.chat-body {
  flex: 1 1 auto;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 13px;
  background:
    radial-gradient(circle at 16% 10%, rgba(46, 110, 104, .04), transparent 45%),
    var(--surface);
}

.chat-body::-webkit-scrollbar { width: 7px }
.chat-body::-webkit-scrollbar-thumb { background: #DFE5E3; border-radius: 8px }

.chat-empty { margin: auto; text-align: center; padding: 32px 20px }

.date-sep {
  align-self: center;
  padding: 3px 12px;
  border-radius: 20px;
  background: var(--sand);
  color: #8A7A62;
  font-size: 11px;
  letter-spacing: .3px;
}

.system-line {
  align-self: center;
  max-width: 76%;
  padding: 7px 14px;
  border-radius: 20px;
  background: var(--lamp-soft);
  color: #8F6316;
  font-size: 12px;
  line-height: 1.7;
  text-align: center;
}

.bubble-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  max-width: 76%;
}
.bubble-row.self { flex-direction: row-reverse; margin-left: auto }

.bubble-avatar {
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(160deg, #B9B0A0, #9A9081);
}
.bubble-row.self .bubble-avatar {
  background: linear-gradient(160deg, #357B74, #22524E);
}

.bubble-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bubble-row.self .bubble-main { align-items: flex-end }

.bubble-meta {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: var(--ink-3);
  padding: 0 2px;
}
.bubble-time { font-variant-numeric: tabular-nums; opacity: .82 }

.bubble {
  display: inline-block;
  padding: 9px 13px;
  border-radius: 13px 13px 13px 4px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 13.5px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
}
.bubble-row.self .bubble {
  border-radius: 13px 13px 4px 13px;
  background: linear-gradient(160deg, #357B74, #22524E);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 8px 20px -16px rgba(34, 82, 78, .9);
}

.bubble-img-wrap { max-width: 240px }
.bubble-img {
  max-width: 100%;
  max-height: 240px;
  border-radius: 12px;
  border: 1px solid var(--line);
  cursor: zoom-in;
  display: block;
  object-fit: cover;
}

.bubble-file {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  color: var(--ink-2);
}
.bubble-row.self .bubble-file {
  background: var(--sea-soft);
  border-color: transparent;
  color: var(--sea-deep);
}

.file-name {
  font-size: 12.5px;
  max-width: 170px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 快捷回复 ---------- */
.quick-row {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 20px 0;
  overflow-x: auto;
  background: var(--surface);
}
.quick-row::-webkit-scrollbar { height: 0 }

.quick-label {
  flex: 0 0 auto;
  font-size: 11.5px;
  color: var(--ink-3);
}

.quick-chip {
  flex: 0 0 auto;
  max-width: 190px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 4px 11px;
  border-radius: 20px;
  border: 1px solid var(--line);
  background: var(--surface-2);
  color: var(--ink-2);
  font-size: 11.5px;
  cursor: pointer;
  transition: border-color .18s, color .18s, background .18s;
}
.quick-chip:hover {
  border-color: var(--sea);
  color: var(--sea-deep);
  background: var(--sea-soft);
}

/* ---------- 输入区 ---------- */
.chat-input {
  flex: 0 0 auto;
  border-top: 1px solid var(--line);
  padding: 12px 20px 16px;
  background: var(--surface);
}

.input-tools {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 8px;
}

.tool-btn {
  width: 29px;
  height: 29px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-3);
  cursor: pointer;
  transition: background .18s, color .18s, border-color .18s;
  padding: 0;
}
.tool-btn:hover {
  background: var(--surface-2);
  border-color: var(--line);
  color: var(--ink);
}

.upload-hint { font-size: 11.5px; color: var(--ink-3); margin-left: 5px }

.input-row { display: flex; gap: 10px; align-items: flex-end }

.input-textarea {
  flex: 1 1 auto;
  min-height: 66px;
  max-height: 150px;
  padding: 10px 13px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  font-size: 13.5px;
  line-height: 1.75;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color .18s, box-shadow .18s;
}
.input-textarea:focus {
  border-color: var(--sea);
  box-shadow: 0 0 0 3px rgba(46, 110, 104, .1);
}
.input-textarea::placeholder { color: var(--ink-3) }

.send-btn {
  height: 42px;
  padding: 0 20px;
  flex: 0 0 auto;
}
.send-btn:disabled { opacity: .45; cursor: not-allowed; box-shadow: none }

.chat-closed {
  flex: 0 0 auto;
  border-top: 1px solid var(--line);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 13px;
  color: var(--ink-3);
  background: var(--surface-2);
}

.preview-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(20, 34, 36, .62);
  backdrop-filter: blur(3px);
}

.preview-img {
  max-width: 86vw;
  max-height: 86vh;
  border-radius: 14px;
  box-shadow: 0 24px 60px -20px rgba(27, 42, 44, .5);
}

@media (max-width: 1100px) {
  .cchat-layout { flex-direction: column; height: auto }
  .side-panel {
    flex: 0 0 auto;
    flex-direction: row;
    overflow-x: auto;
  }
  .side-card { flex: 0 0 240px }
  .chat-shell { height: calc(100vh - 200px); min-height: 420px }
}

@media (max-width: 720px) {
  .chat-head, .chat-body, .chat-input, .quick-row { padding-left: 14px; padding-right: 14px }
  .bubble-row { max-width: 90% }
  .chat-head-actions { margin-left: 0; width: 100% }
}
</style>
