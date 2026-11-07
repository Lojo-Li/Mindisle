<template>
  <div class="test-result">

    <div class="container">
      <!-- 顶部操作栏 -->
      <div class="result-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>测试结果报告</h2>
        <el-dropdown :icon="Share" @command="handleShare">
          <el-button circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="link">
                <el-icon><Link /></el-icon>
                复制链接
              </el-dropdown-item>
              <el-dropdown-item command="image">
                <el-icon><Picture /></el-icon>
                生成长图
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 结果卡片 -->
      <el-card v-loading="loading" class="result-card">
        <el-skeleton v-if="loading" :rows="8" animated />

        <div v-else class="result-content">
          <!-- 测试标题 -->
          <div class="test-title">
            <h1>{{ resultData.testName }} - 测试结果</h1>
          </div>

          <!-- 结果展示 -->
          <div class="score-section">
            <!-- 结果等级 -->
            <div class="result-level-large" :class="resultData.levelClass">
              <div class="level-content">
                <div class="level-label">测试结果</div>
                <div class="level-name">{{ resultData.level }}</div>
                <div class="level-description">{{ resultData.levelDescription }}</div>
              </div>
            </div>
          </div>

          <!-- AI建议卡片 -->
          <div v-if="resultData.aiSuggestion" class="ai-suggestion-card">
            <el-card>
              <template #header>
                <div class="card-header">
                  <div class="header-left">
                    <span class="card-title">AI智能建议</span>
                    <el-tag type="success" size="small">由AI生成</el-tag>
                  </div>
                </div>
              </template>

              <div class="ai-suggestion-content">
                <p>{{ resultData.aiSuggestion }}</p>
              </div>

              <template #footer>
                <div class="card-footer">
                  <el-button
                    type="primary"
                    @click="startAIChat"
                  >
                    与AI咨询师深入交流
                  </el-button>
                  <el-alert
                    type="info"
                    :closable="false"
                  >
                    AI建议仅供参考，不能替代专业心理咨询或医疗诊断
                  </el-alert>
                </div>
              </template>
            </el-card>
          </div>

          <!-- 结果描述 -->
          <div v-if="resultData.description" class="description-section">
            <h3>结果说明</h3>
            <p class="description-text">{{ resultData.description }}</p>
          </div>

          <!-- 维度分析 -->
          <div v-if="resultData.dimensions && resultData.dimensions.length > 0" class="dimensions-section">
            <h3>各维度得分</h3>
            <div class="dimensions-list">
              <div
                v-for="dimension in resultData.dimensions"
                :key="dimension.name"
                class="dimension-item"
              >
                <div class="dimension-info">
                  <span class="dimension-name">{{ dimension.name }}</span>
                  <span v-if="dimension.level" class="dimension-level">{{ getDimLevelText(dimension.level) }}</span>
                  <span class="dimension-score">{{ dimension.score }}/{{ dimension.maxScore }}</span>
                </div>
                <el-progress
                  :percentage="getDimensionPercentage(dimension)"
                  :color="getDimensionColor(dimension)"
                />
              </div>
            </div>
          </div>

          <!-- 建议 -->
          <div v-if="resultData.suggestions && resultData.suggestions.length > 0" class="suggestions-section">
            <h3>建议</h3>
            <div class="suggestions-list">
              <div
                v-for="(suggestion, index) in resultData.suggestions"
                :key="index"
                class="suggestion-item"
              >
                <span class="suggestion-number">{{ index + 1 }}</span>
                <span class="suggestion-text">{{ suggestion }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button :icon="TrendCharts" @click="viewTrend">
              查看详细分析
            </el-button>
            <el-button
              :type="resultData.isFavorited ? 'primary' : 'default'"
              :icon="resultData.isFavorited ? StarFilled : Star"
              @click="toggleFavorite"
            >
              {{ resultData.isFavorited ? '已收藏' : '收藏' }}
            </el-button>
            <el-button :icon="RefreshRight" @click="retakeTest">
              重新测试
            </el-button>
            <el-button type="danger" :icon="Delete" @click="handleDelete">
              删除记录
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 相关推荐 -->
      <el-card v-if="recommendations.length > 0" class="recommendations-card">
        <template #header>
          <span>相关推荐测试</span>
        </template>

        <div class="recommendations-list">
          <div
            v-for="test in recommendations"
            :key="test.id"
            class="recommendation-item"
            @click="goToTest(test.id)"
          >
            <img :src="test.coverImage" :alt="test.title" class="recommendation-cover" />
            <div class="recommendation-info">
              <h4>{{ test.title }}</h4>
              <p>{{ test.description }}</p>
            </div>
            <el-button type="primary" :icon="ArrowRight" circle />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Share,
  Link,
  Picture,
  TrendCharts,
  Star,
  StarFilled,
  RefreshRight,
  ArrowRight,
  Delete
} from '@element-plus/icons-vue'
import { getTestResult, favoriteResult, unfavoriteResult, deleteTestResult } from '@/api/test'

