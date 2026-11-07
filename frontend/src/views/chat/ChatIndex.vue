<template>
  <div class="chat-index">
    <!-- 顶部导航栏?-->
    <div class="chat-header">
      <div class="header-left">
        <!-- 返回按钮 -->
        <el-button
          :icon="ArrowLeft"
          circle
          size="small"
          @click="goBack"
          class="back-button"
        />
        <el-icon :size="24" color="#e8845a">
          <ChatDotSquare />
        </el-icon>
        <h2>智能心理问答</h2>
      </div>
      <div class="header-center">
        <!-- 对话信息 -->
        <div v-if="currentChatId" class="current-chat-info">
          <span class="chat-title-display">{{ currentChatTitle }}</span>
          <el-button
            text
            :icon="Edit"
            size="small"
            @click="editChatTitle(currentChatId)"
          />
        </div>
      </div>
      <div class="header-right">
        <!-- 功能按钮区?-->
        <div class="header-actions">
          <el-tooltip content="历史记录" placement="bottom">
            <el-button circle :icon="Clock" @click="showHistory = true" />
          </el-tooltip>
          <el-tooltip content="标签管理" placement="bottom">
            <el-button circle :icon="PriceTag" @click="showTagManager = true" />
          </el-tooltip>
          <el-tooltip content="导出对话" placement="bottom">
            <el-button circle :icon="Download" @click="exportChat" />
          </el-tooltip>
          <el-tooltip content="清空对话" placement="bottom">
            <el-button circle :icon="Delete" @click="clearChat" />
          </el-tooltip>
          <el-tooltip content="通知" placement="bottom">
            <el-button circle :icon="Bell" />
          </el-tooltip>
        </div>
        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <el-avatar :size="36" :src="userInfo?.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="chat-container">
      <!-- 左侧历史对话列表 -->
      <div class="chat-sidebar">
        <!-- 新建对话按钮 -->
        <div class="new-chat-btn">
          <el-button type="primary" :icon="Plus" @click="createNewChat">
            新建对话
          </el-button>
        </div>

        <!-- 搜索框?-->
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索对话..."
            prefix-icon="Search"
            clearable
            size="small"
          />
        </div>

        <!-- 标签筛选?-->
        <div class="tag-filter">
          <el-select
            v-model="selectedTag"
            placeholder="选择标签"
            clearable
            size="small"
            style="width: 100%"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </div>

        <!-- 对话列表 -->
        <div class="chat-list">
          <el-skeleton v-if="loadingChats" :rows="5" animated />
          <div v-else>
            <div
              v-for="(group, groupIndex) in groupedChats"
              :key="groupIndex"
              class="chat-group"
            >
              <div class="time-group-header">{{ group.label }}</div>
              <div
                v-for="chat in group.chats"
                :key="chat.id"
                class="chat-item"
                :class="{ active: currentChatId === chat.id }"
                @click="selectChat(chat.id)"
              >
                <div class="chat-item-content">
                  <div class="chat-title-row">
                    <h4 class="chat-title">{{ chat.title }}</h4>
                  </div>
                  <p class="chat-preview">{{ chat.lastMessage }}</p>
                  <div class="chat-tags-row" v-if="chat.tags && chat.tags.length > 0">
                    <TransitionGroup name="tag" tag="div" class="chat-tags-inner">
                      <el-tag
                        v-for="tag in chat.tags"
                        :key="tag.id"
                        :color="tag.color"
                        size="small"
                        class="chat-tag-item"
                      >
                        {{ tag.name }}
                      </el-tag>
                    </TransitionGroup>
                  </div>
                </div>
                <div class="chat-item-actions">
                  <el-dropdown
                    trigger="click"
                    @command="(cmd) => handleChatCommand(cmd, chat.id)"
                    @click.stop
                  >
                    <el-icon class="more-icon"><MoreFilled /></el-icon>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit">
                          <el-icon><Edit /></el-icon>
                          编辑标题
                        </el-dropdown-item>
                        <el-dropdown-item command="delete" divided>
                          <el-icon><Delete /></el-icon>
                          删除对话
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <el-popover
                    :visible="tagPopoverChatId === chat.id"
                    placement="right"
                    :width="200"
                    :teleported="false"
                    trigger="manual"
                  >
                    <template #reference>
                      <el-icon
                        class="tag-assign-icon"
                        @click.stop="toggleTagPopover(chat.id)"
                      >
                        <PriceTag />
                      </el-icon>
                    </template>
                    <div class="tag-popover-content" @click.stop>
                      <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #5a4a3a;">为对话分配标签</div>
                      <el-checkbox-group
                        :model-value="chat.tags ? chat.tags.map(t => t.id) : []"
                        @change="(val) => onChatTagsChange(val, chat.id)"
                      >
                        <div v-for="tag in tags" :key="tag.id" style="margin-bottom: 6px;">
                          <el-checkbox :label="tag.id" :value="tag.id">
                            <el-tag :color="tag.color" size="small" style="cursor: pointer;">{{ tag.name }}</el-tag>
                          </el-checkbox>
                        </div>
                      </el-checkbox-group>
                      <div v-if="tags.length === 0" style="color: #999; font-size: 12px; text-align: center; padding: 8px 0;">
                        暂无标签，请先在标签管理中创建
                      </div>
                    </div>
                  </el-popover>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧对话区域 -->
      <div class="chat-main">
        <!-- 未选择对话时的空状态 -->
        <div v-if="!currentChatId" class="chat-empty">
          <div style="text-align: center; padding: 80px 20px;">
            <h3 style="margin-bottom: 12px; color: #5a4a3a; font-size: 18px; font-weight: 500;">选择一个对话或创建新对话</h3>
            <p style="margin-bottom: 24px; color: #999; font-size: 14px;">AI助手随时为您提供帮助</p>
            <el-button type="primary" :icon="Plus" @click="createNewChat">
              开始新对话
            </el-button>
          </div>
        </div>

        <!-- 对话内容 -->
        <div v-else class="chat-content">
          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <!-- AI消息 -->
              <div v-if="message.role === 'assistant'" class="message-assistant">
                <div class="message-bubble">
                  <div class="message-text" v-html="renderMarkdown(message.content)"></div>
                </div>
              </div>

              <!-- 用户消息 -->
              <div v-else class="message-user">
                <div class="message-bubble">
                  <div class="message-text">{{ message.content }}</div>
                </div>
              </div>
            </div>

            <!-- 加载中 -->
            <div v-if="loadingMessages" class="message-item assistant">
              <div class="message-assistant">
                <div class="message-bubble typing-bubble">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <!-- 工具栏-->
            <div class="input-toolbar">
              <VoiceRecorder @transcription-result="handleTranscriptionResult" />
            </div>

            <!-- 输入框-->
            <div class="input-box">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 6 }"
                placeholder="输入您的问题...（Enter发送，Shift+Enter换行）"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact.prevent="() => inputMessage += '\n'"
                resize="none"
              />
              <el-button
                type="primary"
                :icon="Promotion"
                circle
                :loading="sendingMessage"
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              />
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- 标签管理对话框?-->
    <el-dialog
      v-model="showTagManager"
      title="标签管理"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="tag-manager">
        <!-- 创建新标签 -->
        <div class="tag-create">
          <h4>创建新标签</h4>
          <el-input
            v-model="newTagName"
            placeholder="标签名称"
            size="small"
            style="width: 200px; margin-right: 10px"
          />
          <el-color-picker v-model="newTagColor" size="small" />
          <el-button type="primary" size="small" @click="createTag" :icon="Plus">
            添加
          </el-button>
        </div>

        <!-- 标签列表 -->
        <div class="tag-list">
          <h4>我的标签</h4>
          <el-empty v-if="tags.length === 0" description="暂无标签" :image-size="80" />
          <div v-else class="tag-items">
            <el-tag
              v-for="tag in tags"
              :key="tag.id"
              closable
              :color="tag.color"
              @close="deleteTag(tag.id)"
              size="large"
              style="margin: 5px"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 历史记录抽屉 -->
    <el-drawer
      v-model="showHistory"
      title="历史对话"
      size="380px"
      :with-header="true"
    >
      <ChatHistory @select="handleHistorySelect" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onBeforeUnmount, reactive, triggerRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotSquare,
  Plus,
  Search,
  Bell,
  User,
  SwitchButton,
  MoreFilled,
  Edit,
  Delete,
  Microphone,
  Promotion,
  ArrowLeft,
  PriceTag,
  Download,
  Setting,
  DocumentCopy,
  Clock
} from '@element-plus/icons-vue'
import ChatHistory from '@/components/chat/ChatHistory.vue'
import { useUserStore } from '@/stores/user'
import { getChatList, createChat, deleteChat, updateChatTitle, sendMessage as sendMessageApi, sendMessageStream, getChatDetail, addTagToChat, removeTagFromChat } from '@/api/chat'
import { getTags } from '@/api/chat'
import { getToken } from '@/utils/storage'
import VoiceRecorder from '@/components/VoiceRecorder.vue'
import { formatRelativeTime } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 加载状态?
const loadingChats = ref(true)
const loadingMessages = ref(false)
const sendingMessage = ref(false)

