<template>
  <div class="consultation-chat-user">
    <div v-loading="loading" class="chat-wrapper">
      <div class="chat-container">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="header-left">
            <el-avatar :size="48" :src="appointment?.counselorAvatar" class="header-avatar">
              <el-icon :size="24"><User /></el-icon>
            </el-avatar>
            <div class="header-text">
              <h3>{{ appointment?.counselorName }}</h3>
              <div class="header-meta">
                <span class="online-dot" :class="{ on: isOnline }" />
                <span class="meta-status">{{ isOnline ? '在线咨询中' : '暂不在线' }}</span>
                <span class="meta-divider">|</span>
                <span class="meta-type">{{ getTypeLabel(appointment?.type) }}</span>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-button
              v-if="appointment?.type === 'video' || appointment?.type === 'voice'"
              :type="appointment?.type === 'video' ? 'primary' : 'success'"
              round
              size="small"
              :disabled="callStore.isBusy"
              @click="initiateCall"
              class="call-btn"
            >
              <el-icon :size="14"><VideoCamera v-if="appointment?.type === 'video'" /><Phone v-else /></el-icon>
              <span>{{ appointment?.type === 'video' ? '视频通话' : '语音通话' }}</span>
            </el-button>
            <div class="timer-badge">
              <el-icon :size="16"><Timer /></el-icon>
              <span>{{ formatDuration(elapsedTime) }}</span>
            </div>
            <el-button type="danger" plain size="small" round @click="handleEndConsultation">结束咨询</el-button>
          </div>
        </div>

        <!-- 咨询信息摘要 -->
        <div class="info-strip">
          <div class="info-chip">
            <span class="chip-label">预约编号</span>
            <span class="chip-value">{{ appointment?.appointmentNo }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">咨询方式</span>
            <span class="chip-value">{{ getTypeLabel(appointment?.type) }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">费用</span>
            <span class="chip-value price">¥{{ appointment?.price }}</span>
          </div>
        </div>

        <!-- 消息区域 -->
        <div ref="messagesContainer" class="messages-area">
          <!-- 空状态引导 -->
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-icon">💬</div>
            <p class="empty-title">咨询已开始</p>
            <p class="empty-hint">发送第一条消息，开始你的咨询之旅</p>
          </div>

          <template v-for="(msg, idx) in messages" :key="msg.id">
            <!-- 跳过信令消息 -->
            <template v-if="!isSignalMessage(msg)">
            <!-- 日期分隔 -->
            <div v-if="showDateDivider(idx, msg)" class="date-divider">
              <span>{{ formatDateDivider(msg.created_at) }}</span>
            </div>

            <!-- 系统消息 -->
            <div v-if="msg.message_type === 'system'" class="system-message">
              <span>{{ msg.content }}</span>
            </div>

            <!-- 普通消息 -->
            <div
              v-else-if="msg.message_type !== 'system'"
              class="message"
              :class="{ 'message-self': msg.sender_type === 'user' }"
            >
              <el-avatar
                :size="38"
                :src="msg.sender_type === 'user' ? currentUserAvatar : appointment?.counselorAvatar"
                class="msg-avatar"
              />
              <div class="message-body">
                <div class="message-meta">
                  <span class="msg-sender">{{ msg.sender_type === 'user' ? '我' : appointment?.counselorName }}</span>
                  <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                </div>
                <div v-if="msg.message_type === 'text'" class="message-bubble">{{ msg.content }}</div>
                <div v-else-if="msg.message_type === 'image'" class="message-image">
                  <el-image
                    :src="msg.content"
                    fit="cover"
                    :preview-src-list="[msg.content]"
                    class="image-thumb"
                  />
                </div>
                <div v-else-if="msg.message_type === 'file'" class="message-file">
                  <div class="file-icon-wrap">
                    <el-icon :size="20"><Document /></el-icon>
                  </div>
                  <span class="file-name">{{ msg.file_name || getFileName(msg.content) }}</span>
                  <el-button size="small" round @click="downloadFile(msg.file_url || msg.content)">下载</el-button>
                </div>
              </div>
            </div>
          </template>
          </template>

          <div v-if="isTyping" class="typing-indicator">
            <span class="typing-dots"><i></i><i></i><i></i></span>
            <span class="typing-text">对方正在输入...</span>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="toolbar">
            <el-upload
              :show-file-list="false"
              :before-upload="handleUploadImage"
              accept="image/*"
            >
              <el-button :icon="Picture" circle size="small" class="tool-btn" />
            </el-upload>
            <el-upload
              :show-file-list="false"
              :before-upload="handleUploadFile"
            >
              <el-button :icon="Folder" circle size="small" class="tool-btn" />
            </el-upload>
            <el-button
              :icon="Microphone"
              circle
              size="small"
              class="tool-btn"
              :class="{ recording: isRecording }"
              @click="toggleVoiceRecording"
            />
          </div>

          <div class="input-row">
            <el-input
              v-model="inputContent"
              type="textarea"
              :rows="3"
              placeholder="输入消息..."
              class="input-textarea"
              @keydown.enter.ctrl="sendMessage"
            />
            <el-button
              type="primary"
              :loading="sending"
              round
              class="send-btn"
              :disabled="!inputContent.trim()"
              @click="sendMessage"
            >
              <span v-if="!sending">发送</span>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 视频/语音通话（状态由 Pinia callStore 管理） -->
    <VideoCall />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, provide } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Picture, Folder, Microphone, Document, User, VideoCamera, Phone } from '@element-plus/icons-vue'
