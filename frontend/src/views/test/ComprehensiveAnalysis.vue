<template>
  <div class="comprehensive-analysis">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>综合心理分析报告</h2>
        <div></div>
      </div>

      <!-- 主内容区 -->
      <el-card v-loading="loading" class="main-card">
        <!-- 空状态 -->
        <el-empty
          v-if="!loading && (!analysisData || error)"
          :description="error || '暂无数据'"
        >
          <el-button type="primary" @click="goBack">返回测试列表</el-button>
        </el-empty>

        <!-- 分析内容 -->
        <div v-else-if="analysisData" class="analysis-content">
          <!-- 用户信息卡片 -->
          <div class="user-info-section">
            <h3>👤 基本信息</h3>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="昵称">
                {{ analysisData.user_info.nickname || '未设置' }}
              </el-descriptions-item>
              <el-descriptions-item label="性别">
                {{ formatGender(analysisData.user_info.gender) }}
              </el-descriptions-item>
              <el-descriptions-item label="年龄">
                {{ analysisData.user_info.age || '未设置' }}岁
              </el-descriptions-item>
              <el-descriptions-item label="个人简介" :span="3">
                {{ analysisData.user_info.bio || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 分析周期 -->
          <div class="analysis-period-section">
            <h3>📅 分析周期</h3>
            <el-alert
              :title="`最近 ${analysisData.analysis_period.days} 天`"
              type="info"
              :closable="false"
            >
              <template #default>
                <div class="period-info">
                  <p>测试次数：<strong>{{ analysisData.analysis_period.test_count }}</strong> 次</p>
                  <p>
                    分析范围：<strong>{{ analysisData.analysis_period.earliest_test }}</strong>
                    至 <strong>{{ analysisData.analysis_period.latest_test }}</strong>
                  </p>
                </div>
              </template>
            </el-alert>
          </div>

          <!-- 测试记录概览 -->
          <div class="test-summary-section">
            <h3>📊 测试记录概览</h3>
            <div class="test-list">
              <el-card
                v-for="(test, index) in analysisData.test_summary"
                :key="index"
                class="test-item"
                shadow="hover"
              >
                <div class="test-item-header">
                  <span class="test-title">{{ test.test_title }}</span>
                  <el-tag :type="getLevelType(test.result_level)" size="small">
                    {{ formatLevel(test.result_level) }}
                  </el-tag>
                </div>
                <div class="test-item-body">
                  <div class="test-score">
                    <span class="score-label">得分：</span>
                    <span class="score-value">{{ test.total_score }}</span>
                  </div>
                  <div class="test-result">{{ test.result_title }}</div>
                  <div class="test-date">测试时间：{{ test.completed_at }}</div>
                </div>
              </el-card>
            </div>
          </div>

          <!-- AI分析报告 -->
          <div class="ai-report-section">
            <div class="section-header">
              <h3>🤖 AI综合分析报告</h3>
              <el-tag type="success" size="small">
                <el-icon><MagicStick /></el-icon>
                AI生成
              </el-tag>
            </div>

            <el-card class="ai-report-card">
              <div class="markdown-content" v-html="formattedAIAnalysis"></div>

              <template #footer>
                <div class="report-footer">
                  <el-alert
                    type="warning"
                    :closable="false"
                    show-icon
                  >
                    <template #title>
                      <strong>重要提示</strong>
                    </template>
                    <p>本报告由AI生成，仅供参考，不能替代专业心理咨询或医疗诊断。如有严重心理困扰，请及时寻求专业心理咨询师的帮助。</p>
                  </el-alert>

                  <div class="action-buttons">
                    <el-button type="primary" @click="startAIChat">
                      <el-icon><ChatDotRound /></el-icon>
                      与AI咨询师深入交流
                    </el-button>
                    <el-button @click="regenerate" :loading="regenerating">
                      <el-icon><Refresh /></el-icon>
                      重新生成
                    </el-button>
                  </div>
                </div>
              </template>
            </el-card>
          </div>

          <!-- 生成时间 -->
          <div class="generated-time">
            <el-text type="info" size="small">
              生成时间：{{ analysisData.generated_at }}
            </el-text>
          </div>
        </div>
      </el-card>

      <!-- 重新生成按钮（浮动） -->
      <div v-if="analysisData && !loading" class="floating-actions">
        <el-button
          type="primary"
          :icon="Refresh"
          circle
          size="large"
          @click="regenerate"
          :loading="regenerating"
          title="重新生成报告"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  MagicStick,
  ChatDotRound,
  Refresh
} from '@element-plus/icons-vue'
import { getComprehensiveAnalysis } from '@/api/test'

const router = useRouter()
const route = useRoute()

// 数据状态
const loading = ref(false)
const regenerating = ref(false)
const error = ref('')
const analysisData = ref(null)

// 分析天数（从路由参数获取，默认90天）
const days = ref(parseInt(route.query.days) || 90)

// 格式化性别
const formatGender = (gender) => {
  const genderMap = {
    'male': '男',
    'female': '女',
    'secret': '保密'
  }
  return genderMap[gender] || '未设置'
}

// 格式化等级
const formatLevel = (level) => {
  const levelMap = {
    'none': '正常',
    'mild': '轻度',
    'moderate': '中度',
    'severe': '重度',
    'high': '高',
    'medium': '中等',
    'low': '低',
    'good': '良好',
    'fair': '一般',
    'poor': '较差'
  }
  return levelMap[level] || level
}

// 获取等级对应的标签类型
const getLevelType = (level) => {
  const typeMap = {
    'none': 'success',
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

// 格式化AI分析报告（将Markdown转换为HTML）
const formattedAIAnalysis = computed(() => {
  if (!analysisData.value?.ai_analysis) return ''

  let html = analysisData.value.ai_analysis

  // 转换Markdown标题
  html = html.replace(/### (.*)/g, '<h4>$1</h4>')
  html = html.replace(/## (.*)/g, '<h3>$1</h3>')

  // 转换加粗
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 转换段落
  html = html.split('\n\n').map(p => `<p>${p}</p>`).join('')

  // 转换列表
  html = html.replace(/- (.*)/g, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')

  return html
})

// 获取综合分析报告
const fetchAnalysis = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await getComprehensiveAnalysis({ days: days.value })

    if (response.code === 200) {
      analysisData.value = response.data
      ElMessage.success('分析报告生成成功')
    } else {
      error.value = response.message || '生成失败'
      ElMessage.error(error.value)
    }
  } catch (err) {
    console.error('获取综合分析失败:', err)
    error.value = '获取分析报告失败，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 重新生成报告
const regenerate = async () => {
  regenerating.value = true
  await fetchAnalysis()
  regenerating.value = false
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 与AI咨询师深入交流
const startAIChat = () => {
  router.push('/chat')
}

// 页面加载时获取数据
onMounted(() => {
  fetchAnalysis()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.comprehensive-analysis {
  min-height: 100vh;
  background: $bg-page;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: $bg-white;
  border-radius: $border-radius-xl;
  box-shadow: $box-shadow-card;
}

.page-header h2 {
  margin: 0;
  color: $text-primary;
  font-size: 24px;
}

/* 主卡片 */
.main-card {
  border-radius: $border-radius-xl;
  box-shadow: $box-shadow-card;

  :deep(.el-card__body) {
    padding: 32px;
  }
}

.analysis-content {
  padding: 0;
}

/* 各个区块 */
.user-info-section,
.analysis-period-section,
.test-summary-section,
.ai-report-section {
  margin-bottom: 30px;
}

.user-info-section h3,
.analysis-period-section h3,
.test-summary-section h3,
.ai-report-section h3 {
  margin-bottom: 15px;
  color: $text-primary;
  font-size: 18px;
}

/* 分析周期 */
.period-info p {
  margin: 5px 0;
  color: $text-regular;
}

/* 测试列表 */
.test-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.test-item {
  border: 1px solid $border-lighter;
  border-radius: $border-radius-lg;
  transition: all 0.3s;
}

.test-item:hover {
  transform: translateY(-2px);
  box-shadow: $box-shadow-dark;
}

.test-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.test-title {
  font-weight: bold;
  color: $text-primary;
  font-size: 16px;
}

.test-item-body {
  padding: 10px 0;
}

.test-score {
  margin-bottom: 8px;
  font-size: 14px;
}

.score-label {
  color: $text-secondary;
}

.score-value {
  color: $primary-color;
  font-weight: bold;
  font-size: 18px;
}

.test-result {
  color: $text-regular;
  margin-bottom: 8px;
  font-size: 14px;
}

.test-date {
  color: $text-secondary;
  font-size: 12px;
}

/* AI报告 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.ai-report-card {
  border: 1px solid $border-lighter;
  border-radius: $border-radius-lg;

  :deep(.el-card__body) {
    padding: 24px;
  }
}

.markdown-content {
  line-height: 1.8;
  color: $text-primary;
  font-size: 15px;
}

.markdown-content :deep(h3) {
  color: $primary-color;
  margin: 20px 0 10px;
  font-size: 18px;
  border-bottom: 2px solid $border-lighter;
  padding-bottom: 8px;
}

.markdown-content :deep(h4) {
  color: $text-regular;
  margin: 15px 0 8px;
  font-size: 16px;
}

.markdown-content :deep(p) {
  margin: 10px 0;
  text-indent: 2em;
}

.markdown-content :deep(strong) {
  color: $primary-dark;
  font-weight: bold;
}

.markdown-content :deep(ul) {
  margin: 10px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 5px 0;
  list-style-type: disc;
}

.report-footer {
  margin-top: 20px;
}

.report-footer .el-alert {
  margin-bottom: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

/* 生成时间 */
.generated-time {
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  border-top: 1px solid $border-lighter;
}

/* 浮动按钮 */
.floating-actions {
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 1000;
}

.floating-actions .el-button {
  box-shadow: 0 4px 12px rgba($primary-color, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 10px;
  }

  .test-list {
    grid-template-columns: 1fr;
  }

  .floating-actions {
    bottom: 20px;
    right: 20px;
  }
}
</style>