// 搜索和筛选?
const searchKeyword = ref('')
const selectedTag = ref('')

// 对话列表
const chatList = ref([])
const currentChatId = ref(null)

// 消息列表
const messages = ref([])
const messageListRef = ref(null)

// 输入相关
const inputMessage = ref('')
// 标签列表
const tags = ref([])
const showTagManager = ref(false)
const newTagName = ref('')
const newTagColor = ref('#e8845a')
// 标签分配
const tagPopoverChatId = ref(null)
const showHistory = ref(false)

const toggleTagPopover = (chatId) => {
  tagPopoverChatId.value = tagPopoverChatId.value === chatId ? null : chatId
}

// 点击 popover 外部时关闭
const handleDocumentClick = () => {
  tagPopoverChatId.value = null
}

// 当前对话标题
const currentChatTitle = computed(() => {
  const chat = chatList.value.find(c => c.id === currentChatId.value)
  return chat?.title || '未命名对话'
})

// 过滤后的对话列表
const filteredChats = computed(() => {
  let result = chatList.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(chat =>
      chat.title.toLowerCase().includes(keyword) ||
      chat.lastMessage?.toLowerCase().includes(keyword)
    )
  }

  // 标签过滤
  if (selectedTag.value) {
    result = result.filter(chat => chat.tags && chat.tags.some(t => t.id === selectedTag.value))
  }

  // 按更新时间排序
  return result.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// 按时间分组的对话列表
const groupedChats = computed(() => {
  const chats = filteredChats.value
  if (chats.length === 0) return []

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)
  const monthAgo = new Date(today)
  monthAgo.setDate(monthAgo.getDate() - 30)

  const groups = [
    { label: '今天', chats: [] },
    { label: '7天内', chats: [] },
    { label: '30天内', chats: [] },
    { label: '更早', chats: [] }
  ]

  chats.forEach(chat => {
    const chatDate = new Date(chat.updatedAt)

    if (chatDate >= today) {
      groups[0].chats.push(chat)
    } else if (chatDate >= weekAgo) {
      groups[1].chats.push(chat)
    } else if (chatDate >= monthAgo) {
      groups[2].chats.push(chat)
    } else {
      groups[3].chats.push(chat)
    }
  })

  // 只返回有对话的分组
  return groups.filter(group => group.chats.length > 0)
})

