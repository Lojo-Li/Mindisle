<template>
<div class="chat-page">
<section class="chat-view" data-view="chat" ref="rootEl">

  <!-- 加载中 -->
  <div v-if="loading" class="card">
    <div class="empty">
      <div class="empty-mark">◌</div>
      <div>正在进入咨询室…</div>
    </div>
  </div>

  <!-- 加载失败 -->
  <div v-else-if="loadError" class="card">
    <div class="empty">
      <div class="empty-mark">!</div>
      <div class="empty-title">无法进入咨询室</div>
      <div class="empty-sub">{{ loadError }}</div>
      <button class="btn btn-ghost btn-sm" style="margin-top:14px" @click="goBack">返回我的预约</button>
    </div>
  </div>

  <!-- 咨询室 -->
  <div v-else class="chat-shell">

    <!-- 头部：咨询师信息 + 通话 + 计时 + 结束 -->
    <div class="chat-head">
      <div class="chat-peer">
        <div class="chat-avatar">{{ initialOf(counselorName) }}</div>
        <div class="chat-peer-text">
          <h3>
            {{ counselorName }}
            <span class="tag" :class="statusClass(appt.status)">{{ statusLabel(appt.status) }}</span>
          </h3>
          <div class="chat-peer-meta">
            <span class="online-dot" :class="{ on: isOnline }" />
            <span>{{ isOnline ? '在线咨询中' : '暂不在线' }}</span>
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
        <button
          v-if="canCall"
          class="btn btn-soft btn-sm"
          :disabled="callStore.isBusy"
          @click="initiateCall"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="margin-right:5px">
            <path v-if="appt.consultation_type === 'video'" d="M15.5 9.5l5-3v11l-5-3"/>
            <rect v-if="appt.consultation_type === 'video'" x="3.5" y="7" width="12" height="10" rx="2.5"/>
            <path v-else d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 6 6l1.5-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/>
          </svg>
          {{ appt.consultation_type === 'video' ? '视频通话' : '语音通话' }}
        </button>
        <button
          v-if="activeNow"
          class="btn btn-ghost btn-sm"
          @click="handleEndConsultation"
        >结束咨询</button>
      </div>
    </div>

    <!-- 预约信息条 -->
    <div class="info-strip">
      <span class="info-item">预约编号 <b>{{ appt.appointment_no || '—' }}</b></span>
      <span class="info-item">预约时间 <b>{{ fmtDate(appt.appointment_date) }}</b></span>
      <span v-if="appt.problem_description" class="info-item info-note">你的诉求 <b>{{ appt.problem_description }}</b></span>
    </div>

    <!-- 消息区 -->
    <div ref="messagesEl" class="chat-body">
      <div v-if="!visibleMessages.length" class="chat-empty">
        <div class="empty-mark">✧</div>
        <div class="empty-title">咨询已开始</div>
        <div class="empty-sub">发送第一条消息，开始你的咨询之旅。</div>
      </div>

      <template v-for="(msg, idx) in visibleMessages" :key="msg.id">
        <!-- 日期分隔 -->
        <div v-if="showDateDivider(idx)" class="date-sep">
          <span>{{ fmtDateDivider(msg.created_at) }}</span>
        </div>

        <!-- 系统消息 -->
        <div v-if="msg.message_type === 'system'" class="system-line">
          <span>{{ msg.content }}</span>
        </div>

        <!-- 普通消息 -->
        <div v-else class="bubble-row" :class="{ self: msg.sender_type === 'user' }">
          <div class="bubble-avatar">{{ (msg.sender_type === 'user' ? '我' : initialOf(counselorName)) }}</div>
          <div class="bubble-main">
            <div class="bubble-meta">
              <span v-if="msg.sender_type !== 'user'">{{ counselorName }}</span>
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
        <button
          class="tool-btn"
          :class="{ recording: isRecording }"
          title="语音输入"
          @click="toggleVoiceRecording"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
            <rect x="9" y="2.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.5"/>
          </svg>
        </button>
        <span v-if="uploading" class="upload-hint">上传中…</span>
      </div>

      <div class="input-row">
        <textarea
          v-model="inputContent"
          class="input-textarea"
          rows="3"
          placeholder="说点什么…（Enter 发送，Shift + Enter 换行）"
          @keydown.enter.exact.prevent="sendMessage"
        ></textarea>
        <button
          class="btn btn-primary send-btn"
          :disabled="!inputContent.trim() || sending"
          @click="sendMessage"
        >{{ sending ? '发送中…' : '发送' }}</button>
      </div>
    </div>

    <!-- 已结束提示 -->
    <div v-else class="chat-closed">
      <span>本次咨询已{{ statusLabel(appt.status) }}</span>
      <button class="btn btn-ghost btn-sm" @click="goBack">返回我的预约</button>
    </div>

  </div>

  <!-- 图片预览 -->
  <div v-if="previewSrc" class="overlay open" @click.self="previewSrc = ''">
    <img :src="previewSrc" class="preview-img" alt="预览" />
  </div>

  <!-- 视频/语音通话（状态由 Pinia callStore 管理） -->
  <VideoCall />
