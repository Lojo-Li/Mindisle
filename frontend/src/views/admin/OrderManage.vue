<template>
  <div class="order-manage">
    <div class="page-header">
      <h2>订单管理</h2>
      <div class="header-actions">
        <el-button :icon="Download" @click="exportData">导出数据</el-button>
      </div>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索订单号、用户、咨询师"
          style="width: 250px"
          clearable
        />
        <el-select v-model="filters.status" placeholder="全部状态" style="width: 150px" clearable>
          <el-option label="待确认" value="pending" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          placeholder="选择日期范围"
          style="width: 250px"
        />
        <el-button type="primary" @click="loadOrders">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-label">总订单数:</span>
          <span class="stat-value">{{ stats.total }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总收入:</span>
          <span class="stat-value">¥{{ stats.revenue }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">完成率:</span>
          <span class="stat-value">{{ stats.completionRate }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均客单价:</span>
          <span class="stat-value">¥{{ stats.avgPrice }}</span>
        </div>
      </div>

      <!-- 订单表格 -->
      <el-table v-loading="loading" :data="orders" stripe>
        <el-table-column prop="appointment_no" label="预约编号" width="140" />
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="counselor_name" label="咨询师" width="120" />
        <el-table-column prop="appointment_date" label="预约日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.appointment_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="consultation_type" label="方式" width="80">
          <template #default="{ row }">
            {{ getTypeText(row.consultation_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="费用" width="80">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadOrders"
          @current-change="loadOrders"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="600px">
      <div v-if="currentOrder" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预约编号">{{ currentOrder.appointment_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentOrder.status)">
              {{ getStatusText(currentOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户">{{ currentOrder.user_name }}</el-descriptions-item>
          <el-descriptions-item label="咨询师">{{ currentOrder.counselor_name }}</el-descriptions-item>
          <el-descriptions-item label="预约日期">{{ formatDate(currentOrder.appointment_date) }}</el-descriptions-item>
          <el-descriptions-item label="咨询方式">{{ getTypeText(currentOrder.consultation_type) }}</el-descriptions-item>
          <el-descriptions-item label="费用">¥{{ currentOrder.price }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ currentOrder.created_at }}</el-descriptions-item>
        </el-descriptions>

        <template v-if="currentOrder.status === 'completed'">
          <el-divider />
          <h4>评价信息</h4>
          <div class="review-info">
            <div class="rating">
              <el-rate v-model="currentOrder.rating" disabled />
              <span>{{ currentOrder.rating }} 星</span>
            </div>
            <p class="review-content">{{ currentOrder.review || '无文字评价' }}</p>
            <div v-if="currentOrder.tags?.length" class="review-tags">
              <el-tag v-for="tag in currentOrder.tags" :key="tag" size="small">
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getAdminOrders, exportOrders } from '@/api/admin'

const loading = ref(false)
const orders = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  keyword: '',
  status: '',
  dateRange: []
})

const stats = ref({
  total: 0,
  revenue: 0,
  completionRate: 0,
  avgPrice: 0
})

const detailVisible = ref(false)
const currentOrder = ref(null)

const loadOrders = async () => {
  try {
    loading.value = true
    const res = await getAdminOrders({
      keyword: filters.keyword,
      status: filters.status,
      startDate: filters.dateRange?.[0],
      endDate: filters.dateRange?.[1],
      page: currentPage.value,
      pageSize: pageSize.value
    })
    orders.value = res.data.items || []
    total.value = res.data.total || 0
    stats.value.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.dateRange = []
  currentPage.value = 1
  loadOrders()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const getTypeText = (type) => ({ video: '视频', voice: '语音', offline: '线下' }[type] || type)

const getStatusText = (status) => {
  const map = {
    pending: '待确认',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const types = { pending: 'warning', confirmed: 'primary', in_progress: 'primary', completed: 'success', cancelled: 'danger', refunded: 'info' }
  return types[status] || ''
}

const viewDetail = (row) => {
  currentOrder.value = row
  detailVisible.value = true
}

const exportData = async () => {
  try {
    ElMessage.info('正在导出...')
    const res = await exportOrders()
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `orders_${Date.now()}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => loadOrders())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.order-manage { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }

.filter-bar { display: flex; gap: $spacing-md; margin-bottom: $spacing-lg; }
.stats-row { display: flex; gap: $spacing-xl; padding: $spacing-lg; background: #f5f7fa; border-radius: $border-radius; margin-bottom: $spacing-lg; }
.stat-item { display: flex; align-items: center; gap: $spacing-sm; }
.stat-label { color: $text-secondary; }
.stat-value { font-size: 18px; font-weight: 600; color: $primary-color; }

.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }

.detail-content { display: flex; flex-direction: column; gap: $spacing-lg; }
.review-info { padding: $spacing-lg; background: #f5f7fa; border-radius: $border-radius; }
.rating { display: flex; align-items: center; gap: $spacing-md; margin-bottom: $spacing-md; }
.review-content { color: $text-secondary; line-height: 1.8; margin: $spacing-md 0; }
.review-tags { display: flex; gap: $spacing-sm; flex-wrap: wrap; }
</style>