// 格式化时间
const formatTime = (timestamp) => {
  return formatRelativeTime(timestamp)
}

// 渲染Markdown（简化版）
const renderMarkdown = (content) => {
  // 这里简化处理，实际项目应该使用marked或markdown-it库
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

// 加载对话列表
const loadChatList = async () => {
  try {
    loadingChats.value = true
    const res = await getChatList()
    chatList.value = res.data || []

    // 如果有对话，默认选择第一个
    if (chatList.value.length > 0 && !currentChatId.value) {
      selectChat(chatList.value[0].id)
    }
  } catch (error) {
    console.error('加载对话列表失败:', error)
  } finally {
    loadingChats.value = false
  }
}

// 加载标签列表
const loadTags = async () => {
  try {
    const res = await getTags()
    tags.value = res.data || []
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 打开标签分配弹窗
const openTagPopover = (chatId) => {
  const chat = chatList.value.find(c => c.id === chatId)
  if (chat && chat.tags) {
    chatTagSelection.value = chat.tags.map(t => t.id)
  } else {
    chatTagSelection.value = []
  }
  tagPopoverChatId.value = chatId
}

// 处理对话标签变化（乐观更新 + 背景 API 同步）
const onChatTagsChange = async (selectedTagIds, chatId) => {
  const chat = chatList.value.find(c => c.id === chatId)
  if (!chat) return

  const currentTagIds = chat.tags ? chat.tags.map(t => t.id) : []

  // 找出新增和移除的标签
  const addedIds = selectedTagIds.filter(id => !currentTagIds.includes(id))
  const removedIds = currentTagIds.filter(id => !selectedTagIds.includes(id))

  if (addedIds.length === 0 && removedIds.length === 0) return

  // 乐观更新：立即修改本地状态，无需重刷列表
  const originalTags = chat.tags ? [...chat.tags] : []
  chat.tags = selectedTagIds
    .map(id => tags.value.find(t => t.id === id))
    .filter(Boolean)

  try {
    // 背景同步 API
    for (const tagId of addedIds) {
      await addTagToChat(chatId, tagId)
    }
    for (const tagId of removedIds) {
      await removeTagFromChat(chatId, tagId)
    }
    // API 全部成功后再静默刷新列表（保持本地状态优先）
    loadChatList()
  } catch (error) {
    // 失败时回滚本地状态
    chat.tags = originalTags
    ElMessage.error('更新标签失败')
  }
}

// 选择对话
const selectChat = async (chatId) => {
  currentChatId.value = chatId
  await loadMessages(chatId)
  scrollToBottom()
}

// 加载消息
const loadMessages = async (chatId) => {
  try {
    loadingMessages.value = true
    const res = await getChatDetail(chatId)
    messages.value = res.data.messages || []
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    loadingMessages.value = false
  }
}

// 创建新对话
const createNewChat = async () => {
  try {
    const res = await createChat({
      title: '新对话'
    })
    ElMessage.success('创建成功')
    await loadChatList()
    selectChat(res.data.id)
  } catch (error) {
    console.error('创建对话失败:', error)
  }
}

// 处理对话命令
const handleChatCommand = async (command, chatId) => {
  switch (command) {
    case 'edit':
      await editChatTitle(chatId)
      break
    case 'delete':
      await deleteChatById(chatId)
      break
  }
}

// 编辑对话标题
const editChatTitle = async (chatId) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的对话标题', '编辑标题', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: chatList.value.find(c => c.id === chatId)?.title
    })

    await updateChatTitle(chatId, value)
    ElMessage.success('修改成功')
    await loadChatList()
  } catch {
    // 取消编辑
  }
}