const router = useRouter()
const route = useRoute()

// 结果ID
const resultId = route.params.id

// 加载状态
const loading = ref(true)

// 结果数据
const resultData = ref({
  testName: '',
  testId: null,
  score: 0,
  maxScore: 0,
  level: '',
  levelClass: '',
  levelDescription: '',
  description: '',
  aiSuggestion: '',
  dimensions: [],
  suggestions: [],
  isFavorited: false
})

// 等级描述映射
const levelDescriptions = {
  '正常': '您的心理状态良好，没有明显异常。请继续保持良好的生活方式和健康习惯。',
  '轻度': '检测到一些轻微心理困扰，这在生活中很常见。建议通过运动、休息、社交等方式自我调节，一般能够自行缓解。',
  '中度': '您的心理状态需要关注。建议尝试放松技巧、规律作息，必要时可寻求专业心理咨询师的帮助。',
  '重度': '您的心理状态需要重视。建议尽快寻求专业心理咨询师或精神科医生的帮助，进行系统的评估和诊断。'
}

// 推荐测试
const recommendations = ref([])

// 计算等级样式
const levelConfig = {
  '正常': { class: 'level-none' },
  '轻度': { class: 'level-mild' },
  '中度': { class: 'level-moderate' },
  '重度': { class: 'level-severe' }
}

// 获取维度百分比
const getDimensionPercentage = (dimension) => {
  return Math.round((dimension.score / dimension.maxScore) * 100)
}

// 维度水平文字映射
const dimLevelMapping = {
  'none': '无',
  'mild': '轻度',
  'moderate': '中度',
  'severe': '重度',
  'low': '偏低',
  'medium': '中等',
  'high': '偏高',
  'medium_low': '偏低',
  'medium_high': '偏高',
  'good': '良好',
  'fair': '一般',
  'poor': '较差'
}

const getDimLevelText = (level) => dimLevelMapping[level] || '无'

