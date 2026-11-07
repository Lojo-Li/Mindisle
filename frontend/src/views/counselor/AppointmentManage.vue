<template>
  <div class="appointment-page">
    <div class="container">

      <div class="page-title">
        <h2>我的预约</h2>
        <p>管理你的咨询预约记录</p>
      </div>

      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="tab-btn"
          :class="{ active: activeTab === tab.value }"
          @click="switchTab(tab.value)"
        >
          {{ tab.label }}
          <span v-if="tabCounts[tab.value] !== undefined" class="tab-count">{{ tabCounts[tab.value] }}</span>
        </button>
      </div>

      <div v-loading="loading" class="order-list">
        <el-empty v-if="!loading && orders.length === 0" description="暂无预约记录" :image-size="120" />

        <div v-for="order in orders" :key="order.id" class="order-card" :class="`status-${order.status}`">
          <!-- 左侧竖条 -->
          <div class="card-stripe" />

          <!-- 主体内容 -->
          <div class="card-main">
            <!-- 顶部：日期 + 状态 -->
            <div class="card-top">
              <div class="date-block">
                <span class="date-icon">📅</span>
                <span class="date-text">{{ formatDate(order.appointment_date) }}</span>
              </div>
              <el-tag :type="getStatusType(order.status)" round size="small" class="status-tag">
                {{ getStatusLabel(order.status) }}
              </el-tag>
            </div>

            <!-- 信息行 -->
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">预约编号</span>
                <span class="info-value mono">{{ order.appointment_no }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">咨询师</span>
                <span class="info-value highlight">{{ order.counselor?.name || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">咨询方式</span>
                <span class="info-value">
                  <span class="type-badge">{{ getTypeLabel(order.consultation_type) }}</span>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">咨询费用</span>
                <span class="info-value price">¥{{ order.price }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="card-actions">
              <el-button
                v-if="order.status === 'confirmed' || order.status === 'in_progress'"
                type="success"
                size="small"
                round
                @click="enterConsultation(order.id)"
              >💬 进入咨询</el-button>
              <el-button
                v-if="order.status !== 'completed' && order.status !== 'cancelled' && order.status !== 'refunded' && order.status !== 'in_progress'"
                size="small"
                round
                @click="cancelOrder(order.id)"
              >取消预约</el-button>
              <el-button
                v-if="order.status === 'completed'"
                type="primary"
                size="small"
                round
                @click="goToReview(order.id)"
              >✍️ 写评价</el-button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserAppointments, cancelAppointment } from '@/api/counselor'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')

// 状态 → 中文标签映射
const STATUS_LABELS = {
  pending: '待确认',
  confirmed: '已确认',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
  refunded: '已退款'
}

const orders = ref([])
const tabCounts = ref({})

// 显示全部状态标签（始终展示所有状态供筛选）
const tabs = [
  { label: '全部', value: 'all' },
  ...Object.entries(STATUS_LABELS).map(([value, label]) => ({ label, value }))
]

const switchTab = (tab) => {
  activeTab.value = tab
  loadOrders()
}

const loadOrders = async () => {
  try {
    loading.value = true
    const status = activeTab.value === 'all' ? '' : activeTab.value
    const res = await getUserAppointments({ status, page: 1, page_size: 100 })
    orders.value = res.data.items || []
    await loadCounts()
  } finally {
    loading.value = false
  }
}

/** 并行查询各状态数量用于标签角标 */
const loadCounts = async () => {
  const statuses = ['', ...Object.keys(STATUS_LABELS)]
  const queries = statuses.map(s => getUserAppointments({ status: s, page: 1, page_size: 1 }))
  try {
    const results = await Promise.allSettled(queries)
    const counts = {}
    results.forEach((r, i) => {
      if (r.status === 'fulfilled') {
        counts[statuses[i] || 'all'] = r.value.data?.total || 0
      }
    })
    tabCounts.value = counts
  } catch { /* 获取数量失败不影响主流程 */ }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'info', in_progress: 'primary', refunded: 'info' }
  return types[status] || ''
}

const getStatusLabel = (status) => {
  const labels = { pending: '待确认', confirmed: '已确认', in_progress: '进行中', completed: '已完成', cancelled: '已取消', refunded: '已退款' }
  return labels[status] || status
}

const getTypeLabel = (type) => {
  const labels = { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }
  return labels[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const cancelOrder = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消预约吗？', '提示', { type: 'warning' })
    await cancelAppointment(id)
    ElMessage.success('取消成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const goToReview = (id) => {
  router.push(`/counselor/review/${id}`)
}

const enterConsultation = (id) => {
  router.push(`/consultation/user/${id}`)
}

onMounted(() => loadOrders())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.appointment-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

// ── 页头 ──────────────────────────────────────────────
.page-title {
  margin-bottom: 28px;

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 4px;
  }

  p {
    font-size: 13px;
    color: $text-secondary;
    margin: 0;
  }
}

// ── Tab 栏 ────────────────────────────────────────────
.tab-bar {
  display: flex;
  gap: 6px;
  margin-bottom: 24px;
  background: #fff;
  border: 1px solid $border-lighter;
  border-radius: 12px;
  padding: 5px;
  width: fit-content;
}

.tab-btn {
  padding: 6px 20px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: $text-regular;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover { color: $primary-color; }

  &.active {
    background: $primary-color;
    color: #fff;
    box-shadow: 0 2px 8px rgba(232,132,90,0.35);
  }
}

// ── 订单列表 ──────────────────────────────────────────
.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 120px;
}

// ── 订单卡片 ──────────────────────────────────────────
.order-card {
  display: flex;
  background: #fff;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 14px rgba(107,82,68,0.07);
  overflow: hidden;
  transition: transform 0.22s, box-shadow 0.22s;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(107,82,68,0.12);
  }

  // 状态左侧竖条颜色
  &.status-pending   .card-stripe { background: #e6a23c; }
  &.status-confirmed .card-stripe { background: #409eff; }
  &.status-in_progress .card-stripe { background: #409eff; }
  &.status-completed .card-stripe { background: #67c23a; }
  &.status-cancelled .card-stripe { background: #909399; }
  &.status-refunded  .card-stripe { background: #909399; }
}

.card-stripe {
  width: 5px;
  flex-shrink: 0;
  background: $border-base;
}

.card-main {
  flex: 1;
  padding: 20px 24px;
}

// 顶部行
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.date-block {
  display: flex;
  align-items: center;
  gap: 6px;

  .date-icon { font-size: 15px; }

  .date-text {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
  }
}

.status-tag { font-weight: 600; }

// 信息网格
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
  margin-bottom: 18px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;

  .info-label {
    font-size: 11px;
    color: $text-placeholder;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .info-value {
    font-size: 14px;
    color: $text-regular;

    &.mono { font-family: monospace; font-size: 12px; color: $text-secondary; }
    &.highlight { font-weight: 600; color: $text-primary; }
    &.price { font-weight: 700; color: $primary-color; font-size: 15px; }
  }

  .type-badge {
    display: inline-block;
    padding: 2px 10px;
    background: rgba(232,132,90,0.1);
    color: $primary-color;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
  }
}

// 操作按钮
.card-actions {
  display: flex;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid $border-lighter;
}

@media (max-width: 480px) {
  .info-grid { grid-template-columns: 1fr; }
  .tab-bar { flex-wrap: wrap; }
}
</style>
