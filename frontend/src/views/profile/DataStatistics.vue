<template>
  <div class="data-statistics">
    <div class="ds-container">

      <!-- 页头 -->
      <div class="ds-header">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <h2>我的数据统计</h2>
        <el-select v-model="timeRange" @change="handleTimeRangeChange" style="width:130px">
          <el-option label="最近7天"  value="7days" />
          <el-option label="最近30天" value="30days" />
          <el-option label="最近90天" value="90days" />
        </el-select>
      </div>

      <!-- 概览卡片 -->
      <div class="ds-stats-grid">
        <div class="ds-stat-card">
          <div class="ds-stat-icon" style="--c:#e8845a">
            <el-icon :size="22"><DocumentCopy /></el-icon>
          </div>
            <div class="ds-stat-num">{{ overviewData.test_count || 0 }}</div>
          <div class="ds-stat-lbl">心理测试</div>
        </div>
        <div class="ds-stat-card">
          <div class="ds-stat-icon" style="--c:#9b8bb4">
            <el-icon :size="22"><ChatDotSquare /></el-icon>
          </div>
            <div class="ds-stat-num">{{ overviewData.chat_count || 0 }}</div>
          <div class="ds-stat-lbl">对话次数</div>
        </div>
        <div class="ds-stat-card">
          <div class="ds-stat-icon" style="--c:#56ab91">
            <el-icon :size="22"><Calendar /></el-icon>
          </div>
            <div class="ds-stat-num">{{ overviewData.appointment_count || 0 }}</div>
          <div class="ds-stat-lbl">预约次数</div>
        </div>
        <div class="ds-stat-card">
          <div class="ds-stat-icon" style="--c:#f4a57a">
            <el-icon :size="22"><Star /></el-icon>
          </div>
            <div class="ds-stat-num">{{ overviewData.favorite_count || 0 }}</div>
          <div class="ds-stat-lbl">收藏文章</div>
        </div>
      </div>

      <!-- 活动趋势 -->
      <el-card v-if="allowTrendAnalysis" v-loading="loading" class="ds-chart-card">
        <template #header><span>活动趋势</span></template>
        <div class="ds-chart" ref="activityChartRef"></div>
      </el-card>

      <el-card v-else class="ds-chart-card ds-disabled">
        <template #header><span>活动趋势</span></template>
        <div class="ds-disabled-tip">
          <el-icon :size="36"><Lock /></el-icon>
          <p>趋势分析已在隐私设置中关闭</p>
          <el-button type="primary" plain size="small" @click="$router.push('/profile/privacy')">前往开启</el-button>
        </div>
      </el-card>

      <!-- 分布图 -->
      <div class="ds-charts-row" v-if="allowTrendAnalysis">
        <el-card v-loading="loading" class="ds-chart-card">
          <template #header><span>测试分类分布</span></template>
          <div class="ds-chart ds-chart-sm" ref="testChartRef"></div>
        </el-card>
        <el-card v-loading="loading" class="ds-chart-card">
          <template #header><span>对话主题分布</span></template>
          <div class="ds-chart ds-chart-sm" ref="chatChartRef"></div>
        </el-card>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DocumentCopy, ChatDotSquare, Calendar, Star, Lock } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  getUserStatistics,
  getActivityTrend,
  getTestDistribution,
  getChatDistribution,
  getPrivacySettings
} from '@/api/user'

const router = useRouter()

// 图表引用
const activityChartRef = ref(null)
const testChartRef = ref(null)
const chatChartRef = ref(null)

let activityChart = null
let testChart = null
let chatChart = null

// 时间范围
const timeRange = ref('30days')

// 加载状态
const loading = ref(false)

// 趋势分析开关
const allowTrendAnalysis = ref(true)

// 总览数据
const overviewData = ref({
  test_count: 0,
  chat_count: 0,
  appointment_count: 0,
  favorite_count: 0
})

