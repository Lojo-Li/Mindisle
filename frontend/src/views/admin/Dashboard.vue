<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-content">
          <p class="stat-value">{{ stats.users }}</p>
          <p class="stat-label">用户总数</p>
        </div>
        <el-icon :size="48" color="#fff"><User /></el-icon>
      </div>

      <div class="stat-card red">
        <div class="stat-content">
          <p class="stat-value">{{ stats.counselors }}</p>
          <p class="stat-label">咨询师总数</p>
        </div>
        <el-icon :size="48" color="#fff"><UserFilled /></el-icon>
      </div>

      <div class="stat-card cyan">
        <div class="stat-content">
          <p class="stat-value">{{ stats.orders }}</p>
          <p class="stat-label">订单总数</p>
        </div>
        <el-icon :size="48" color="#fff"><List /></el-icon>
      </div>

      <div class="stat-card orange">
        <div class="stat-content">
          <p class="stat-value">{{ stats.tests }}</p>
          <p class="stat-label">测试完成数</p>
        </div>
        <el-icon :size="48" color="#fff"><Notebook /></el-icon>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>订单统计</h3>
        </div>
        <div ref="orderChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>用户增长趋势</h3>
        </div>
        <div ref="userChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- 公告列表 -->
    <div class="announcement-card">
      <div class="card-header">
        <h3>公告列表</h3>
        <el-button type="primary" size="small" @click="handleAddAnnouncement">发布公告</el-button>
      </div>
      <div class="announcement-list">
        <el-empty v-if="announcements.length === 0" description="暂无公告" />
        <div v-for="item in announcements" :key="item.id" class="announcement-item">
          <div class="announcement-content">
            <h4>{{ item.title }}</h4>
            <p>{{ item.content }}</p>
            <span class="announcement-date">{{ item.date }}</span>
          </div>
          <div class="announcement-actions">
            <el-button type="primary" text size="small" @click="handleEditAnnouncement(item)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDeleteAnnouncement(item)">删除</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, UserFilled, List, Notebook } from '@element-plus/icons-vue'
import { getDashboardStats, getChartData, getAdminTestList } from '@/api/admin'
import * as echarts from 'echarts'

// 统计数据
const stats = ref({
  users: 0,
  counselors: 0,
  orders: 0,
  tests: 0
})

// 公告列表（后端暂无公告 API，保留占位）
const announcements = ref([])

const orderChartRef = ref(null)
const userChartRef = ref(null)

let orderChart = null
let userChart = null

// 生成最近N天的日期数组
const getRecentDates = (days) => {
  const dates = []
  const today = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}-${date.getDate()}`)
  }
  return dates
}

// 初始化订单统计图表（先用空数据，数据加载后更新）
const initOrderChart = () => {
  if (!orderChartRef.value) return
  orderChart = echarts.init(orderChartRef.value)
  orderChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: getRecentDates(7) },
    yAxis: { type: 'value' },
    series: [{
      name: '订单数', type: 'line', smooth: true, data: [],
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
        { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
      ])},
      lineStyle: { color: '#3b82f6', width: 2 },
      itemStyle: { color: '#3b82f6' }
    }]
  })
}

// 初始化用户增长图表（空数据，加载后更新）
const initUserChart = () => {
  if (!userChartRef.value) return
  userChart = echarts.init(userChartRef.value)
  userChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: getRecentDates(30) },
    yAxis: { type: 'value' },
    series: [{
      name: '新增用户', type: 'line', smooth: true, data: [],
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(6, 182, 212, 0.3)' },
        { offset: 1, color: 'rgba(6, 182, 212, 0.05)' }
      ])},
      lineStyle: { color: '#06b6d4', width: 2 },
      itemStyle: { color: '#06b6d4' }
    }]
  })
}

// 更新订单图表数据（最近7天活动趋势）
const updateOrderChart = async () => {
  try {
    const res = await getChartData('trend')
    const points = res.data?.data || []
    orderChart?.setOption({
      xAxis: { data: points.map(p => p.date) },
      series: [{ data: points.map(p => p.value) }]
    })
  } catch { /* 图表数据加载失败不影响主面板 */ }
}

// 更新用户增长图表数据（最近30天）
const updateUserChart = async () => {
  try {
    const res = await getChartData('user')
    const points = res.data?.data || []
    userChart?.setOption({
      xAxis: { data: points.map(p => p.date) },
      series: [{ data: points.map(p => p.value) }]
    })
  } catch { /* 图表数据加载失败不影响主面板 */ }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const [statsRes, testRes] = await Promise.all([
      getDashboardStats(),
      getAdminTestList({ page: 1, pageSize: 1 })
    ])
    const data = statsRes.data || {}
    stats.value = {
      users: data.user_count || 0,
      counselors: data.counselor_count || 0,
      orders: data.order_count || 0,
      tests: testRes.data?.total || 0
    }
  } catch {
    // 加载失败保持默认值 0
  }
}

// 公告操作
const handleAddAnnouncement = () => {
  ElMessage.info('发布公告功能开发中...')
}

const handleEditAnnouncement = (item) => {
  ElMessage.info('编辑公告功能开发中...')
}

const handleDeleteAnnouncement = (item) => {
  ElMessage.info('删除公告功能开发中...')
}

onMounted(async () => {
  initOrderChart()
  initUserChart()
  await loadStats()
  // 图表数据异步加载（不阻塞首屏）
  updateOrderChart()
  updateUserChart()

  window.addEventListener('resize', () => {
    orderChart?.resize()
    userChart?.resize()
  })
})

onUnmounted(() => {
  orderChart?.dispose()
  userChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-card.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-card.red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card.cyan {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.stat-card.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chart-container {
  height: 300px;
}

/* 公告列表 */
.announcement-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.announcement-item:hover {
  background: #f3f4f6;
}

.announcement-content {
  flex: 1;
}

.announcement-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.announcement-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #6b7280;
}

.announcement-date {
  font-size: 12px;
  color: #9ca3af;
}

.announcement-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 28px;
  }

  .announcement-card {
    padding: 16px;
  }
}
</style>
