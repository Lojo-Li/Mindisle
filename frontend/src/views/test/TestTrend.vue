<template>
  <div class="test-trend">

    <div class="container">
      <!-- 顶部操作栏 -->
      <div class="trend-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>我的历史测试</h2>
        <el-button :icon="Download" @click="exportData">导出数据</el-button>
      </div>

      <!-- 筛选栏 -->
      <el-card class="filter-card">
        <div class="filter-row">
          <!-- 测试选择 -->
          <div class="filter-item">
            <span class="label">测试：</span>
            <el-select
              v-model="filters.testId"
              placeholder="选择测试"
              @change="handleFilterChange"
              style="width: 200px"
            >
              <el-option
                v-for="test in testOptions"
                :key="test.value"
                :label="test.label"
                :value="test.value"
              />
            </el-select>
          </div>

          <!-- 时间范围 -->
          <div class="filter-item">
            <span class="label">时间：</span>
            <el-select
              v-model="filters.timeRange"
              placeholder="选择时间范围"
              @change="handleFilterChange"
              style="width: 150px"
            >
              <el-option label="最近1个月" value="1month" />
              <el-option label="最近3个月" value="3months" />
              <el-option label="最近6个月" value="6months" />
              <el-option label="最近1年" value="1year" />
              <el-option label="全部" value="all" />
            </el-select>
          </div>
        </div>
      </el-card>

      <!-- 趋势图 -->
      <el-card v-loading="loading" class="chart-card">
        <template #header>
          <span>分数变化趋势</span>
        </template>

        <el-empty 
          v-if="!loading && trendData.length === 0" 
          :description="filters.testId ? '暂无数据' : '请选择一个测试查看趋势'" 
        />

        <div v-else class="chart-container" ref="chartRef"></div>
      </el-card>

      <!-- 历史记录 -->
      <el-card class="history-card">
        <template #header>
          <span>历史记录</span>
        </template>

        <el-table :data="historyRecords" style="width: 100%">
          <el-table-column prop="date" label="测试日期" width="180" />
          <el-table-column prop="testName" label="测试名称" />
          <el-table-column prop="score" label="得分" width="120">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.score, row.maxScore)">
                {{ row.score }}/{{ row.maxScore }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="等级" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)">
                {{ levelLabel(row.level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                text
                :icon="View"
                @click="viewResult(row.id)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, View } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getTestHistory, getTestTrend } from '@/api/test'
import { formatDate } from '@/utils/format'

const router = useRouter()

// 图表引用
const chartRef = ref(null)
let chartInstance = null

// 加载状态
const loading = ref(false)

// 测试选项
const testOptions = ref([
  { label: '全部测试', value: '' }
])

// 筛选条件
const filters = reactive({
  testId: '',
  timeRange: '6months'
})

// 趋势数据
const trendData = ref([])

// 历史记录
const historyRecords = ref([])

// 获取分数类型
const getScoreType = (score, maxScore) => {
  if (!score || !maxScore) return 'info'
  const percentage = (score / maxScore) * 100
  if (percentage >= 75) return 'success'
  if (percentage >= 50) return 'warning'
  return 'danger'
}

// 获取等级类型
const getLevelType = (level) => {
  const typeMap = {
    'normal': 'info',
    'none': 'info',
    'mild': 'warning',
    'moderate': 'warning',
    'severe': 'danger',
    'high': 'success',
    'medium': 'info',
    'low': 'warning',
    'good': 'success',
    'fair': 'warning',
    'poor': 'danger'
  }
  return typeMap[level] || 'info'
}

// 等级中文标签
const levelLabel = (level) => {
  const map = {
    'none': '正常',
    'normal': '正常',
    'mild': '轻度',
    'moderate': '中度',
    'severe': '重度',
    'high': '高',
    'medium': '中等',
    'low': '低',
    'good': '良好',
    'fair': '一般',
    'poor': '较差',
    'unknown': '无'
  }
  return map[level] || '正常'
}

// 加载历史记录
const loadHistory = async () => {
  try {
    loading.value = true
    const params = {
      testId: filters.testId || undefined
    }
    const res = await getTestHistory(params)
    // 映射后端 snake_case 字段到前端 camelCase 字段
    let items = (res.data.items || []).map(item => ({
      id: item.id,
      testId: item.test_id,
      date: item.created_at ? item.created_at.slice(0, 10) : '',
      testName: item.test_title || '未知测试',
      score: item.total_score,
      maxScore: item.max_score,
      level: item.result_level,
      levelTitle: item.result_title
    }))
    // 客户端时间范围过滤
    if (filters.timeRange && filters.timeRange !== 'all') {
      const now = new Date()
      const cutoff = new Date()
      const msMap = { '1month': 30, '3months': 90, '6months': 180, '1year': 365 }
      cutoff.setDate(cutoff.getDate() - (msMap[filters.timeRange] || 180))
      items = items.filter(item => {
        if (!item.date) return true
        return new Date(item.date) >= cutoff
      })
    }
    historyRecords.value = items
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载趋势数据
const loadTrend = async () => {
  if (!filters.testId) {
    trendData.value = []
    return
  }

  try {
    loading.value = true
    const res = await getTestTrend(filters.testId)
    // 映射后端趋势数据
    trendData.value = (res.data?.trend_data || []).map(item => ({
      date: item.date,
      score: item.score
    }))

    // 更新图表
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('加载趋势失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) return

  // 销毁旧图表
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新图表
  chartInstance = echarts.init(chartRef.value)

  // 准备数据
  const dates = trendData.value.map(item => item.date)
  const scores = trendData.value.map(item => item.score)

  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>得分: ${param.value}`
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
      name: '分数'
    },
    series: [
      {
        name: '得分',
        type: 'line',
        smooth: true,
        data: scores,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(232, 132, 90, 0.3)' },
            { offset: 1, color: 'rgba(232, 132, 90, 0.03)' }
          ])
        },
        lineStyle: {
          width: 3,
          color: '#e8845a'
        },
        itemStyle: {
          color: '#e8845a',
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          itemStyle: {
            color: '#e8845a',
            borderWidth: 4,
            borderColor: '#fff'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)

  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 筛选变化
const handleFilterChange = () => {
  loadHistory()
  if (filters.testId) {
    loadTrend()
  }
}

// 查看结果
const viewResult = (resultId) => {
  router.push(`/test/${resultId}/result`)
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

// 返回
const goBack = () => {
  router.push('/test')
}

// 组件挂载
onMounted(async () => {
  await loadHistory()
  // 自动选取最近一次测试，加载趋势图
  if (historyRecords.value.length > 0 && !filters.testId) {
    const firstRecord = historyRecords.value[0]
    if (firstRecord.testId) {
      filters.testId = firstRecord.testId
      await loadTrend()
    }
  }
})

// 组件卸载
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.test-trend {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 36px $spacing-lg;
}

.trend-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;

  h2 {
    flex: 1;
    margin: 0;
    color: $text-primary;
    font-weight: 700;
  }
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;

  :deep(.el-card__body) {
    padding: 20px 24px;
  }
}

.filter-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;

  .filter-item {
    display: flex;
    align-items: center;
    gap: 10px;

    .label {
      font-weight: 500;
      color: $text-regular;
      white-space: nowrap;
    }
  }
}

.chart-card {
  margin-bottom: 24px;
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
  }
}

.chart-container {
  width: 100%;
  height: 400px;
}

.history-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
  }

  :deep(.el-table) {
    background: transparent;

    th {
      background: $bg-page;
      color: $text-regular;
      font-weight: 600;
    }

    tr:hover td {
      background: rgba(232,132,90,0.04) !important;
    }
  }
}

@media (max-width: $breakpoint-md) {
  .filter-row {
    flex-direction: column;
    gap: $spacing-md;

    .filter-item {
      width: 100%;

      .el-select {
        width: 100% !important;
      }
    }
  }

  .chart-container {
    height: 300px;
  }
}
</style>
