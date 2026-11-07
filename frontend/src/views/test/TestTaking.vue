<template>
  <div class="test-taking">
    <div class="container">
      <!-- 顶部栏 -->
      <div class="taking-header">
        <el-button :icon="ArrowLeft" @click="handleExit">退出</el-button>
        <div class="test-info">
          <h2>{{ testInfo.title }}</h2>
          <div class="timer">
            <el-icon><Clock /></el-icon>
            <span>{{ formatElapsedTime }}</span>
          </div>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-bar">
        <el-progress
          :percentage="progressPercentage"
          :format="() => `${currentIndex + 1} / ${questions.length}`"
        />
      </div>

      <!-- 答题区域 -->
      <el-card v-loading="loading" class="question-card">
        <!-- 加载状态 -->
        <el-skeleton v-if="loading && questions.length === 0" :rows="5" animated />

        <!-- 答题内容 -->
        <div v-else-if="questions.length > 0" class="question-content">
          <!-- 题目 -->
          <div class="question-header">
            <div class="question-number">问题 {{ currentIndex + 1 }}/{{ questions.length }}</div>
            <div class="question-text">
              {{ currentQuestion.question_text }}
            </div>
          </div>

          <!-- 选项 -->
          <div class="options-list">
            <div
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              class="option-item"
              :class="{ selected: currentAnswer === index }"
              @click="selectOption(index)"
            >
              <div class="option-radio">
                <el-radio
                  :model-value="currentAnswer"
                  :label="index"
                  @click.prevent
                >
                </el-radio>
              </div>
              <div class="option-text">{{ option.label || option }}</div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              :disabled="currentIndex === 0"
              @click="previousQuestion"
            >
              上一题
            </el-button>

            <el-button
              @click="saveProgress"
              :loading="saving"
            >
              保存进度
            </el-button>

            <el-button
              v-if="currentIndex < questions.length - 1"
              type="primary"
              @click="nextQuestion"
            >
              下一题
            </el-button>

            <el-button
              v-else
              type="primary"
              :loading="submitting"
              @click="submitAnswers"
            >
              提交答卷
            </el-button>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-else description="加载失败" />
      </el-card>

      <!-- 答题卡 -->
      <el-card class="answer-card">
        <template #header>
          <span>答题卡</span>
        </template>

        <div class="answer-grid">
          <div
            v-for="(question, index) in questions"
            :key="index"
            class="answer-item"
            :class="{
              current: index === currentIndex,
              answered: answers[index] !== null,
              skipped: answers[index] === null && index < currentIndex
            }"
            @click="jumpToQuestion(index)"
          >
            {{ index + 1 }}
          </div>
        </div>

        <div class="answer-legend">
          <div class="legend-item">
            <span class="dot answered"></span>
            <span>已答</span>
          </div>
          <div class="legend-item">
            <span class="dot current"></span>
            <span>当前</span>
          </div>
          <div class="legend-item">
            <span class="dot skipped"></span>
            <span>未答</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 退出确认对话框 -->
    <el-dialog
      v-model="exitDialogVisible"
      title="确认退出"
      width="400px"
    >
      <p>退出后将自动保存当前作答进度，下次可继续作答。</p>
      <p class="tip">已提交的测试记录可在"我的测试"中查看。</p>
      <template #footer>
        <el-button @click="exitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExit">
          确认退出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Clock } from '@element-plus/icons-vue'
import { getTestDetail, startTest, saveProgress as saveProgressApi, getProgress, submitTest } from '@/api/test'

const router = useRouter()
const route = useRoute()

// 测试ID
const testId = route.params.id

// 加载状态
const loading = ref(true)
const saving = ref(false)
const submitting = ref(false)

// 退出对话框
const exitDialogVisible = ref(false)

// 测试信息
const testInfo = ref({
  id: '',
  title: '',
  description: '',
  questionCount: 0,
  duration: 0
})

// 题目列表
const questions = ref([])

// 答案列表
const answers = ref([])