const getDimensionColor = (dimension) => {
  const percentage = getDimensionPercentage(dimension)
  if (percentage >= 75) return '#67C23A'
  if (percentage >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 加载测试结果
const loadResult = async () => {
  try {
    loading.value = true
    const res = await getTestResult(resultId)

    const data = res.data

    // 处理等级配置 - 判断测试类型，适配临床量表和非临床量表
    const clinicalLevels = ['none', 'mild', 'moderate', 'severe']
    const isClinical = clinicalLevels.includes(data.result_level)

    let levelText, levelClass, levelDesc
    if (isClinical) {
      const levelMapping = {
        'none': '正常',
        'mild': '轻度',
        'moderate': '中度',
        'severe': '重度'
      }
      levelText = levelMapping[data.result_level] || '正常'
      levelDesc = levelDescriptions[levelText] || ''
      levelClass = levelConfig[levelText]?.class || 'level-none'
    } else {
      // 非临床量表（大五人格、自尊、情绪稳定性、睡眠等），直接使用后端返回的标题
      levelText = data.result_title || '分析完成'
      levelDesc = data.result_description || ''
      levelClass = 'level-neutral'
    }

    // 处理建议文本 - 转换为数组
    let suggestionsArray = []
    if (data.suggestions) {
      // 按句号或换行符分割建议
      suggestionsArray = data.suggestions
        .split(/[。\\n]/)
        .filter(s => s && s.trim())
        .map(s => s.trim())
    }

    // 处理维度得分 - 转换格式
    let dimensionsArray = []
    if (data.dimension_scores && Array.isArray(data.dimension_scores)) {
      dimensionsArray = data.dimension_scores.map(dim => ({
        name: dim.dimension,
        score: dim.score,
        maxScore: dim.max_score || Math.round(dim.score * 2) || 100,
        level: dim.level
      }))
    }

    resultData.value = {
      testName: data.test_title || '测试',
      testId: data.test_id,
      score: data.total_score || 0,
      maxScore: 100,
      level: levelText,
      levelClass: levelClass,
      levelDescription: levelDesc,
      description: data.result_description || '',
      aiSuggestion: data.ai_suggestion || '',
      dimensions: dimensionsArray,
      suggestions: suggestionsArray,
      isFavorited: data.is_favorite || false
    }

    recommendations.value = data.recommendations || []
  } catch (error) {
    console.error('加载结果失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    if (resultData.value.isFavorited) {
      await unfavoriteResult(resultId)
      resultData.value.isFavorited = false
      ElMessage.success('取消收藏')
    } else {
      await favoriteResult(resultId)
      resultData.value.isFavorited = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 查看趋势
const viewTrend = () => {
  router.push('/test/trend?testId=' + resultData.value.testId)
}

// 重新测试
const retakeTest = () => {
  router.push(`/test/${resultData.value.testId}/taking`)
}

// 删除结果
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此测试记录吗？删除后无法恢复。',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteTestResult(resultId)
    ElMessage.success('删除成功')
    router.push('/test')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 开始AI深度咨询
const startAIChat = () => {
  // 跳转到智能问答页面，携带测试结果ID
  router.push({
    path: '/chat',
    query: {
      result_id: resultId,
      type: 'test_result'
    }
  })
}

// 跳转到推荐测试
const goToTest = (testId) => {
  router.push(`/test/${testId}`)
}

// 返回
const goBack = () => {
  router.push('/test')
}

// 分享
const handleShare = (command) => {
  if (command === 'link') {
    // 复制链接
    const url = window.location.href
    navigator.clipboard.writeText(url).then(() => {
      ElMessage.success('链接已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  } else if (command === 'image') {
    ElMessage.info('生成长图功能开发中...')
  }
}

// 组件挂载
onMounted(() => {
  loadResult()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.test-result {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 36px $spacing-lg;
}

.result-header {
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

.result-card {
  margin-bottom: 24px;
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__body) {
    padding: 32px;
  }
}

.result-content {
  .test-title {
    text-align: center;
    margin-bottom: $spacing-xl;

    h1 {
      font-size: $font-size-extra-large;
      margin: 0;
    }
  }

  .score-section {
    display: flex;
    justify-content: center;
    margin-bottom: $spacing-xl;
    padding: $spacing-xl;

    .result-level-large {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-lg;
      padding: 40px;
      border-radius: 24px;
      width: 100%;
      max-width: 500px;
      text-align: center;

      &.level-none {
        background: linear-gradient(135deg, #a8e6cf 0%, #56ab91 100%);
        color: white;
      }

      &.level-mild {
        background: linear-gradient(135deg, #fde8d8 0%, #f4a57a 100%);
        color: #3d2b1f;
      }

      &.level-moderate {
        background: linear-gradient(135deg, #f4a57a 0%, #e8845a 100%);
        color: white;
      }

      &.level-severe {
        background: linear-gradient(135deg, #e8845a 0%, #c96f42 100%);
        color: white;
      }

      &.level-neutral {
        background: linear-gradient(135deg, #a0c4f0 0%, #6b8fc4 100%);
        color: white;
      }

      .level-content {
        display: flex;
        flex-direction: column;
        gap: 10px;

        .level-label {
          font-size: $font-size-small;
          opacity: 0.85;
          text-transform: uppercase;
          letter-spacing: 2px;
          font-weight: 500;
        }

        .level-name {
          font-size: 36px;
          font-weight: 800;
        }

        .level-description {
          font-size: $font-size-base;
          line-height: 1.7;
          opacity: 0.92;
          max-width: 400px;
          margin: 0 auto;
        }
      }
    }
  }

  .description-section {
    margin-bottom: $spacing-xl;
    padding: 20px 24px;
    background: rgba(232,132,90,0.06);
    border-radius: 16px;
    border-left: 4px solid $primary-color;

    h3 {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: $font-size-large;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: $spacing-md;
    }

    .description-text {
      font-size: $font-size-base;
      line-height: 1.8;
      color: $text-regular;
      margin: 0;
    }
  }

  .dimensions-section,
  .suggestions-section {
    margin-bottom: $spacing-xl;

    h3 {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: $font-size-large;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: $spacing-md;
    }
  }

  .dimensions-list {
    .dimension-item {
      margin-bottom: 16px;

      .dimension-info {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;

        .dimension-name {
          font-weight: 500;
          color: $text-primary;
        }

        .dimension-level {
          font-size: 11px;
          color: #909399;
          background: #f0f2f5;
          padding: 1px 8px;
          border-radius: 10px;
        }

        .dimension-score {
          margin-left: auto;
          color: $text-secondary;
          font-size: 13px;
          font-weight: 600;
        }
      }
    }
  }

  .suggestions-list {
    .suggestion-item {
      display: flex;
      gap: 14px;
      padding: 16px 18px;
      background: $bg-page;
      border: 1px solid $border-lighter;
      border-radius: 14px;
      margin-bottom: 10px;

      .suggestion-number {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: $primary-gradient;
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 13px;
      }

      .suggestion-text {
        flex: 1;
        line-height: 1.8;
        color: $text-regular;
      }
    }
  }

  .ai-suggestion-card {
    margin-bottom: $spacing-xl;
    border-radius: 16px !important;
    border: 1px solid rgba(232,132,90,0.2) !important;
    background: linear-gradient(135deg, rgba(253,232,216,0.5) 0%, rgba(253,212,192,0.3) 100%) !important;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .header-left {
        display: flex;
        align-items: center;
        gap: $spacing-sm;

        .card-title {
          font-size: $font-size-large;
          font-weight: 600;
          color: $text-primary;
        }
      }
    }

    .ai-suggestion-content {
      padding: $spacing-md 0;
      line-height: 1.8;

      p {
        font-size: $font-size-base;
        color: $text-primary;
        margin: 0;
        white-space: pre-wrap;
      }
    }

    .card-footer {
      display: flex;
      flex-direction: column;
      gap: $spacing-md;

      .el-alert {
        font-size: $font-size-small;
      }
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: $spacing-md;
    flex-wrap: wrap;
  }
}

.recommendations-card {
  .recommendations-list {
    .recommendation-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-md;
      border: 1px solid $border-lighter;
      border-radius: $border-radius-md;
      cursor: pointer;
      transition: $transition-base;

      &:hover {
        border-color: $primary-color;
        background: rgba($primary-color, 0.05);
      }

      .recommendation-cover {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: $border-radius-sm;
      }

      .recommendation-info {
        flex: 1;

        h4 {
          margin: 0 0 $spacing-xs;
        }

        p {
          margin: 0;
          font-size: $font-size-small;
          color: $text-secondary;
        }
      }
    }
  }
}

@media (max-width: $breakpoint-md) {
  .action-buttons {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }

  .result-level-large {
    .level-content {
      .level-name {
        font-size: 28px;
      }

      .level-description {
        font-size: $font-size-small;
      }
    }
  }
}
</style>

