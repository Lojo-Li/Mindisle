<template>
  <div class="dialogue-manage">
    <div class="page-header">
      <h2>对话管理</h2>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="用户ID">
          <el-input v-model="searchForm.userId" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item label="对话标签">
          <el-select v-model="searchForm.tag" placeholder="请选择标签" clearable>
            <el-option label="焦虑" value="焦虑" />
            <el-option label="抑郁" value="抑郁" />
            <el-option label="压力" value="压力" />
            <el-option label="失眠" value="失眠" />
            <el-option label="人际关系" value="人际关系" />
            <el-option label="职场" value="职场" />
            <el-option label="情感" value="情感" />
            <el-option label="家庭" value="家庭" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table v-loading="loading" :data="dialogueList" stripe>
        <el-table-column prop="id" label="对话ID" width="100" />
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="title" label="对话标题" min-width="180" />
        <el-table-column prop="message_count" label="消息数" width="80" />
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="tag in row.tags"
              :key="tag.id"
              :color="tag.color"
              size="small"
              style="margin-right: 6px; color: #fff"
            >
              {{ tag.name }}
            </el-tag>
            <span v-if="!row.tags?.length" class="no-tags">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_message" label="最后消息" min-width="200">
          <template #default="{ row }">
            <span class="last-msg">{{ row.last_message || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleViewDetail(row)">查看详情</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="loadDialogues"
        @current-change="loadDialogues"
      />
    </el-card>

    <!-- 对话详情对话框 -->
    <el-dialog v-model="detailVisible" title="对话详情" width="800px" top="5vh">
      <div v-loading="detailLoading" class="dialogue-detail">
        <div class="detail-header">
          <div class="detail-info">
            <span class="detail-label">对话标题：</span>
            <strong>{{ currentDialogue?.title }}</strong>
          </div>
          <div class="detail-info">
            <span class="detail-label">用户：</span>
            <span>{{ currentDialogue?.user_name }}</span>
          </div>
          <div class="detail-info">
            <span class="detail-label">创建时间：</span>
            <span>{{ formatDate(currentDialogue?.created_at) }}</span>
          </div>
        </div>

        <el-divider />

        <div class="messages-container">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message-item"
            :class="msg.role"
          >
            <div class="message-role">
              <el-tag :type="msg.role === 'user' ? 'primary' : 'success'" size="small">
                {{ msg.role === 'user' ? '用户' : 'AI助手' }}
              </el-tag>
              <span class="message-time">{{ formatDate(msg.created_at) }}</span>
            </div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <el-empty v-if="!detailLoading && messages.length === 0" description="暂无消息" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminDialogues, getAdminDialogueDetail, deleteAdminDialogue } from '@/api/admin'

const loading = ref(false)
const dialogueList = ref([])

const searchForm = reactive({
  userId: '',
  tag: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const detailVisible = ref(false)
const detailLoading = ref(false)
const currentDialogue = ref(null)
const messages = ref([])

const loadDialogues = async () => {
  try {
    loading.value = true
    const res = await getAdminDialogues({
      user_id: searchForm.userId || undefined,
      tag: searchForm.tag || undefined,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    dialogueList.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadDialogues()
}

const handleReset = () => {
  searchForm.userId = ''
  searchForm.tag = ''
  pagination.page = 1
  loadDialogues()
}

const handleViewDetail = async (row) => {
  currentDialogue.value = row
  detailVisible.value = true
  try {
    detailLoading.value = true
    const res = await getAdminDialogueDetail(row.id)
    messages.value = res.data.messages || []
  } catch {
    messages.value = []
  } finally {
    detailLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除对话「${row.title}」吗？`, '提示', { type: 'warning' })
    await deleteAdminDialogue(row.id)
    ElMessage.success('删除成功')
    loadDialogues()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => loadDialogues())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;

.dialogue-manage {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.table-card {
  flex: 1;
}

.no-tags {
  color: $text-placeholder;
}

.last-msg {
  color: $text-secondary;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 13px;
}

/* 对话详情 */
.dialogue-detail {
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-info {
  font-size: 14px;
}

.detail-label {
  color: $text-secondary;
}

.messages-container {
  max-height: 500px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  padding: 12px 16px;
  border-radius: 10px;
}

.message-item.user {
  background: #f0f7ff;
  border-left: 3px solid #409eff;
}

.message-item.assistant {
  background: #f0fdf4;
  border-left: 3px solid #67c23a;
}

.message-role {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.message-time {
  font-size: 12px;
  color: $text-placeholder;
}

.message-content {
  font-size: 14px;
  line-height: 1.8;
  color: $text-primary;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
