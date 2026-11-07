<template>
  <div class="counselor-dashboard-page">

    <div class="container">
      <!-- 欢迎卡片 -->
      <el-card class="welcome-card">
        <div class="welcome-content">
          <div class="avatar-section">
            <el-avatar :size="80" :src="counselorInfo?.avatar">
              <el-icon :size="40"><User /></el-icon>
            </el-avatar>
          </div>
          <div class="info-section">
            <h2>欢迎，{{ counselorInfo?.name || '咨询师' }}</h2>
            <p class="subtitle">咨询师工作台</p>
            <div class="stats">
              <div class="stat-item">
                <span class="label">评分：</span>
                <el-rate :model-value="counselorInfo?.rating" disabled show-score text-color="#ff9900" />
              </div>
              <div class="stat-item">
                <span class="label">咨询次数：</span>
                <span class="value">{{ counselorInfo?.consultation_count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="label">状态：</span>
                <el-tag :type="statusType">{{ statusText }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 快捷入口 -->
      <el-card class="quick-access-card">
        <template #header>
          <span>快捷入口</span>
        </template>

        <div class="quick-access-grid">
          <div class="access-item" @click="navigateTo('/consultation/counselor/orders')">
            <div class="access-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <span>预约管理</span>
          </div>

          <div class="access-item" @click="navigateTo('/profile')">
            <div class="access-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <span>个人资料</span>
          </div>

          <div class="access-item" @click="navigateTo('/counselor')">
            <div class="access-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="32"><View /></el-icon>
            </div>
            <span>我的主页</span>
          </div>

          <div class="access-item" @click="navigateTo('/chat')">
            <div class="access-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
              <el-icon :size="32"><ChatDotSquare /></el-icon>
            </div>
            <span>智能问答</span>
          </div>
        </div>
      </el-card>

      <!-- 数据统计 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
                <el-icon :size="28"><Calendar /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.totalOrders || 0 }}</div>
                <div class="stat-label">总订单数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
                <el-icon :size="28"><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.pendingOrders || 0 }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
                <el-icon :size="28"><ChatDotRound /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.completedOrders || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
                <el-icon :size="28"><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ counselorInfo?.rating || 5.0 }}</div>
                <div class="stat-label">平均评分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近预约 -->
      <el-card class="recent-orders-card">
        <template #header>
          <div class="card-header">
            <span>最近预约</span>
            <el-button type="primary" link @click="navigateTo('/consultation/counselor/orders')">
              查看全部
            </el-button>
          </div>
        </template>

        <el-empty v-if="!recentOrders || recentOrders.length === 0" description="暂无预约" />
        <div v-else class="orders-list">
          <div
            v-for="order in recentOrders"
            :key="order.id"
            class="order-item"
            @click="viewOrder(order)"
          >
            <div class="order-info">
              <div class="order-title">
                <el-tag :type="getOrderStatusType(order.status)" size="small">
                  {{ getOrderStatusText(order.status) }}
                </el-tag>
                <span class="order-no">{{ order.appointment_no }}</span>
              </div>
              <div class="order-detail">
                <span>{{ formatDate(order.appointment_date) }}</span>
                <span>{{ order.consultation_type === 'video' ? '视频' : order.consultation_type === 'voice' ? '语音' : '线下' }}</span>
              </div>
            </div>
            <el-icon :size="20"><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  User,
  Calendar,
  ChatDotSquare,
  View,
  Clock,
  ChatDotRound,
  Star,
  ArrowRight
} from '@element-plus/icons-vue'
import { getApplicationStatus } from '@/api/counselor'
import { getCounselorOrders } from '@/api/consultation'
import dayjs from 'dayjs'

const router = useRouter()

// 咨询师信息
const counselorInfo = ref(null)

// 统计数据
const statistics = ref({
  totalOrders: 0,
  pendingOrders: 0,
  completedOrders: 0
})

// 最近预约
const recentOrders = ref([])

// 状态计算
const statusType = computed(() => {
  const status = counselorInfo.value?.status
  if (status === 'active') return 'success'
  if (status === 'pending_review') return 'warning'
  if (status === 'inactive') return 'info'
  return 'danger'
})

