<template>
  <div class="cd-page">
    <div class="cd-container">

      <el-button :icon="ArrowLeft" text class="back-btn" @click="goBack">返回</el-button>

      <div v-if="loading" class="cd-skeleton">
        <el-skeleton :rows="8" animated />
      </div>

      <div v-else-if="error" class="cd-error">
        <el-empty description="咨询师信息加载失败" />
        <el-button @click="loadDetail">重试</el-button>
      </div>

      <template v-else>
        <!-- 头部卡片 -->
        <div class="cd-hero">
          <el-avatar :size="96" :src="counselor.avatar" class="cd-avatar">
            <el-icon :size="40"><User /></el-icon>
          </el-avatar>
          <div class="cd-hero-info">
            <div class="cd-name-row">
              <h1>{{ counselor.name }}</h1>
              <el-tag v-if="counselor.is_verified" type="success" size="small">已认证</el-tag>
            </div>
            <p class="cd-title">{{ counselor.title || '心理咨询师' }}</p>
            <div class="cd-meta">
              <span v-if="counselor.experience_years">从业 {{ counselor.experience_years }} 年</span>
              <el-divider direction="vertical" v-if="counselor.experience_years && counselor.education" />
              <span v-if="counselor.education">{{ counselor.education }}</span>
            </div>
            <div class="cd-rating">
              <el-rate :model-value="counselor.rating" disabled show-score score-template="{value}" />
              <span class="cd-review-count">{{ counselor.review_count }} 条评价</span>
              <span class="cd-consult-count">· 咨询 {{ counselor.consultation_count }} 次</span>
            </div>
          </div>
          <el-button type="primary" size="large" round class="cd-appt-btn" @click="goToAppointment">
            立即预约
          </el-button>
          <el-button size="large" round class="cd-chat-btn" @click="goToInquiry">
            <el-icon><ChatDotSquare /></el-icon> 联系咨询师
          </el-button>
        </div>

        <!-- 主体内容 -->
        <div class="cd-body">
          <!-- 左列 -->
          <div class="cd-main">
            <el-card class="cd-card" v-if="counselor.bio">
              <template #header><span class="cd-card-title">个人简介</span></template>
              <p class="cd-text">{{ counselor.bio }}</p>
            </el-card>

            <el-card class="cd-card" v-if="counselor.approach">
              <template #header><span class="cd-card-title">咨询方法</span></template>
              <p class="cd-text">{{ counselor.approach }}</p>
            </el-card>

            <el-card class="cd-card" v-if="counselor.achievements">
              <template #header><span class="cd-card-title">成就荣誉</span></template>
              <p class="cd-text">{{ counselor.achievements }}</p>
            </el-card>
          </div>

          <!-- 右列 -->
          <div class="cd-side">
            <el-card class="cd-card">
              <template #header><span class="cd-card-title">擅长领域</span></template>
              <div class="cd-tags">
                <el-tag
                  v-for="s in specialtyList"
                  :key="s"
                  round
                  class="cd-specialty-tag"
                >{{ specialtyLabel(s) }}</el-tag>
              </div>
            </el-card>

            <el-card class="cd-card">
              <template #header><span class="cd-card-title">咨询方式 &amp; 收费</span></template>
              <div class="cd-price-list">
                <div v-if="counselor.price_video && typeList.includes('video')" class="cd-price-row">
                  <div class="cd-price-type">
                    <el-icon><VideoCamera /></el-icon> 视频咨询
                  </div>
                  <span class="cd-price">¥{{ counselor.price_video }}<em>/小时</em></span>
                </div>
                <div v-if="counselor.price_voice && typeList.includes('voice')" class="cd-price-row">
                  <div class="cd-price-type">
                    <el-icon><Microphone /></el-icon> 语音咨询
                  </div>
                  <span class="cd-price">¥{{ counselor.price_voice }}<em>/小时</em></span>
                </div>
                <div v-if="counselor.price_offline && typeList.includes('offline')" class="cd-price-row">
                  <div class="cd-price-type">
                    <el-icon><Location /></el-icon> 线下咨询
                  </div>
                  <span class="cd-price">¥{{ counselor.price_offline }}<em>/小时</em></span>
                </div>
              </div>
            </el-card>

            <el-button type="primary" round size="large" style="width:100%;margin-bottom:12px" @click="goToAppointment">
              立即预约
            </el-button>
            <el-button round size="large" style="width:100%" @click="goToInquiry">
              <el-icon><ChatDotSquare /></el-icon> 联系咨询师
            </el-button>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User, VideoCamera, Microphone, Location, ChatDotSquare } from '@element-plus/icons-vue'
