<template>
  <div class="chat-detail">

    <div class="container">
      <!-- 顶部操作栏 -->
      <div class="detail-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>对话详情</h2>
        <el-dropdown :icon="MoreFilled" @command="handleCommand">
          <el-button circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="export">
                <el-icon><Download /></el-icon>
                导出对话
              </el-dropdown-item>
              <el-dropdown-item command="regenerate">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided>
                <el-icon><Delete /></el-icon>
                删除对话
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 对话信息 -->
      <el-card class="chat-info-card">
        <div class="info-row">
          <span class="label">对话标题：</span>
          <span class="value">{{ chatInfo.title }}</span>
          <el-button text :icon="Edit" @click="editTitle">编辑</el-button>
        </div>
        <div class="info-row">
          <span class="label">标签：</span>
          <div class="tags">
            <el-tag
              v-for="tag in chatInfo.tags"
              :key="tag.id"
              :color="tag.color"
              closable
              @close="removeTag(tag.id)"
            >
              {{ tag.name }}
            </el-tag>
            <el-button
              text
              :icon="Plus"
              size="small"
              @click="showAddTagDialog"
            >
              添加标签
            </el-button>
          </div>
        </div>
        <div class="info-row">
          <span class="label">创建时间：</span>
          <span class="value">{{ formatDateTime(chatInfo.createdAt) }}</span>
        </div>
        <div class="info-row">
          <span class="label">消息数量：</span>
          <span class="value">{{ messages.length }} 条</span>
        </div>
      </el-card>

      <!-- 对话内容 -->
      <el-card class="messages-card">
        <template #header>
          <span>完整对话记录</span>
        </template>

        <div class="message-list" ref="messageListRef">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-item"
            :class="message.role"
          >
            <!-- AI消息 -->
            <div v-if="message.role === 'assistant'" class="message-assistant">
              <div class="message-content">
                <div class="message-bubble">
                  <div class="message-text" v-html="renderMarkdown(message.content)"></div>
                  <span class="message-time">{{ formatDateTime(message.timestamp) }}</span>
                </div>
              </div>
            </div>

            <!-- 用户消息 -->
            <div v-else class="message-user">
              <div class="message-content">
                <div class="message-bubble">
                  <div class="message-text">{{ message.content }}</div>
                  <span class="message-time">{{ formatDateTime(message.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 添加标签对话框 -->
    <el-dialog
      v-model="addTagDialogVisible"
      title="添加标签"
      width="400px"
    >
      <el-select
        v-model="selectedTagId"
        placeholder="选择标签"
        style="width: 100%"
      >
        <el-option
          v-for="tag in availableTags"
          :key="tag.id"
          :label="tag.name"
          :value="tag.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="addTagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addTag">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  MoreFilled,
  Download,
  Refresh,
  Delete,
  Edit,
  Plus,
  ChatDotSquare,
  User
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getChatDetail, deleteChat, updateChatTitle, addTagToChat } from '@/api/chat'
import { getTags } from '@/api/chat'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 对话信息
const chatInfo = ref({
  id: '',
  title: '',
  createdAt: null,
  tags: []
})

// 消息列表
const messages = ref([])
const messageListRef = ref(null)

// 所有标签
const allTags = ref([])

// 可用标签（未添加的）
const availableTags = computed(() => {
  const addedTagIds = chatInfo.value.tags.map(t => t.id)
  return allTags.value.filter(tag => !addedTagIds.includes(tag.id))
})

// 添加标签对话框
const addTagDialogVisible = ref(false)
const selectedTagId = ref('')

// 加载对话详情
const loadChatDetail = async () => {
  try {
    const chatId = route.params.id
    const res = await getChatDetail(chatId)
    chatInfo.value = res.data.chat
    messages.value = res.data.messages || []
  } catch (error) {
    console.error('加载对话详情失败:', error)
    ElMessage.error('加载失败')
  }
}

// 加载标签列表
const loadTags = async () => {
  try {
    const res = await getTags()
    allTags.value = res.data || []
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 编辑标题
const editTitle = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的对话标题', '编辑标题', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: chatInfo.value.title
    })

    await updateChatTitle(chatInfo.value.id, value)
    chatInfo.value.title = value
    ElMessage.success('修改成功')
  } catch {
    // 取消编辑
  }
}

