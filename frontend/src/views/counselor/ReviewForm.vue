<template>
  <div class="review-form">
    <div class="container">
      <el-button :icon="ArrowLeft" @click="goBack" class="back-btn">返回</el-button>

      <el-card v-loading="loading" class="form-card">
        <div class="review-header">
          <el-avatar :size="80" :src="appointment?.counselorAvatar" />
          <div class="header-info">
            <h2>评价咨询</h2>
            <p>{{ appointment?.counselorName }}</p>
            <p class="appointment-time">{{ appointment?.date }} {{ appointment?.timeSlot }}</p>
          </div>
        </div>

        <el-divider />

        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="总体评分" prop="rating">
            <el-rate v-model="form.rating" size="large" show-text :texts="['非常不满意', '不满意', '一般', '满意', '非常满意']" />
          </el-form-item>

          <el-form-item label="满意度" prop="tags">
            <el-checkbox-group v-model="form.tags">
              <el-checkbox label="专业度高">专业度高</el-checkbox>
              <el-checkbox label="倾听耐心">倾听耐心</el-checkbox>
              <el-checkbox label="环境舒适">环境舒适</el-checkbox>
              <el-checkbox label="效果明显">效果明显</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="您的评价" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="6"
              placeholder="请分享您的咨询体验（选填，最多500字）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="form.isAnonymous">匿名评价</el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="submitReview">提交评价</el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { submitReview as submitReviewApi } from '@/api/counselor'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const submitting = ref(false)
const formRef = ref(null)
const appointment = ref({})

const form = reactive({
  rating: 5,
  tags: [],
  content: '',
  isAnonymous: false
})

const rules = {
  rating: [{ required: true, message: '请选择评分', trigger: 'change' }]
}

const loadAppointment = async () => {
  // 这里应该根据appointmentId加载订单信息
  appointment.value = {
    counselorName: '张老师',
    counselorAvatar: '',
    date: '2026-02-26',
    timeSlot: '14:00-15:00'
  }
  loading.value = false
}

const submitReview = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    submitting.value = true
    await submitReviewApi(route.params.id, form)
    ElMessage.success('评价成功')
    goBack()
  } catch (error) {
    console.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.push('/counselor/orders')

onMounted(() => loadAppointment())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.review-form { min-height: 100vh; background: $bg-color; }
.container { max-width: 700px; margin: 0 auto; padding: $spacing-lg; }
.back-btn { margin-bottom: $spacing-lg; }
.review-header { display: flex; align-items: center; gap: $spacing-lg; margin-bottom: $spacing-xl; }
.header-info h2 { margin: 0 0 $spacing-xs; }
.appointment-time { color: $text-secondary; }
.form-card { margin-top: $spacing-lg; }
:deep(.el-form-item__content) { max-width: 500px; }
</style>