import { getCounselorDetail } from '@/api/counselor'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref(false)
const counselor = ref({})

const specialtyMap = { anxiety: '焦虑', depression: '抑郁', emotion: '情感', career: '职场', family: '家庭' }
const specialtyLabel = (s) => specialtyMap[s] || s

// 后端返回逗号分隔字符串，转为数组
const specialtyList = computed(() => {
  const v = counselor.value.specialties
  if (!v) return []
  return Array.isArray(v) ? v : v.split(',').map(s => s.trim()).filter(Boolean)
})
const typeList = computed(() => {
  const v = counselor.value.consultation_types
  if (!v) return []
  return Array.isArray(v) ? v : v.split(',').map(s => s.trim()).filter(Boolean)
})

const loadDetail = async () => {
  loading.value = true
  error.value = false
  try {
    const res = await getCounselorDetail(route.params.id)
    counselor.value = res.data
  } catch (e) {
    error.value = true
    ElMessage.error('加载咨询师信息失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.push('/counselor')
const goToAppointment = () => {
  router.push({ path: '/counselor/appointment', query: { counselorId: route.params.id } })
}
const goToInquiry = () => {
  router.push(`/counselor/${route.params.id}/inquiry`)
}

onMounted(loadDetail)
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.cd-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.cd-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

.back-btn { margin-bottom: 20px; }

.cd-skeleton, .cd-error {
  background: #fff;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
}

// 头部英雄区
.cd-hero {
  background: #fff;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08);
  padding: 32px;
  display: flex;
  align-items: flex-start;
  gap: 28px;
  margin-bottom: 24px;
}

.cd-avatar {
  flex-shrink: 0;
  background: $border-lighter;
  color: $text-secondary;
}

.cd-hero-info { flex: 1; }

.cd-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  h1 { margin: 0 0 4px; font-size: 24px; font-weight: 700; color: $text-primary; }
}

.cd-title { margin: 0 0 8px; color: $text-secondary; font-size: 14px; }

.cd-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: $text-secondary;
  margin-bottom: 10px;
}

.cd-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: $text-secondary;
}

.cd-appt-btn { flex-shrink: 0; align-self: center; }
.cd-chat-btn { flex-shrink: 0; align-self: center; }

// 主体布局
.cd-body {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  align-items: start;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.cd-card {
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;
  margin-bottom: 16px;

  :deep(.el-card__header) {
    border-bottom: 1px solid $border-lighter;
    padding: 14px 20px;
  }
}

.cd-card-title { font-weight: 600; color: $text-primary; font-size: 15px; }

.cd-text { margin: 0; color: $text-regular; line-height: 1.8; font-size: 14px; }

.cd-tags { display: flex; flex-wrap: wrap; gap: 8px; }

.cd-specialty-tag {
  background: rgba(232,132,90,0.1) !important;
  border-color: rgba(232,132,90,0.3) !important;
  color: $primary-color !important;
}

.cd-price-list { display: flex; flex-direction: column; gap: 14px; }

.cd-price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cd-price-type {
  display: flex;
  align-items: center;
  gap: 6px;
  color: $text-regular;
  font-size: 14px;
}

.cd-price {
  font-size: 18px;
  font-weight: 700;
  color: $primary-color;
  em { font-style: normal; font-size: 12px; font-weight: 400; color: $text-secondary; }
}
</style>
