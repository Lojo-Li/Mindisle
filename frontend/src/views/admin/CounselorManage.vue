<template>
  <div class="counselor-manage">
    <div class="page-header">
      <h2>咨询师管理</h2>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="姓名/邮箱/手机号" clearable @clear="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable @clear="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="counselorList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="specialties" label="擅长领域" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="spec in row.specialties" :key="spec" size="small" style="margin-right: 5px;">
              {{ getSpecialtyText(spec) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'active'"
              type="warning"
              text
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '暂停' : '激活' }}
            </el-button>
            <el-button type="info" text size="small" @click="handleViewOrders(row)">订单</el-button>
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
import {
  getAdminCounselors,
  toggleCounselorStatus
} from '@/api/admin'

// 搜索表单
const searchForm = ref({
  keyword: '',
  status: ''
})

// 加载状态
const loading = ref(false)

// 咨询师列表
const counselorList = ref([])

// 分页信息
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 状态映射
const statusMap = {
  'pending_review': '待审核',
  'active': '已激活',
  'inactive': '未激活',
  'suspended': '已暂停',
  'pending': '待审核',
  'approved': '已通过',
  'rejected': '已拒绝',
  'disabled': '已禁用'
}

// 状态类型映射
const statusTypeMap = {
  'pending_review': 'warning',
  'active': 'success',
  'inactive': 'info',
  'suspended': 'danger',
  'pending': 'warning',
  'approved': 'success',
  'rejected': 'danger',
  'disabled': 'info'
}

// 擅长领域映射（英文 -> 中文）
const specialtyMap = {
  'anxiety': '焦虑症',
  'depression': '抑郁症',
  'relationship': '人际关系',
  'career': '职业发展',
  'family': '家庭关系',
  'marriage': '婚姻咨询',
  'adolescent': '青少年心理',
  'stress': '压力管理',
  'emotion': '情绪调节',
  'sleep': '睡眠障碍',
  'trauma': '创伤疗愈',
  'addiction': '成瘾行为',
  'eating_disorder': '饮食障碍',
  'obsessive_compulsive': '强迫症',
  'phobia': '恐惧症',
  'bipolar': '双相情感障碍',
  'schizophrenia': '精神分裂症',
  'personality_disorder': '人格障碍',
  'gender_identity': '性别认同',
  'sexual_issues': '性心理',
  'grief': '丧失与悲伤',
  'self_esteem': '自尊自信',
  'perfectionism': '完美主义',
  'procrastination': '拖延行为',
  'anger_management': '愤怒管理',
  'divorce': '离婚调适',
  'parenting': '亲子教育',
  'aging': '老年心理',
  'life_transition': '人生转变',
  'loneliness': '孤独感',
  'burnout': '职业倦怠',
  'other': '其他'
}

// 获取状态文本
const getStatusText = (status) => {
  return statusMap[status] || status || '未知'
}

// 获取状态类型
const getStatusType = (status) => {
  return statusTypeMap[status] || 'info'
}

// 获取擅长领域中文文本
const getSpecialtyText = (specialty) => {
  return specialtyMap[specialty] || specialty || '未知'
}

// 加载咨询师列表
const loadCounselorList = async () => {
  try {
    loading.value = true
    const res = await getAdminCounselors({
      keyword: searchForm.value.keyword,
      counselor_status: searchForm.value.status,
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })

    if (res.data) {
      counselorList.value = res.data.list || res.data.counselors || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载咨询师列表失败:', error)
    ElMessage.error('加载咨询师列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.page = 1
  loadCounselorList()
}

// 重置
const handleReset = () => {
  searchForm.value.keyword = ''
  searchForm.value.status = ''
  pagination.value.page = 1
  loadCounselorList()
}

// 查看详情
const handleView = (row) => {
  ElMessage.info(`查看咨询师: ${row.name}`)
}

// 切换状态（激活/暂停）
const handleToggleStatus = async (row) => {
  try {
    const action = row.is_active ? '暂停' : '激活'
    await ElMessageBox.confirm(
      `确定要${action}咨询师"${row.name}"吗？`,
      `${action}确认`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await toggleCounselorStatus(row.id, { active: !row.is_active })
    ElMessage.success(`${action}成功`)

    // 重新加载列表
    await loadCounselorList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${action}失败:`, error)
      ElMessage.error(`${action}失败`)
    }
  }
}

// 查看订单
const handleViewOrders = (row) => {
  ElMessage.info(`查看咨询师订单: ${row.name}`)
}

// 分页大小改变
const handleSizeChange = (val) => {
  pagination.value.pageSize = val
  pagination.value.page = 1
  loadCounselorList()
}

// 当前页改变
const handleCurrentChange = (val) => {
  pagination.value.page = val
  loadCounselorList()
}

// 组件挂载时加载数据
onMounted(() => {
  loadCounselorList()
})
</script>

<style scoped>
.counselor-manage {
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