const statusText = computed(() => {
  const status = counselorInfo.value?.status
  if (status === 'active') return '已激活'
  if (status === 'pending_review') return '审核中'
  if (status === 'inactive') return '未激活'
  return '已封禁'
})

// 加载咨询师信息
const loadCounselorInfo = async () => {
  try {
    const res = await getApplicationStatus()
    if (res.data && res.data.has_applied) {
      counselorInfo.value = res.data
    }
  } catch (error) {
    console.error('加载咨询师信息失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    // 获取所有订单来计算统计数据
    const res = await getCounselorOrders({ page: 1, page_size: 100 })
    const orders = res.data.items || []

    // 计算统计数据
    const totalOrders = orders.length
    const pendingOrders = orders.filter(o => o.status === 'pending').length
    const completedOrders = orders.filter(o => o.status === 'completed').length

    statistics.value = {
      totalOrders,
      pendingOrders,
      completedOrders
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    statistics.value = {
      totalOrders: 0,
      pendingOrders: 0,
      completedOrders: 0
    }
  }
}

// 加载最近预约
const loadRecentOrders = async () => {
  try {
    // 获取最近的5条订单
    const res = await getCounselorOrders({ page: 1, page_size: 5 })
    recentOrders.value = res.data.items || []
  } catch (error) {
    console.error('加载最近预约失败:', error)
    recentOrders.value = []
  }
}

// 导航
const navigateTo = (path) => {
  router.push(path)
}

// 查看订单
const viewOrder = (order) => {
  router.push(`/consultation/user/${order.id}`)
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const textMap = {
    pending: '待确认',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

// 组件挂载
onMounted(() => {
  loadCounselorInfo()
  loadStatistics()
  loadRecentOrders()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-dashboard-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.welcome-card {
  margin-bottom: $spacing-lg;

  .welcome-content {
    display: flex;
    align-items: center;
    gap: $spacing-xl;

    .info-section {
      flex: 1;

      h2 {
        margin: 0 0 $spacing-xs;
        font-size: $font-size-extra-large;
      }

      .subtitle {
        color: $text-secondary;
        margin-bottom: $spacing-md;
      }

      .stats {
        display: flex;
        gap: $spacing-xl;

        .stat-item {
          display: flex;
          align-items: center;
          gap: $spacing-sm;

          .label {
            color: $text-secondary;
          }

          .value {
            font-weight: 600;
            color: $text-primary;
          }
        }
      }
    }
  }
}

.quick-access-card {
  margin-bottom: $spacing-lg;

  .quick-access-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: $spacing-md;
  }

  .access-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $spacing-lg;
    border: 1px solid $border-lighter;
    border-radius: $border-radius-md;
    cursor: pointer;
    transition: $transition-base;

    &:hover {
      border-color: $primary-color;
      background: rgba($primary-color, 0.05);
    }

    .access-icon {
      width: 60px;
      height: 60px;
      border-radius: $border-radius-md;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      margin-bottom: $spacing-sm;
    }

    span {
      font-size: $font-size-base;
      color: $text-primary;
    }
  }
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: $border-radius-md;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .stat-info {
      flex: 1;

      .stat-number {
        font-size: 24px;
        font-weight: 600;
        color: $text-primary;
        line-height: 1.2;
      }

      .stat-label {
        font-size: $font-size-small;
        color: $text-secondary;
      }
    }
  }
}

.recent-orders-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .orders-list {
    .order-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: $spacing-md;
      border: 1px solid $border-lighter;
      border-radius: $border-radius-md;
      margin-bottom: $spacing-sm;
      cursor: pointer;
      transition: $transition-base;

      &:hover {
        border-color: $primary-color;
        background: rgba($primary-color, 0.05);
      }

      .order-info {
        flex: 1;

        .order-title {
          display: flex;
          align-items: center;
          gap: $spacing-sm;
          margin-bottom: $spacing-xs;

          .order-no {
            font-weight: 500;
            color: $text-primary;
          }
        }

        .order-detail {
          display: flex;
          gap: $spacing-md;
          font-size: $font-size-small;
          color: $text-secondary;
        }
      }
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .welcome-content {
    flex-direction: column;
    text-align: center;

    .info-section {
      .stats {
        flex-direction: column;
        gap: $spacing-sm;
      }
    }
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
