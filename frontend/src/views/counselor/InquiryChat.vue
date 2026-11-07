<template>
  <div class="ic-page">
    <div class="ic-wrap">

      <!-- 头部 -->
      <div class="ic-header">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <div class="ic-counselor-info" v-if="counselorInfo.counselor_name">
          <el-avatar :size="40" :src="counselorInfo.counselor_avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div>
            <div class="ic-name">{{ counselorInfo.counselor_name }}</div>
            <div class="ic-subtitle">{{ counselorInfo.counselor_title || '心理咨询师' }} · 预约前沟通</div>
          </div>
        </div>
        <el-button type="primary" size="small" round @click="goToAppointment">
          立即预约
        </el-button>
      </div>

      <!-- 消息区域 -->
      <div class="ic-messages" ref="msgBox">
        <div v-if="loading" class="ic-loading">
          <el-icon class="is-loading"><Loading /></el-icon> 加载中...
        </div>

        <template v-else>
          <div v-if="messages.length === 0" class="ic-empty">
            <el-icon :size="40"><ChatDotSquare /></el-icon>
            <p>向咨询师发送消息，了解他/她的擅长方向，也让对方更了解你的情况</p>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.id"
            class="ic-msg-row"
            :class="msg.sender_role === 'user' ? 'ic-self' : 'ic-other'"
          >
            <el-avatar
              v-if="msg.sender_role === 'counselor'"
              :size="36"
              :src="counselorInfo.counselor_avatar"
              class="ic-avatar"
            >
              <el-icon><User /></el-icon>
            </el-avatar>

            <div class="ic-bubble-wrap">
              <div class="ic-bubble">{{ msg.content }}</div>
              <div class="ic-time">{{ formatTime(msg.created_at) }}</div>
            </div>

            <el-avatar
              v-if="msg.sender_role === 'user'"
              :size="36"
              :src="userAvatar"
              class="ic-avatar"
            >
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
          </div>
        </template>
      </div>

      <!-- 输入区 -->
      <div class="ic-input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入消息…（Enter 发送，Shift+Enter 换行）"
          @keydown.enter.exact.prevent="send"
        />
        <el-button
          type="primary"
          :loading="sending"
          :disabled="!inputText.trim()"
          @click="send"
        >发送</el-button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User, UserFilled, ChatDotSquare, Loading } from '@element-plus/icons-vue'
import { startInquiry, getInquiryMessages, sendInquiryMessage } from '@/api/counselor'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const counselorId = route.params.counselorId
const inquiryId = ref(null)
const counselorInfo = ref({})
const messages = ref([])
const inputText = ref('')
const loading = ref(true)
const sending = ref(false)
const msgBox = ref(null)

const userAvatar = computed(() => userStore.user?.avatar)

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const scrollBottom = async () => {
  await nextTick()
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}

const loadMessages = async () => {
  if (!inquiryId.value) return
  try {
    const res = await getInquiryMessages(inquiryId.value)
    messages.value = res.data || []
    scrollBottom()
  } catch {
    ElMessage.error('加载消息失败')
  }
}

const send = async () => {
  const text = inputText.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    const res = await sendInquiryMessage(inquiryId.value, text)
    inputText.value = ''
    messages.value.push(res.data)
    scrollBottom()
  } catch {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const goBack = () => router.push(`/counselor/${counselorId}`)
const goToAppointment = () => router.push({ path: '/counselor/appointment', query: { counselorId } })

onMounted(async () => {
  try {
    const res = await startInquiry(counselorId)
    counselorInfo.value = res.data
    inquiryId.value = res.data.inquiry_id
    await loadMessages()
  } catch {
    ElMessage.error('无法建立沟通会话，请先登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.ic-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
  display: flex;
  justify-content: center;
}

.ic-wrap {
  width: 100%;
  max-width: 760px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - #{$header-height});
  background: #fff;
  border-left: 1px solid $border-lighter;
  border-right: 1px solid $border-lighter;
}

// 头部
.ic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid $border-lighter;
  background: #fff;
  flex-shrink: 0;
}

.ic-counselor-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.ic-name {
  font-weight: 600;
  font-size: 15px;
  color: $text-primary;
}

.ic-subtitle {
  font-size: 12px;
  color: $text-secondary;
}

// 消息列表
.ic-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 20px 10px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ic-loading, .ic-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: $text-secondary;
  gap: 12px;
  p { margin: 0; font-size: 13px; text-align: center; max-width: 280px; line-height: 1.6; }
}

// 消息行
.ic-msg-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;

  &.ic-self {
    flex-direction: row-reverse;
    .ic-bubble {
      background: $primary-color;
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .ic-time { text-align: right; }
  }

  &.ic-other .ic-bubble {
    background: #f4f4f5;
    color: $text-primary;
    border-bottom-left-radius: 4px;
  }
}

.ic-avatar { flex-shrink: 0; }

.ic-bubble-wrap { max-width: 65%; }

.ic-bubble {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.ic-time {
  font-size: 11px;
  color: $text-secondary;
  margin-top: 4px;
  padding: 0 4px;
}

// 输入区
.ic-input-area {
  padding: 12px 16px;
  border-top: 1px solid $border-lighter;
  background: #fff;
  display: flex;
  gap: 10px;
  align-items: flex-end;
  flex-shrink: 0;

  .el-textarea { flex: 1; }
  .el-button { align-self: flex-end; }
}
</style>
