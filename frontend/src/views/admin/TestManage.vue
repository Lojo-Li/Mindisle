<template>
  <div class="test-manage">
    <div class="page-header">
      <h2>心理测试管理</h2>
      <el-button type="primary" @click="handleAddTest">
        <el-icon><Plus /></el-icon>
        添加测试
      </el-button>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="测试名称">
          <el-input v-model="searchForm.keyword" placeholder="请输入测试名称" clearable @clear="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="testList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="测试名称" min-width="200" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryText(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="questionCount" label="题目数量" width="100" align="center" />
        <el-table-column prop="completedCount" label="完成次数" width="100" align="center" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" text size="small" @click="handleViewQuestions(row)">题目管理</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAdminTestList,
  deleteTest,
  getAdminTestDetail
} from '@/api/admin'

// 搜索表单
const searchForm = ref({
  keyword: ''
})

// 加载状态
const loading = ref(false)

// 测试列表
const testList = ref([])

// 分页信息
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 分类映射（英文 -> 中文）
const categoryMap = {
  'anxiety': '焦虑测评',
  'depression': '抑郁测评',
  'personality': '人格测试',
  'stress': '压力测评',
  'emotion': '情绪管理',
  'emotional': '情绪测评',
  'comprehensive': '综合测评',
  'work': '职业发展',
  'health': '健康测评',
  'sleep': '睡眠质量',
  'relationship': '人际关系',
  'career': '职业规划',
  'other': '其他'
}

// 获取分类中文文本
const getCategoryText = (category) => {
  return categoryMap[category] || category || '未分类'
}

// 加载测试列表
const loadTestList = async () => {
  try {
    loading.value = true
    const res = await getAdminTestList({
      keyword: searchForm.value.keyword,
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    })

    if (res.data) {
      testList.value = res.data.list || res.data.tests || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载测试列表失败:', error)
    ElMessage.error('加载测试列表失败')
  } finally {
    loading.value = false
  }
}

// 添加测试
const handleAddTest = () => {
  ElMessage.info('添加测试功能开发中...')
}

// 搜索
const handleSearch = () => {
  pagination.value.page = 1
  loadTestList()
}

// 重置
const handleReset = () => {
  searchForm.value.keyword = ''
  pagination.value.page = 1
  loadTestList()
}

// 编辑测试
const handleEdit = (row) => {
  ElMessage.info(`编辑测试: ${row.title}`)
}

// 题目管理
const handleViewQuestions = (row) => {
  ElMessage.info(`题目管理: ${row.title}`)
}

// 删除测试
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试"${row.title}"吗？删除后不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteTest(row.id)
    ElMessage.success('删除成功')

    // 重新加载列表
    await loadTestList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 分页大小改变
const handleSizeChange = (val) => {
  pagination.value.pageSize = val
  pagination.value.page = 1
  loadTestList()
}

// 当前页改变
const handleCurrentChange = (val) => {
  pagination.value.page = val
  loadTestList()
}

// 组件挂载时加载数据
onMounted(() => {
  loadTestList()
})
</script>

<style scoped>
.test-manage {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
}

.search-card {
  margin-bottom: 0;
}

.search-card :deep(.el-card__body) {
  padding: 20px;
}

.table-card {
  flex: 1;
}

.table-card :deep(.el-card__body) {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .pagination-container {
    justify-content: center;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      justify-content: center;
    }
  }
}
</style>
