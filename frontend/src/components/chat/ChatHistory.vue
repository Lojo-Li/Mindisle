<template>
  <div class="chat-history">
    <div class="history-header">
      <h3>历史记录</h3>
      <!-- 搜索框 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索对话或测试..."
        prefix-icon="Search"
        clearable
        size="small"
        style="width: 220px"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      />
    </div>

    <!-- Tab 切换：对话历史 / 测试历史 -->
    <el-tabs v-model="activeTab" class="history-tabs">
      <el-tab-pane label="对话历史" name="chat">
        <div v-loading="chatLoading" class="history-list">
          <el-empty v-if="!chatLoading && chatList.length === 0" description="暂无对话记录" />

          <div
            v-for="item in chatList"
            :key="item.id"
            class="history-item"
            @click="openChat(item)"
          >
            <div class="item-icon">
              <el-icon :size="20" color="#409eff"><ChatDotSquare /></el-icon>
            </div>
            <div class="item-content">
              <div class="item-title">{{ item.title || '未命名对话' }}</div>
              <div class="item-meta">
                <span class="item-date">{{ formatTime(item.createdAt || item.updatedAt) }}</span>
                <el-tag
                  v-if="item.tag"
                  size="small"
                  type="info"
                  class="item-tag"
                >
                  {{ item.tag }}
                </el-tag>
              </div>
            </div>
            <el-button
              text
              :icon="ArrowRight"
              size="small"
              class="item-action"
            />
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="chatTotal > chatPageSize" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="chatPage"
            :page-size="chatPageSize"
            :total="chatTotal"
            small
            layout="prev, pager, next"
            @current-change="loadChatList"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="测试历史" name="test">
        <div v-loading="testLoading" class="history-list">
          <el-empty v-if="!testLoading && testList.length === 0" description="暂无测试记录" />

          <div
            v-for="item in testList"
            :key="item.id"
            class="history-item"
            @click="viewTestResult(item)"
          >
            <div class="item-icon">
              <el-icon :size="20" color="#67c23a"><List /></el-icon>
            </div>
            <div class="item-content">
              <div class="item-title">{{ item.testName }}</div>
              <div class="item-meta">
                <span class="item-date">{{ formatTime(item.date) }}</span>
                <el-tag
                  :type="getScoreTagType(item.score, item.maxScore)"
                  size="small"
                >
                  {{ item.score }}/{{ item.maxScore }}
                </el-tag>
                <el-tag
                  v-if="item.level"
                  :type="getLevelTagType(item.level)"
                  size="small"
                >
                  {{ item.level }}
                </el-tag>
              </div>
            </div>
            <el-button
              text
              :icon="ArrowRight"
              size="small"
              class="item-action"
            />
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="testTotal > testPageSize" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="testPage"
            :page-size="testPageSize"
            :total="testTotal"
            small
            layout="prev, pager, next"
            @current-change="loadTestList"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotSquare, List, ArrowRight, Search } from '@element-plus/icons-vue'
import { getChatList } from '@/api/chat'
import { getTestHistory } from '@/api/test'

const router = useRouter()
const emit = defineEmits(['select'])

// Tab
const activeTab = ref('chat')

// 搜索
const searchKeyword = ref('')

// Chat list
const chatList = ref([])
const chatLoading = ref(false)
const chatPage = ref(1)
const chatPageSize = ref(20)
const chatTotal = ref(0)

// Test list
const testList = ref([])
const testLoading = ref(false)
const testPage = ref(1)
const testPageSize = ref(20)
const testTotal = ref(0)

/** 加载对话列表 */
async function loadChatList() {
  chatLoading.value = true
  try {
    const res = await getChatList({
      page: chatPage.value,
      pageSize: chatPageSize.value,
      keyword: searchKeyword.value || undefined
    })
    chatList.value = res.data?.list || res.data?.records || []
    chatTotal.value = res.data?.total || res.data?.count || 0
  } catch (e) {
    ElMessage.error('加载对话历史失败')
  } finally {
    chatLoading.value = false
  }
}

/** 加载测试列表 */
async function loadTestList() {
  testLoading.value = true
  try {
    const res = await getTestHistory({
      page: testPage.value,
      pageSize: testPageSize.value
    })
    testList.value = res.data?.list || res.data?.records || []
    testTotal.value = res.data?.total || res.data?.count || 0
  } catch (e) {
    ElMessage.error('加载测试历史失败')
  } finally {
    testLoading.value = false
  }
}

/** 搜索 */
function handleSearch() {
  chatPage.value = 1
  testPage.value = 1
  if (activeTab.value === 'chat') {
    loadChatList()
  } else {
    loadTestList()
  }
}

/** 打开对话 */
function openChat(item) {
  router.push({ name: 'ChatDetail', params: { id: item.id } })
  emit('select', { type: 'chat', id: item.id })
}

/** 查看测试结果 */
function viewTestResult(item) {
  router.push({ name: 'TestResult', params: { id: item.id } })
  emit('select', { type: 'test', id: item.id })
}

/** 格式化时间 */
function formatTime(time) {
  if (!time) return ''
  const d = new Date(time)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

/** 得分标签样式 */
function getScoreTagType(score, maxScore) {
  if (!maxScore) return 'info'
  const pct = score / maxScore
  if (pct >= 0.8) return 'success'
  if (pct >= 0.6) return 'warning'
  return 'danger'
}

/** 等级标签样式 */
function getLevelTagType(level) {
  if (!level) return 'info'
  if (level === '优秀' || level === '良好') return 'success'
  if (level === '中等') return 'warning'
  return 'danger'
}

// 切换 Tab 时按需加载
watch(activeTab, (tab) => {
  if (tab === 'chat' && chatList.value.length === 0) {
    loadChatList()
  } else if (tab === 'test' && testList.value.length === 0) {
    loadTestList()
  }
})

onMounted(() => {
  loadChatList()
})
</script>

<style scoped>
.chat-history {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.history-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.history-tabs :deep(.el-tab-pane) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-item + .history-item {
  border-top: 1px solid #f0f0f0;
}

.item-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f9ff;
  border-radius: 8px;
  margin-right: 12px;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.item-date {
  font-size: 12px;
  color: #909399;
}

.item-tag {
  flex-shrink: 0;
}

.item-action {
  flex-shrink: 0;
  margin-left: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}
</style>