// 删除对话
const deleteChatById = async (chatId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteChat(chatId)
    ElMessage.success('删除成功')

    // 如果删除的是当前对话，清空消息区
    if (currentChatId.value === chatId) {
      currentChatId.value = null
      messages.value = []
    }

    await loadChatList()
  } catch {
    // 取消删除
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const content = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息到列表
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  scrollToBottom()

  try {
    sendingMessage.value = true
    loadingMessages.value = true

    // 创建AI消息占位符（空消息，准备接收流式内容）
    const aiMessageIndex = messages.value.length
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    })
    scrollToBottom()

    // 使用流式API接收AI回复
    const token = getToken()
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/${currentChatId.value}/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content, type: 'text' }),
      // 重要：确保流式传输不被缓存
      cache: 'no-store',
      // 某些浏览器可能需要这个
      priority: 'high'
    })

    if (!response.ok) {
      throw new Error('网络响应失败')
    }

    // 读取流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let chunkCount = 0  // 用于调试

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

            // 如果有错误
            if (data.error) {
              throw new Error(data.error)
            }

            // 如果完成
            if (data.done) {
              console.log('流式接收完成，总chunk数:', chunkCount)

              // 更新消息状态
              const completedMessage = {
                ...messages.value[aiMessageIndex],
                id: data.message_id,
                isStreaming: false
              }
              messages.value.splice(aiMessageIndex, 1, completedMessage)

              sendingMessage.value = false
              loadingMessages.value = false
              // 不 break：继续监听 title_update 事件，直到流自然关闭
              continue
            }

            // 后台异步标题生成完成后的更新事件
            if (data.type === 'title_update' && data.dialogue_title) {
              const chat = chatList.value.find(c => c.id === currentChatId.value)
              if (chat) {
                chat.title = data.dialogue_title
              }
              // title_update 是最后一个事件，流会自然关闭
              continue
            }

            // 接收内容并更新UI（打字机效果）
            if (data.content) {
              chunkCount++
              console.log('接收chunk #', chunkCount, ':', data.content)

              // 更新内容（创建新对象以触发Vue更新）
              const updatedMessage = {
                ...messages.value[aiMessageIndex],
                content: messages.value[aiMessageIndex].content + data.content
              }
              messages.value.splice(aiMessageIndex, 1, updatedMessage)

              // 立即滚动到底部
              scrollToBottom()
            }
          } catch (e) {
            console.error('解析数据失败:', e, line)
          }
        }
      }
    }

    // 更新对话列表的最后消息
    const chat = chatList.value.find(c => c.id === currentChatId.value)
    if (chat) {
      // 从数组中获取最新的AI消息
      const finalMessage = messages.value[aiMessageIndex]
      if (finalMessage && finalMessage.content) {
        chat.lastMessage = finalMessage.content.substring(0, 50) + (finalMessage.content.length > 50 ? '...' : '')
        chat.updatedAt = new Date()
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)

    // 移除失败的AI消息
    const index = messages.value.findIndex(m => m.role === 'assistant' && m.isStreaming)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }

    ElMessage.error('发送失败，请重试')
  } finally {
    sendingMessage.value = false
    loadingMessages.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 处理语音识别结果
const handleTranscriptionResult = (text) => {
  // 将识别结果填充到输入框
  inputMessage.value += (inputMessage.value ? ' ' : '') + text
}

// 标签管理方法
const createTag = async () => {
  if (!newTagName.value.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }

  try {
    const token = getToken()
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/tag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: newTagName.value.trim(),
        color: newTagColor.value
      })
    })

    if (response.ok) {
      ElMessage.success('标签创建成功')
      newTagName.value = ''
      await loadTags()
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const deleteTag = async (tagId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个标签吗？', '删除标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = getToken()
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/tag/${tagId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      ElMessage.success('标签删除成功')
      await loadTags()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 返回上一页
const goBack = () => {
  // 检查是否有历史记录
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    // 如果没有历史记录，返回首页
    router.push('/')
  }
}

// 导出对话
const exportChat = () => {
  if (!currentChatId.value || messages.value.length === 0) {
    ElMessage.warning('没有可导出的对话内容')
    return
  }

  // 导出为文本
  let content = `对话标题：${currentChatTitle.value}\n`
  content += `导出时间：${new Date().toLocaleString()}\n`
  content += `─`.repeat(50) + '\n\n'

  messages.value.forEach(msg => {
    const role = msg.role === 'user' ? '用户' : 'AI助手'
    content += `${role} [${formatTime(msg.timestamp)}]：\n${msg.content}\n\n`
  })

  // 创建下载
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `对话_${currentChatTitle.value}_${Date.now()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('对话已导出')
}

// 清空对话
const clearChat = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前对话的所有消息吗？此操作不可恢复！',
      '清空对话',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 清空消息列表
    messages.value = []
    ElMessage.success('对话已清空')
  } catch {
    // 用户取消
  }
}

// 用户菜单命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/profile/privacy')
      break
    case 'logout':
      await userStore.logout()
      break
  }
}

// 历史记录选择
const handleHistorySelect = ({ type, id }) => {
  showHistory.value = false
  if (type === 'chat') {
    selectChat(id)
  } else if (type === 'test') {
    router.push({ name: 'TestResult', params: { id } })
  }
}

// 组件挂载
onMounted(() => {
  loadChatList()
  loadTags()
  document.addEventListener('click', handleDocumentClick)
})

// 组件卸载时
onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.chat-index {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-page;
}

.chat-header {
  height: 64px;
  background: rgba(255, 252, 248, 0.92);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107, 82, 68, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-lg;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .back-button {
      margin-right: $spacing-xs;
    }

    h2 {
      font-size: 17px;
      font-weight: 700;
      color: $text-primary;
      margin: 0;
    }
  }

  .header-center {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;

    .current-chat-info {
      display: flex;
      align-items: center;
      gap: $spacing-sm;

      .chat-title-display {
        font-size: 15px;
        font-weight: 600;
        color: $text-primary;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: $spacing-sm;

    .header-actions {
      display: flex;
      align-items: center;
      gap: 4px;

      .el-button.is-circle {
        border-color: $border-base !important;
        color: $text-regular !important;

        &:hover {
          border-color: $primary-color !important;
          color: $primary-color !important;
          background: $bg-subtle !important;
        }
      }
    }
  }
}

.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

// ---- 左侧边栏 ----
.chat-sidebar {
  width: 268px;
  background: $bg-white;
  border-right: 1px solid $border-lighter;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  .new-chat-btn {
    padding: 14px;
    border-bottom: 1px solid $border-lighter;

    .el-button {
      width: 100%;
      border-radius: 12px !important;
      background: $primary-gradient !important;
      border: none !important;
      color: white !important;
      font-weight: 600;
      height: 40px;
      box-shadow: 0 4px 12px rgba(232, 132, 90, 0.25) !important;
    }
  }

  .search-box, .tag-filter {
    padding: 8px 14px;
  }

  .chat-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;

    &::-webkit-scrollbar { width: 4px; }
    &::-webkit-scrollbar-thumb { background: $border-base; border-radius: 4px; }
  }

  .time-group-header {
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 600;
    color: $text-secondary;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 8px 0 4px;
  }

  .chat-group { margin-bottom: 4px; }

  .chat-item {
    padding: 10px 12px;
    border-radius: 12px;
    cursor: pointer;
    transition: $transition-base;
    margin-bottom: 2px;
    display: flex;
    align-items: flex-start;

    .chat-item-actions {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      margin-left: 6px;
      flex-shrink: 0;

      .more-icon, .tag-assign-icon {
        opacity: 0;
        padding: 4px;
        border-radius: 6px;
        font-size: 16px;
        color: $text-secondary;
        transition: $transition-base;
        cursor: pointer;

        &:hover {
          color: $primary-color;
          background: rgba(232, 132, 90, 0.1);
        }
      }
    }

    &:hover .chat-item-actions .more-icon,
    &:hover .chat-item-actions .tag-assign-icon {
      opacity: 1;
    }

    &:hover {
      background: $bg-subtle;
    }

    &.active {
      background: rgba(232, 132, 90, 0.1);
      border: 1px solid rgba(232, 132, 90, 0.2);

      .chat-title { color: $primary-dark; }
      .chat-preview { color: $primary-color; }
    }

    .chat-item-content {
      flex: 1;
      min-width: 0;
      .chat-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
      }

      .chat-title {
        font-size: 13px;
        font-weight: 600;
        color: $text-primary;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;
        margin: 0;
      }

      .chat-preview {
        font-size: 12px;
        color: $text-secondary;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .chat-tags-row {
      margin-top: 4px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      min-height: 0;
    }

    .chat-tags-inner {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
    }

    .chat-tag-item {
      margin-right: 4px;
      margin-bottom: 2px;
    }
  }
}

.tag-enter-active,
.tag-leave-active {
  transition: all 0.3s ease;
}

.tag-enter-from,
.tag-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.tag-leave-active {
  position: absolute;
}

.tag-move {
  transition: transform 0.3s ease;
}

.tag-popover-content {
  padding: 4px 0;
}

// ---- 右侧主区域 ----?----
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: $bg-page;
  overflow: hidden;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: $text-secondary;

  :deep(.el-result__icon) svg { fill: $primary-lighter; }
  :deep(.el-result__title p) { color: $text-regular; font-weight: 600; }
  :deep(.el-result__subtitle p) { color: $text-secondary; }
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// ---- 消息列表 ----
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: $bg-page;

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: $border-base; border-radius: 4px; }
}

.message-item {
  margin-bottom: 20px;

  &.assistant {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;

    // max-width 控制在直接 flex 子项上，避免气泡百分比循环塌陷
    .message-assistant { max-width: 68%; }

    .message-bubble {
      background: white;
      color: $text-primary;
      border-radius: 4px 18px 18px 18px;
      padding: 14px 18px;
      max-width: 100%;
      min-width: 56px;   // 流式输出初始内容为空时防止宽度归零
      box-shadow: $box-shadow-card;
      border: 1px solid $border-lighter;
      line-height: 1.65;
    }
  }

  &.user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;

    .message-user { max-width: 68%; }

    .message-bubble {
      background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%);
      color: white;
      border-radius: 18px 4px 18px 18px;
      padding: 14px 18px;
      max-width: 100%;
      min-width: 56px;
      box-shadow: 0 4px 16px rgba(232, 132, 90, 0.3);
      line-height: 1.65;
    }
  }
}

.message-text {
  line-height: 1.65;
  word-break: break-word;
}

// ---- 打字动画 ----
.typing-bubble {
  display: flex !important;
  gap: 7px;
  align-items: center;

  span {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $primary-color;
    opacity: 0.35;
    animation: typing-wave 1.2s ease-in-out infinite;

    &:nth-child(2) { animation-delay: 0.18s; }
    &:nth-child(3) { animation-delay: 0.36s; }
  }
}

@keyframes typing-wave {
  0%, 100% { transform: translateY(0) scale(1);   opacity: 0.35; }
  40%       { transform: translateY(-6px) scale(1.15); opacity: 1; }
}

// ---- 输入区域 ----
.chat-input-area {
  background: white;
  border-top: 1px solid $border-lighter;
  padding: 16px;
}

.input-toolbar {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.input-box {
  display: flex;
  gap: 10px;
  align-items: flex-end;

  .el-textarea { flex: 1; }

  :deep(.el-textarea__inner) {
    border-radius: $border-radius-lg !important;
    border: 1px solid $border-base !important;
    background: $bg-page !important;
    transition: $transition-base;

    &:focus {
      border-color: $primary-color !important;
      box-shadow: 0 0 0 3px rgba(232, 132, 90, 0.12) !important;
    }
  }
}

// ---- 响应式 ----
@media (max-width: $breakpoint-md) {
  .chat-sidebar {
    position: absolute;
    left: -268px;
    height: calc(100vh - 64px);
    z-index: 100;
    box-shadow: 4px 0 20px rgba(0,0,0,0.1);
    transition: $transition-base;

    &.show { left: 0; }
  }

  .message-assistant,
  .message-user { max-width: 86% !important; }
}
</style>

<!-- 标签管理对话框样式?-->
<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.tag-manager {
  .tag-create {
    display: flex;
    align-items: center;
    padding: $spacing-md 0;
    margin-bottom: $spacing-lg;
    border-bottom: 1px solid $border-lighter;

    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }
  }

  .tag-list {
    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }

    .tag-items {
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-sm;
      padding: $spacing-sm 0;
    }
  }
}
</style>

<!-- 标签管理对话框样式?-->
<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.tag-manager {
  .tag-create {
    display: flex;
    align-items: center;
    padding: $spacing-md 0;
    margin-bottom: $spacing-lg;
    border-bottom: 1px solid $border-light;

    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }
  }

  .tag-list {
    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }

    .tag-items {
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-sm;
      padding: $spacing-sm 0;
    }
  }
}
</style>