import { getMessages, sendMessage as sendMessageApi, uploadFile, endConsultation, isSignalMessage } from '@/api/consultation'
import { getUserAppointments } from '@/api/counselor'
import { useUserStore } from '@/stores/user'
import { useCallStore } from '@/stores/call'
import VideoCall from '@/components/VideoCall.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const appointmentId = route.params.id
const loading = ref(true)
const sending = ref(false)
const isRecording = ref(false)
const isTyping = ref(false)
const isOnline = ref(true)
const elapsedTime = ref(0)
const inputContent = ref('')
const messages = ref([])
const appointment = ref({})
const messagesContainer = ref(null)
const callStore = useCallStore()

const currentUserId = computed(() => userStore.user?.id)
const currentUserAvatar = computed(() => userStore.user?.avatar)
provide('currentUser', computed(() => userStore.userInfo))

let pollingTimer = null
let durationTimer = null

const loadAppointment = async () => {
  try {
    loading.value = true
    const res = await getUserAppointments({ page: 1, page_size: 100 })
    const orders = res.data.items || []
    const currentOrder = orders.find(o => o.id == appointmentId)

    if (currentOrder) {
      appointment.value = {
        id: currentOrder.id,
        appointmentNo: currentOrder.appointment_no,
        counselorName: currentOrder.counselor?.name || '咨询师',
        counselorAvatar: currentOrder.counselor?.avatar || '',
        type: currentOrder.consultation_type,
        description: currentOrder.problem_description || '暂无描述',
        status: currentOrder.status,
        price: currentOrder.price,
        counselor: currentOrder.counselor
      }
      document.title = `与${appointment.value.counselorName}的咨询 - SoulStation`
    } else {
      throw new Error('订单不存在')
    }
  } catch (error) {
    console.error('加载预约信息失败', error)
    ElMessage.error('加载预约信息失败')
    appointment.value = { counselorName: '咨询师', counselorAvatar: '', status: 'unknown' }
  } finally {
    loading.value = false
  }
}

const loadMessages = async () => {
  try {
    const haveMessages = messages.value.length > 0
    const params = {}
    if (haveMessages) {
      params.last_id = messages.value[messages.value.length - 1].id
    } else {
      params.limit = 2000
    }
    const res = await getMessages(appointmentId, params)
    const newMessages = res.data.items || []
    if (haveMessages) {
      messages.value = [...messages.value, ...newMessages]
    } else {
      messages.value = newMessages
    }
    // 检测来电
    checkIncomingCall(newMessages)
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
  }
}

const lastProcessedOfferId = ref(0)

const checkIncomingCall = (msgs) => {
  // 如果当前已在通话中或正在来电，不再处理新的邀请
  if (callStore.callStage !== 'idle') return
  const now = Date.now()
  const offerMsg = msgs.find(m =>
    m.message_type === 'webrtc_offer' &&
    m.sender_id !== currentUserId.value &&
    m.id > lastProcessedOfferId.value &&
    now - new Date(m.created_at).getTime() < 30000
  )
  if (offerMsg) {
    lastProcessedOfferId.value = offerMsg.id
    // 设置对方信息（从当前预约中获取）
    callStore.peerName = appointment.value?.counselorName || ''
    callStore.peerAvatar = appointment.value?.counselorAvatar || ''
    callStore.receiveOffer(offerMsg)
  }
}