// 加载统计数据
const loadStatistics = async () => {
  try {
    loading.value = true
    const res = await getUserStatistics({ timeRange: timeRange.value })
    overviewData.value = res.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载活动趋势
const loadActivityTrend = async () => {
  try {
    const res = await getActivityTrend({ timeRange: timeRange.value })
    const data = res.data || []

    await nextTick()
    renderActivityChart(data)
  } catch (error) {
    console.error('加载活动趋势失败:', error)
  }
}

// 加载测试分类分布
const loadTestDistribution = async () => {
  try {
    const res = await getTestDistribution()
    const data = res.data || []

    await nextTick()
    renderTestChart(data)
  } catch (error) {
    console.error('加载测试分布失败:', error)
  }
}

// 加载对话主题分布
const loadChatDistribution = async () => {
  try {
    const res = await getChatDistribution()
    const data = res.data || []

    await nextTick()
    renderChatChart(data)
  } catch (error) {
    console.error('加载对话分布失败:', error)
  }
}

// 渲染活动趋势图
const renderActivityChart = (data) => {
  if (!activityChartRef.value) return

  if (activityChart) {
    activityChart.dispose()
  }

  activityChart = echarts.init(activityChartRef.value)

  const dates = data.map(item => item.date)
  const activities = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>活动次数: ${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '次数'
    },
    series: [
      {
        name: '活动次数',
        type: 'line',
        smooth: true,
        data: activities,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(232, 132, 90, 0.3)' },
            { offset: 1, color: 'rgba(232, 132, 90, 0.03)' }
          ])
        },
        lineStyle: {
          width: 3,
          color: '#e8845a',
          borderWidth: 2,
          borderColor: '#fff'
        }
      }
    ]
  }

  activityChart.setOption(option)
}

// 渲染测试分类饼图
const renderTestChart = (data) => {
  if (!testChartRef.value) return

  if (testChart) {
    testChart.dispose()
  }

  testChart = echarts.init(testChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center'
    },
    series: [
      {
        name: '测试分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }

  testChart.setOption(option)
}

// 渲染对话主题柱状图
const renderChatChart = (data) => {
  if (!chatChartRef.value) return

  if (chatChart) {
    chatChart.dispose()
  }

  chatChart = echarts.init(chatChartRef.value)

  const categories = data.map(item => item.name)
  const counts = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '对话数'
    },
    series: [
      {
        name: '对话数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 1, color: '#188df0' }
          ]),
          borderRadius: [5, 5, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }

  chatChart.setOption(option)
}

// 时间范围变化
const handleTimeRangeChange = () => {
  loadStatistics()
  loadActivityTrend()
}

// 返回
const goBack = () => {
  router.push('/profile')
}

// 响应式图表
const handleResize = () => {
  activityChart?.resize()
  testChart?.resize()
  chatChart?.resize()
}

// 组件挂载
onMounted(async () => {
  // 先加载隐私设置
  try {
    const privRes = await getPrivacySettings()
    const privacy = privRes.data || {}
    allowTrendAnalysis.value = privacy.allow_trend_analysis !== false
  } catch {
    allowTrendAnalysis.value = true
  }

  await loadStatistics()
  if (allowTrendAnalysis.value) {
    await loadActivityTrend()
    await loadTestDistribution()
    await loadChatDistribution()
  }

  window.addEventListener('resize', handleResize)
})

// 组件卸载
onBeforeUnmount(() => {
  activityChart?.dispose()
  testChart?.dispose()
  chatChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.data-statistics {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.ds-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

// 页头
.ds-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  h2 { margin: 0; font-size: 22px; font-weight: 700; color: $text-primary; flex: 1; }
}

// 概览卡片网格
.ds-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 28px;
  @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); }
}

.ds-stat-card {
  background: #fff;
  border-radius: 18px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}

.ds-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--c, #e8845a);
  opacity: 0.85;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.ds-stat-num {
  font-size: 32px;
  font-weight: 800;
  color: $text-primary;
  line-height: 1;
}

.ds-stat-lbl {
  font-size: 13px;
  color: $text-secondary;
}

// 图表卡片
.ds-chart-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;
  margin-bottom: 24px;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
  }
}

.ds-chart { width: 100%; height: 350px; }
.ds-chart-sm { height: 280px; }

.ds-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

// 趋势关闭占位符
.ds-disabled {
  .ds-disabled-tip {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #bbb;
    gap: 12px;
    p { margin: 0; font-size: 14px; }
  }
}
</style>