// 当前题目索引
const currentIndex = ref(0)

// 当前题目
const currentQuestion = computed(() => {
  return questions.value[currentIndex.value] || {}
})

// 当前答案
const currentAnswer = computed({
  get: () => answers.value[currentIndex.value],
  set: (value) => {
    answers.value[currentIndex.value] = value
  }
})

// 进度百分比
const progressPercentage = computed(() => {
  const answeredCount = answers.value.filter(a => a !== null).length
  return Math.round((answeredCount / questions.value.length) * 100)
})

// 计时器
const elapsedTime = ref(0)
let timerInterval = null

// 格式化经过的时间
const formatElapsedTime = computed(() => {
  const minutes = Math.floor(elapsedTime.value / 60)
  const seconds = elapsedTime.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

// 加载测试详情
const loadTestDetail = async () => {
  try {
    loading.value = true
    const res = await getTestDetail(testId)
    testInfo.value = res.data
  } catch (error) {
    console.error('加载测试失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 开始测试（获取题目）
const startTesting = async () => {
  try {
    loading.value = true
    const res = await startTest(testId)
    questions.value = res.data.questions || []

    // 初始化答案数组
    answers.value = new Array(questions.value.length).fill(null)

    // 尝试获取已保存的进度（断点续答）
    try {
      const progressRes = await getProgress(testId)
      if (progressRes.data) {
        const savedAnswers = progressRes.data.answers || {}
        Object.keys(savedAnswers).forEach((key) => {
          const idx = parseInt(key, 10)
          if (idx >= 0 && idx < answers.value.length) {
            answers.value[idx] = savedAnswers[key]
          }
        })
        // 跳转到已答的最后一道题
        if (progressRes.data.current_question) {
          currentIndex.value = progressRes.data.current_question
        }
      }
    } catch (e) {
      // 没有进度记录，从头开始
      console.log('无进度记录，从头开始')
    }

    // 开始计时
    startTimer()
  } catch (error) {
    console.error('加载题目失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 开始计时
const startTimer = () => {
  timerInterval = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

// 停止计时
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 选择选项
const selectOption = (index) => {
  answers.value[currentIndex.value] = index
}

// 上一题
const previousQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

// 下一题
const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

// 跳转到指定题目
const jumpToQuestion = (index) => {
  currentIndex.value = index
}

// 将答案数组转换为对象格式
const answersToObject = (answersArray) => {
  const obj = {}
  answersArray.forEach((answer, index) => {
    if (answer !== null) {
      obj[index] = answer
    }
  })
  return obj
}

// 保存进度
const saveProgress = async () => {
  try {
    saving.value = true
    await saveProgressApi(testId, {
      answers: answersToObject(answers.value)
    })
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 提交答卷
const submitAnswers = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要提交答卷吗？提交后无法修改。',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true
    stopTimer()

    const res = await submitTest(testId, {
      answers: answersToObject(answers.value)
    })

    ElMessage.success('提交成功')

    // 跳转到结果页（后端返回的是 id，不是 resultId）
    router.push(`/test/${res.data.id}/result`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 退出测试
const handleExit = () => {
  exitDialogVisible.value = true
}

// 确认退出（保存当前进度，退出测试）
const confirmExit = async () => {
  stopTimer()
  exitDialogVisible.value = false

  // 检查是否有已答题目
  const hasAnswers = answers.value.some(a => a !== null)
  if (hasAnswers) {
    try {
      saving.value = true
      await saveProgressApi(testId, {
        answers: answersToObject(answers.value)
      })
      ElMessage.success('进度已保存')
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }

  // 退出后返回测试列表
  router.push('/test')
}

// 键盘快捷键
const handleKeydown = (e) => {
  // 方向键左右切换题目
  if (e.key === 'ArrowLeft') {
    previousQuestion()
  } else if (e.key === 'ArrowRight') {
    nextQuestion()
  }
  // 数字键选择选项
  else if (e.key >= '1' && e.key <= '4') {
    const index = parseInt(e.key) - 1
    if (index < currentQuestion.options?.length) {
      selectOption(index)
    }
  }
}

// 组件挂载
onMounted(async () => {
  await loadTestDetail()
  await startTesting()

  // 绑定键盘事件
  window.addEventListener('keydown', handleKeydown)
})

// 组件卸载
onBeforeUnmount(() => {
  stopTimer()
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.test-taking {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 36px $spacing-lg;
}

.taking-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;

  .test-info {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      color: $text-primary;
      font-weight: 700;
    }

    .timer {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: $font-size-large;
      font-weight: 700;
      color: $primary-color;
      background: rgba(232,132,90,0.1);
      padding: 6px 16px;
      border-radius: 999px;
    }
  }
}

.progress-bar {
  margin-bottom: 24px;

  :deep(.el-progress-bar__outer) {
    background: $border-lighter;
    border-radius: 999px;
  }

  :deep(.el-progress-bar__inner) {
    background: $primary-gradient;
    border-radius: 999px;
  }
}

.question-card {
  margin-bottom: 24px;
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__body) {
    padding: 32px;
  }
}

.question-content {
  .question-header {
    margin-bottom: 28px;

    .question-number {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 10px;
      font-weight: 500;
    }

    .question-text {
      font-size: $font-size-extra-large;
      font-weight: 600;
      line-height: 1.65;
      color: $text-primary;
    }
  }

  .options-list {
    margin-bottom: 28px;
  }

  .option-item {
    display: flex;
    align-items: center;
    padding: 14px 18px;
    margin-bottom: 12px;
    border: 2px solid $border-lighter;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: $bg-page;

    &:hover {
      border-color: rgba(232,132,90,0.4);
      background: rgba(232,132,90,0.04);
    }

    &.selected {
      border-color: $primary-color;
      background: rgba(232,132,90,0.08);
    }

    .option-radio {
      flex-shrink: 0;
      margin-right: 14px;

      :deep(.el-radio__label) {
        display: none;
      }
    }

    .option-text {
      flex: 1;
      font-size: $font-size-base;
      color: $text-primary;
      line-height: 1.5;
    }
  }

  .action-buttons {
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }
}

.answer-card {
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;

  :deep(.el-card__body) {
    padding: 20px 24px;
  }

  .answer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
    gap: 8px;
    margin-bottom: 14px;
  }

  .answer-item {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid $border-lighter;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    color: $text-secondary;
    cursor: pointer;
    transition: all 0.15s ease;

    &.answered {
      background: rgba(232,132,90,0.1);
      border-color: $primary-color;
      color: $primary-color;
    }

    &.current {
      background: $primary-gradient;
      border-color: transparent;
      color: #fff;
      box-shadow: 0 4px 12px rgba(200,110,60,0.3);
    }

    &:hover:not(.current) {
      border-color: rgba(232,132,90,0.5);
      background: rgba(232,132,90,0.06);
    }
  }
}

.answer-legend {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 0 0;
  border-top: 1px solid $border-lighter;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: $text-secondary;

    .dot {
      width: 14px;
      height: 14px;
      border-radius: 4px;
      flex-shrink: 0;
      transition: all 0.15s ease;

      &.answered {
        background: rgba(232,132,90,0.12);
        border: 1.5px solid $primary-color;
      }

      &.current {
        background: $primary-gradient;
        border: 1.5px solid transparent;
        box-shadow: 0 2px 6px rgba(200,110,60,0.35);
      }

      &.skipped {
        background: transparent;
        border: 1.5px solid $border-lighter;
      }
    }
  }
}

.tip {
  color: $warning-color;
  font-size: $font-size-small;
  margin-top: $spacing-md;
}

@media (max-width: $breakpoint-md) {
  .action-buttons {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }

  .answer-grid {
    grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)) !important;

    .answer-item {
      width: 40px !important;
      height: 40px !important;
      font-size: $font-size-small;
    }
  }
}
</style>