// 显示添加标签对话框
const showAddTagDialog = () => {
  selectedTagId.value = ''
  addTagDialogVisible.value = true
}

// 添加标签
const addTag = async () => {
  if (!selectedTagId.value) {
    ElMessage.warning('请选择标签')
    return
  }

  try {
    await addTagToChat(chatInfo.value.id, selectedTagId.value)

    // 更新本地标签列表
    const tag = allTags.value.find(t => t.id === selectedTagId.value)
    if (tag) {
      chatInfo.value.tags.push(tag)
    }

    ElMessage.success('添加成功')
    addTagDialogVisible.value = false
  } catch (error) {
    console.error('添加标签失败:', error)
  }
}

// 移除标签
const removeTag = async (tagId) => {
  // 这里应该调用移除标签的API
  const index = chatInfo.value.tags.findIndex(t => t.id === tagId)
  if (index > -1) {
    chatInfo.value.tags.splice(index, 1)
    ElMessage.success('移除成功')
  }
}

// 处理命令
const handleCommand = async (command) => {
  switch (command) {
    case 'export':
      await exportChat()
      break
    case 'regenerate':
      await regenerateChat()
      break
    case 'delete':
      await deleteChatById()
      break
  }
}

// 导出对话
const exportChat = async () => {
  try {
    const { value } = await ElMessageBox.confirm(
      '选择导出格式',
      '导出对话',
      {
        confirmButtonText: 'PDF',
        cancelButtonText: 'TXT',
        distinguishCancelAndClose: true,
        type: 'info'
      }
    )

    // 这里应该调用导出API
    ElMessage.success(value === 'confirm' ? '导出为PDF' : '导出为TXT')
  } catch (action) {
    if (action === 'cancel') {
      ElMessage.success('导出为TXT')
    }
  }
}

// 重新生成
const regenerateChat = () => {
  ElMessage.info('重新生成功能开发中...')
}

// 删除对话
const deleteChatById = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？删除后不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteChat(chatInfo.value.id)
    ElMessage.success('删除成功')
    goBack()
  } catch {
    // 取消删除
  }
}

// 返回
const goBack = () => {
  router.push('/chat')
}

// 渲染Markdown（简化版）
const renderMarkdown = (content) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

// 组件挂载
onMounted(() => {
  loadChatDetail()
  loadTags()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.chat-detail {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;

  h2 {
    flex: 1;
    margin: 0;
    font-weight: 700;
    color: $text-primary;
  }
}

.chat-info-card {
  margin-bottom: 24px;
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__body) { padding: 8px 24px; }

  .info-row {
    display: flex;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid $border-lighter;

    &:last-child { border-bottom: none; }

    .label { font-weight: 600; color: $text-regular; min-width: 100px; font-size: 14px; }
    .value { color: $text-regular; flex: 1; font-size: 14px; }
    .tags { flex: 1; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  }
}

.messages-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  .message-list {
    max-height: 600px;
    overflow-y: auto;
    padding: 8px 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .message-item {
    &.assistant .message-content {
      display: flex;
      justify-content: flex-start;

      .message-bubble {
        background: $bg-page;
        color: $text-primary;
        border-radius: 4px 18px 18px 18px;
        border: 1px solid $border-lighter;
      }
    }

    &.user .message-content {
      display: flex;
      justify-content: flex-end;

      .message-bubble {
        background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%);
        color: white;
        border-radius: 18px 4px 18px 18px;
      }
    }
  }

  .message-bubble {
    padding: 12px 16px;
    max-width: 80%;
    word-break: break-word;
    box-shadow: 0 2px 8px rgba(107,82,68,0.06);
  }

  .message-text { line-height: 1.7; }

  .message-time {
    font-size: 11px;
    color: $text-secondary;
    margin-top: 4px;
    display: block;

    &.user-time { text-align: right; color: rgba(255,255,255,0.75); }
  }
}

@media (max-width: $breakpoint-md) {
  .container { padding: 16px; }
  .message-bubble { max-width: 90%; }
}
</style>
