<template>
  <div class="counselor-orders-page">
    <div class="container">

      <div class="page-title">
        <h2>咨询师工作台</h2>
        <p>管理用户的咨询预约</p>
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
          <div class="card-stripe" />

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
                <span class="info-label">用户</span>
                <span class="info-value highlight">{{ order.user_name || '未知' }}</span>
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

            <!-- 问题描述 -->
            <div v-if="order.problem_description" class="problem-desc">
              <span class="desc-label">问题描述：</span>
              <span class="desc-text">{{ order.problem_description }}</span>
            </div>

            <!-- 操作按钮 -->
            <div class="card-actions">
              <template v-if="order.status === 'pending'">
                <el-button type="success" size="small" round @click="agreeOrder(order)">同意</el-button>
                <el-button type="danger" size="small" round @click="rejectOrder(order)">拒绝</el-button>
              </template>
              <el-button
                v-else-if="order.status === 'confirmed' || order.status === 'in_progress'"
                type="success"
                size="small"
                round
                @click="startChat(order)"
              >💬 进入咨询</el-button>
              <el-button
                v-else-if="order.status === 'completed'"
                type="primary"
                size="small"
                round
                @click="viewReview(order)"
              >查看评价</el-button>
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
import { getCounselorOrders, handleOrder } from '@/api/consultation'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')
const orders = ref([])
const tabCounts = ref({})

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已确认', value: 'confirmed' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
]

const switchTab = (tab) => {
  activeTab.value = tab
  loadOrders()
}

const loadOrders = async () => {
  try {
    loading.value = true
    const status = activeTab.value === 'all' ? '' : activeTab.value
    const res = await getCounselorOrders({ status, page_size: 100 })
    orders.value = res.data.items || []
    await loadCounts()
  } finally {
    loading.value = false
  }
}

const loadCounts = async () => {
  try {
    const statuses = ['', 'pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
    const counts = {}
    for (const s of statuses) {
      const r = await getCounselorOrders({ status: s, page_size: 1 })
      counts[s || 'all'] = r.data.total || 0
    }
    tabCounts.value = counts
  } catch {
    // 获取数量失败不影响主流程
  }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', confirmed: 'primary', in_progress: '', completed: 'success', cancelled: 'info' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { pending: '待确认', confirmed: '已确认', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
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

const agreeOrder = async (order) => {
  try {
    await ElMessageBox.confirm('确定接受此预约吗？', '提示', { type: 'warning' })
    await handleOrder(order.id, { action: 'agree' })
    ElMessage.success('已接受')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const rejectOrder = async (order) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝理由', '拒绝预约', {
      inputPattern: /.+/,
      inputErrorMessage: '请输入理由'
    })
    await handleOrder(order.id, { action: 'reject', reason: value })
    ElMessage.success('已拒绝')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const startChat = (order) => {
  router.push(`/consultation/counselor/${order.id}`)
}

const viewReview = (order) => {
  ElMessageBox.alert(
    `用户评分: ${order.rating ? '⭐'.repeat(order.rating) : '暂无评分'}\n\n${order.review || '用户暂未留下评价'}`,
    '评价详情',
    { confirmButtonText: '知道了' }
  )
}

onMounted(() => loadOrders())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-orders-page {
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
  flex-wrap: wrap;
}

.tab-btn {
  padding: 6px 16px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: $text-regular;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;

  &:hover { color: $primary-color; }

  &.active {
    background: $primary-color;
    color: #fff;
    box-shadow: 0 2px 8px rgba(232,132,90,0.35);
  }
}

.tab-count {
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.85;
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

  &.status-pending    .card-stripe { background: #e6a23c; }
  &.status-confirmed  .card-stripe { background: #409eff; }
  &.status-in_progress .card-stripe { background: #409eff; }
  &.status-completed  .card-stripe { background: #67c23a; }
  &.status-cancelled  .card-stripe { background: #909399; }
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
  margin-bottom: 14px;
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

// 问题描述
.problem-desc {
  padding: 10px 14px;
  background: #faf7f5;
  border-radius: 10px;
  margin-bottom: 2px;
  line-height: 1.55;

  .desc-label {
    font-size: 12px;
    color: $text-placeholder;
    font-weight: 500;
  }

  .desc-text {
    font-size: 13px;
    color: $text-secondary;
  }
}

// 操作按钮
.card-actions {
  display: flex;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid $border-lighter;
  margin-top: 4px;
}

@media (max-width: 480px) {
  .info-grid { grid-template-columns: 1fr; }
  .tab-bar { flex-wrap: wrap; }
}
</style>