const sendMessage = async () => {
  if (!inputContent.value.trim()) return
  try {
    sending.value = true
    await sendMessageApi(appointmentId, { content: inputContent.value, message_type: 'text' })
    inputContent.value = ''
    await loadMessages()
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const handleUploadImage = async (file) => {
  try {
    const res = await uploadFile(file)
    await sendMessageApi(appointmentId, { content: res.data.file_url, message_type: 'image' })
    await loadMessages()
  } catch { ElMessage.error('上传失败') }
  return false
}

const handleUploadFile = async (file) => {
  try {
    const res = await uploadFile(file)
    await sendMessageApi(appointmentId, { content: res.data.file_name, file_url: res.data.file_url, file_name: res.data.file_name, file_size: res.data.file_size, message_type: 'file' })
    await loadMessages()
  } catch { ElMessage.error('上传失败') }
  return false
}

const toggleVoiceRecording = () => {
  isRecording.value = !isRecording.value
  ElMessage.info(isRecording.value ? '开始录音' : '停止录音')
}

const handleEndConsultation = async () => {
  try {
    await ElMessageBox.confirm('确定要结束本次咨询吗？', '提示', { type: 'warning' })
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/counselor/orders')
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

/** 发起通话（用户端） */
const initiateCall = () => {
  if (callStore.isBusy) {
    ElMessage.warning('当前正在通话中，请先结束当前通话')
    return
  }
  callStore.initiateCall({
    appointmentId,
    type: appointment.value?.type || 'video',
    peerName: appointment.value?.counselorName || '',
    peerAvatar: appointment.value?.counselorAvatar || ''
  })
}

/** 通话结束时写入系统消息 */
const onCallEnded = (event) => {
  const { endReason, duration } = event.detail || {}
  const store = callStore
  let message = ''
  if (endReason === 'cancel') message = '视频通话已取消'
  else if (endReason === 'reject') message = '对方已拒绝'
  else if (endReason === 'timeout') message = '对方无应答'
  else if (endReason === 'remote_hangup') message = '对方已挂断'
  else if (endReason === 'hangup') message = '视频通话已结束'
  else if (endReason === 'network_lost') message = '通话已断开'
  else message = '通话已结束'

  if (duration > 0) {
    message += `，时长 ${store.formatDuration(duration)}`
  }

  messages.value.push({
    id: Date.now(),
    message_type: 'system',
    content: message,
    created_at: new Date().toISOString(),
    sender_id: 0,
    sender_type: 'system'
  })
  // 发送系统消息到后端，让双方聊天记录同步
  sendMessageApi(appointmentId, { message_type: 'system', content: message }).catch(() => {})
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const showDateDivider = (idx, msg) => {
  if (idx === 0) return true
  const prev = new Date(messages.value[idx - 1].created_at)
  const curr = new Date(msg.created_at)
  return prev.toDateString() !== curr.toDateString()
}

const formatDateDivider = (dateStr) => {
  const d = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const time = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  if (d.toDateString() === today.toDateString()) return `今天 ${time}`
  if (d.toDateString() === yesterday.toDateString()) return `昨天 ${time}`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${time}`
}

const formatTime = (time) => {
  const date = new Date(time)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

const getTypeLabel = (type) => {
  const labels = { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }
  return labels[type] || type
}

const getFileName = (url) => url.split('/').pop()

const downloadFile = (url) => { window.open(url, '_blank') }

const startPolling = () => { pollingTimer = setInterval(() => loadMessages(), 3000) }
const startTimer = () => { durationTimer = setInterval(() => { elapsedTime.value++ }, 1000) }

onMounted(async () => {
  await loadAppointment()
  await loadMessages()
  loading.value = false
  startPolling()
  startTimer()
  // 监听通话结束事件（由 callStore 通过 window 派发）
  window.addEventListener('call-ended', onCallEnded)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (durationTimer) clearInterval(durationTimer)
  window.removeEventListener('call-ended', onCallEnded)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.consultation-chat-user {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f0eb;
  padding-top: $header-height;
}

.chat-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 24px 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  min-height: 0;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 4px 32px rgba(107,82,68,0.1);
  overflow: hidden;
  min-height: 0;
}

// ── 头部 ──────────────────────────────────────────────
.chat-header {
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #faf7f4 0%, #fff 100%);
  border-bottom: 1px solid $border-lighter;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-avatar {
  box-shadow: 0 2px 12px rgba(107,82,68,0.15);
  border: 2px solid #fff;
}

.header-text {
  h3 {
    margin: 0 0 2px;
    font-size: 17px;
    font-weight: 700;
    color: $text-primary;
  }
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: $text-secondary;
}

.online-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #c0c4cc;
  flex-shrink: 0;

  &.on {
    background: #67c23a;
    box-shadow: 0 0 6px rgba(103,194,58,0.4);
  }
}

.meta-divider {
  color: $border-base;
}

.meta-type {
  color: $primary-color;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.timer-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  color: $primary-color;
  font-weight: 600;
  font-size: 14px;
  font-variant-numeric: tabular-nums;
  background: rgba(232,132,90,0.08);
  padding: 5px 14px;
  border-radius: 999px;
}

// ── 信息条 ────────────────────────────────────────────
.info-strip {
  display: flex;
  gap: 16px;
  padding: 10px 24px;
  background: #fdfbf9;
  border-bottom: 1px solid $border-lighter;
}

.info-chip {
  display: flex;
  flex-direction: column;
  gap: 1px;

  .chip-label {
    font-size: 10px;
    color: $text-placeholder;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
  }

  .chip-value {
    font-size: 13px;
    color: $text-primary;
    font-weight: 500;

    &.price {
      color: $primary-color;
      font-weight: 700;
    }
  }
}

// ── 消息区 ────────────────────────────────────────────
.messages-area {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
  background: #faf8f6;
  display: flex;
  flex-direction: column;
  gap: 4px;

  &::-webkit-scrollbar { width: 5px; }
  &::-webkit-scrollbar-thumb { background: #e0d8d0; border-radius: 10px; }
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $text-placeholder;

  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-title { font-size: 16px; font-weight: 600; color: $text-secondary; margin: 0 0 4px; }
  .empty-hint { font-size: 13px; margin: 0; }
}

// 日期分隔
.date-divider {
  display: flex;
  justify-content: center;
  padding: 16px 0 12px;

  span {
    font-size: 12px;
    color: $text-placeholder;
    background: #faf8f6;
    padding: 3px 16px;
    border-radius: 999px;
    border: 1px solid $border-lighter;
  }
}

// 系统消息
.system-message {
  text-align: center;
  padding: 8px 0;

  span {
    font-size: 12px;
    color: $text-placeholder;
    font-style: italic;
  }
}

// 消息
.message {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  animation: msgIn 0.25s ease-out;

  &.message-self {
    flex-direction: row-reverse;

    .message-body { align-items: flex-end; }
    .message-meta { flex-direction: row-reverse; }

    .message-bubble {
      background: linear-gradient(135deg, #e88a5a 0%, #d4754a 100%);
      color: #fff;
      border-radius: 18px 6px 18px 18px;
    }
  }
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
  flex-shrink: 0;
  margin-top: 14px;
  box-shadow: 0 1px 4px rgba(107,82,68,0.1);
}

.message-body {
  display: flex;
  flex-direction: column;
  max-width: 65%;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  padding: 0 4px;

  .msg-sender {
    font-size: 12px;
    color: $text-secondary;
    font-weight: 500;
  }

  .msg-time {
    font-size: 11px;
    color: $text-placeholder;
  }
}

.message-bubble {
  padding: 11px 16px;
  background: #fff;
  border-radius: 6px 18px 18px 18px;
  word-break: break-word;
  box-shadow: 0 1px 6px rgba(107,82,68,0.06);
  line-height: 1.65;
  font-size: 14px;
}

.message-image .image-thumb {
  max-width: 220px;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(107,82,68,0.12);
}

.message-file {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 1px 6px rgba(107,82,68,0.06);

  .file-icon-wrap {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: rgba(232,132,90,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: $primary-color;
  }

  .file-name {
    flex: 1;
    font-size: 13px;
    color: $text-primary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

// 输入中
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 12px;
  color: $text-secondary;
}

.typing-dots {
  display: flex;
  gap: 3px;

  i {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #c0c4cc;
    animation: dotPulse 1.2s infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes dotPulse {
  0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1.2); }
}

// ── 输入区 ────────────────────────────────────────────
.input-area {
  border-top: 1px solid $border-lighter;
  padding: 14px 24px 18px;
  background: #fff;
}

.toolbar {
  display: flex;
  gap: 4px;
  margin-bottom: 10px;
}

.tool-btn {
  border: none !important;
  background: transparent !important;
  color: $text-secondary;

  &:hover { color: $primary-color; background: rgba(232,132,90,0.08) !important; }
  &.recording { color: #f56c6c !important; background: rgba(245,108,108,0.1) !important; }
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-textarea {
  flex: 1;

  :deep(.el-textarea__inner) {
    border-radius: 14px;
    background: #faf8f6;
    border: 1px solid $border-lighter;
    resize: none;
    font-size: 14px;
    line-height: 1.6;
    padding: 10px 16px;

    &:focus {
      border-color: $primary-color;
      background: #fff;
      box-shadow: 0 0 0 3px rgba(232,132,90,0.08);
    }
  }
}

.send-btn {
  height: 40px;
  padding: 0 28px;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  align-self: flex-end;
}

.call-btn {
  font-weight: 600;
  span { margin-left: 4px; }
}

@media (max-width: 640px) {
  .chat-wrapper { padding: 0; }
  .chat-container { border-radius: 0; }
  .header-right { gap: 10px; }
  .timer-badge { display: none; }
  .info-strip { padding: 10px 16px; }
  .messages-area { padding: 16px; }
  .input-area { padding: 12px 16px 16px; }
  .message-body { max-width: 80%; }
}
</style>