</section>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMessages, sendMessage as sendMessageApi, uploadFile,
  endConsultation, isSignalMessage
} from '@/api/consultation'
import { getUserAppointments } from '@/api/counselor'
import { useCallStore } from '@/stores/call'
import VideoCall from '@/components/VideoCall.vue'

const route = useRoute()
const router = useRouter()
const callStore = useCallStore()

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
const isRecording = ref(false)
const previewSrc = ref('')
const isOnline = ref(true)
const elapsedTime = ref(0)

let pollTimer = null
let tickTimer = null

// ---------- 计算 ----------
const counselorName = computed(() => appt.value?.counselor?.name || appt.value?.counselor_name || '咨询师')

const activeNow = computed(() => ['confirmed', 'in_progress'].includes(appt.value?.status))

const canCall = computed(() =>
  activeNow.value && ['video', 'voice'].includes(appt.value?.consultation_type)
)

// 过滤掉信令消息（WebRTC 用）
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
  return { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }[t] || '咨询'
}

function initialOf(n) { return String(n || '咨').slice(0, 1) }

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
  const now = new Date()
  const same = d.toDateString() === now.toDateString()
  if (same) return '今天'
  const w = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${w}`
}

function showDateDivider(idx) {
  if (idx === 0) return true
  const cur = visibleMessages.value[idx]
  const prev = visibleMessages.value[idx - 1]
  const a = parseDate(cur?.created_at)
  const b = parseDate(prev?.created_at)
  if (!a || !b) return false
  return a.toDateString() !== b.toDateString()
}

function fileNameOf(url) {
  if (!url) return '附件'
  try {
    const p = String(url).split('?')[0].split('/')
    return decodeURIComponent(p[p.length - 1] || '附件')
  } catch (e) {
    return '附件'
  }
}

function formatDuration(sec) {
  const s = Math.max(0, Number(sec) || 0)
  const m = Math.floor(s / 60)
  const r = s % 60
  const h = Math.floor(m / 60)
  const mm = m % 60
  if (h > 0) return `${h}:${String(mm).padStart(2, '0')}:${String(r).padStart(2, '0')}`
  return `${String(mm).padStart(2, '0')}:${String(r).padStart(2, '0')}`
}

// ---------- 数据 ----------
async function loadAppointment() {
  const res = await getUserAppointments({ page: 1, page_size: 100 })
  const items = res?.data?.items || []
  const cur = items.find(o => String(o.id) === String(appointmentId))
  if (!cur) throw new Error('预约不存在，或你没有权限查看')
  appt.value = cur
  document.title = `与${counselorName.value}的咨询 - 心屿 Mindisle`
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
  } catch (e) {
    // 轮询失败静默处理，不打扰用户
  }
}

function scrollToBottom() {
  const el = messagesEl.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

function startTimers() {
  stopTimers()
  // 消息轮询 3 秒
  pollTimer = setInterval(() => loadMessages(), 3000)
  // 会话计时
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
    // 首条消息会让后端把 confirmed 隐式推到 in_progress，刷新状态
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

function toggleVoiceRecording() {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    ElMessage.info('语音输入已开启（占位功能，可接入浏览器语音识别）')
  }
}

function initiateCall() {
  if (callStore.isBusy) {
    ElMessage.warning('当前正在通话中，请先结束当前通话')
    return
  }
  callStore.initiateCall({
    appointmentId,
    type: appt.value?.consultation_type || 'video',
    peerName: counselorName.value,
    peerAvatar: appt.value?.counselor?.avatar || ''
  })
}

function downloadFile(url) {
  if (!url) return
  window.open(url, '_blank')
}

async function handleEndConsultation() {
  try {
    await ElMessageBox.confirm(
      '确定要结束本次咨询吗？结束后将进入评价环节。',
      '结束咨询',
      { confirmButtonText: '确定结束', cancelButtonText: '继续咨询', type: 'warning' }
    )
  } catch (e) {
    return
  }
  try {
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/workspace/appointments')
  } catch (e) {
    ElMessage.error('操作失败，请重试')
  }
}

function goBack() {
  router.push('/workspace/appointments')
}
</script>

<style scoped>
/* 独立页：不依赖 MindisleShell 的 .mi-portal 容器，
   这里把心屿设计变量与基础排版就地定义，保证与主界面视觉一致 */
.chat-page {
  --bg: #F6F5F1;
  --surface: #FFFFFF;
  --surface-2: #FBFAF7;
  --ink: #1B2A2C;
  --ink-2: #56696D;
  --ink-3: #94A4A6;
  --sea: #2E6E68;
  --sea-deep: #22524E;
  --sea-soft: #E2EFEC;
  --lamp: #D9982F;
  --lamp-soft: #FAEFD7;
  --sand: #F1EBE0;
  --rose-soft: #F7E7E4;
  --line: #E7E5DE;
  --shadow-s: 0 1px 2px rgba(27, 42, 44, .05);

  min-height: 100vh;
  background: var(--bg);
  padding: 26px 32px 32px;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: var(--ink);
}

.chat-page *,
.chat-page *::before,
.chat-page *::after { box-sizing: border-box; }

.chat-view {
  max-width: 1180px;
  margin: 0 auto;
}

/* 心屿通用组件（就地实现，与 MindisleShell 保持一致） */
.chat-page .card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-s);
}

.chat-page .empty {
  text-align: center;
  padding: 46px 20px;
  color: var(--ink-3);
  font-size: 13px;
}

.empty-mark {
  font-size: 26px;
  color: var(--sea);
  opacity: .42;
  margin-bottom: 10px;
}

.empty-title {
  font-size: 14px;
  font-weight: 590;
  color: var(--ink);
  letter-spacing: .2px;
}

.empty-sub {
  margin-top: 6px;
  font-size: 12.5px;
  color: var(--ink-3);
}

.chat-page .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  padding: 0 16px;
  border-radius: 11px;
  border: 1px solid transparent;
  font-size: 13.5px;
  font-weight: 540;
  font-family: inherit;
  cursor: pointer;
  transition: transform .18s, box-shadow .18s, border-color .18s, background .18s;
  white-space: nowrap;
}

.chat-page .btn-primary {
  background: linear-gradient(160deg, #357B74, #22524E);
  color: #fff;
  box-shadow: 0 8px 20px -12px rgba(34, 82, 78, .9);
}

.chat-page .btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 26px -12px rgba(34, 82, 78, .85);
}

.chat-page .btn-ghost {
  background: var(--surface);
  border-color: var(--line);
  color: var(--ink-2);
}

.chat-page .btn-ghost:hover:not(:disabled) {
  border-color: #CFDCD9;
  color: var(--ink);
  box-shadow: var(--shadow-s);
}

.chat-page .btn-soft {
  background: var(--sea-soft);
  color: var(--sea-deep);
}

.chat-page .btn-soft:hover:not(:disabled) {
  background: #D6E8E4;
}

.chat-page .btn-sm {
  height: 32px;
  padding: 0 13px;
  font-size: 12.5px;
  border-radius: 9px;
}

.chat-page .tag {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  padding: 2.5px 9px;
  border-radius: 20px;
  background: var(--sand);
  color: #8A7A62;
  letter-spacing: .3px;
  font-weight: 520;
}

.chat-page .tag.sea { background: var(--sea-soft); color: var(--sea-deep) }
.chat-page .tag.lamp { background: var(--lamp-soft); color: #8F6316 }
.chat-page .tag.rose { background: var(--rose-soft); color: #96574E }

.chat-page .overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(20, 34, 36, .62);
  backdrop-filter: blur(3px);
}

/* ---------- 聊天主体 ---------- */
.chat-shell {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 84px);
  min-height: 520px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-s);
  overflow: hidden;
}

/* ---------- 头部 ---------- */
.chat-head {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 22px;
  border-bottom: 1px solid var(--line);
  background: var(--surface-2, #FBFAF7);
  flex-wrap: wrap;
}

.chat-peer {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 0;
}

.chat-avatar {
  flex: 0 0 auto;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(160deg, #357B74, #22524E);
}

.chat-peer-text h3 {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: .2px;
}

.chat-peer-meta {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 5px;
  font-size: 12px;
  color: var(--ink-3);
}

.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C3CFCE;
}

.online-dot.on {
  background: #4E9A6A;
  box-shadow: 0 0 0 3px rgba(78, 154, 106, .14);
}

.dot-sep { opacity: .5 }

.chat-head-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 9px;
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

/* ---------- 信息条 ---------- */
.info-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 11px 22px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  font-size: 12px;
  color: var(--ink-3);
}

.info-item b {
  font-weight: 560;
  color: var(--ink-2);
  margin-left: 3px;
}

.info-note {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 消息区 ---------- */
.chat-body {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background:
    radial-gradient(circle at 18% 12%, rgba(46, 110, 104, .035), transparent 42%),
    var(--surface);
}

.chat-body::-webkit-scrollbar { width: 8px }
.chat-body::-webkit-scrollbar-thumb {
  background: #DFE5E3;
  border-radius: 8px;
}

.chat-empty {
  margin: auto;
  text-align: center;
  padding: 40px 20px;
}

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
  max-width: 78%;
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
  max-width: 78%;
}

.bubble-row.self {
  flex-direction: row-reverse;
  margin-left: auto;
}

.bubble-avatar {
  flex: 0 0 auto;
  width: 32px;
  height: 32px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12.5px;
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
  gap: 5px;
}

.bubble-row.self .bubble-main {
  align-items: flex-end;
}

.bubble-meta {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11.5px;
  color: var(--ink-3);
}

.bubble-time {
  font-variant-numeric: tabular-nums;
  opacity: .8;
}

.bubble {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 14px 14px 14px 4px;
  background: var(--surface-2, #FBFAF7);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 13.5px;
  line-height: 1.85;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
}

.bubble-row.self .bubble {
  border-radius: 14px 14px 4px 14px;
  background: linear-gradient(160deg, #357B74, #22524E);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 8px 20px -14px rgba(34, 82, 78, .9);
}

.bubble-img-wrap {
  max-width: 260px;
}

.bubble-img {
  max-width: 100%;
  max-height: 260px;
  border-radius: 13px;
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
  border-radius: 13px;
  background: var(--surface-2, #FBFAF7);
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
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 输入区 ---------- */
.chat-input {
  border-top: 1px solid var(--line);
  padding: 13px 22px 18px;
  background: var(--surface);
}

.input-tools {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 9px;
}

.tool-btn {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-3);
  cursor: pointer;
  transition: background .18s, color .18s, border-color .18s;
}

.tool-btn:hover {
  background: var(--surface-2, #FBFAF7);
  border-color: var(--line);
  color: var(--ink);
}

.tool-btn.recording {
  background: var(--rose-soft);
  color: #96574E;
}

.upload-hint {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-left: 4px;
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-textarea {
  flex: 1 1 auto;
  min-height: 72px;
  max-height: 160px;
  padding: 11px 14px;
  border-radius: 13px;
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

.input-textarea::placeholder {
  color: var(--ink-3);
}

.send-btn {
  height: 44px;
  padding: 0 22px;
  flex: 0 0 auto;
}

.send-btn:disabled {
  opacity: .45;
  cursor: not-allowed;
  box-shadow: none;
}

/* ---------- 已结束 ---------- */
.chat-closed {
  border-top: 1px solid var(--line);
  padding: 18px 22px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 13px;
  color: var(--ink-3);
  background: var(--surface-2, #FBFAF7);
}

/* ---------- 预览 ---------- */
.preview-img {
  max-width: 88vw;
  max-height: 88vh;
  border-radius: 14px;
  box-shadow: 0 24px 60px -20px rgba(27, 42, 44, .5);
}

@media (max-width: 720px) {
  .chat-shell {
    height: calc(100vh - 96px);
    border-radius: 14px;
  }
  .chat-head, .chat-body, .chat-input {
    padding-left: 14px;
    padding-right: 14px;
  }
  .bubble-row { max-width: 92% }
  .chat-head-actions { margin-left: 0; width: 100%; }
}
</style>
