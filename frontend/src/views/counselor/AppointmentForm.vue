<template>
  <div class="appointment-form">
    <div class="container">
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>预约咨询</h2>
      </div>

      <el-card v-loading="loading">
        <el-steps :active="currentStep" finish-status="success" class="steps">
          <el-step title="选择时间" />
          <el-step title="填写信息" />
        </el-steps>

        <!-- 步骤1: 选择时间 -->
        <div v-show="currentStep === 0" class="step-content">
          <h3>1. 选择咨询方式</h3>
          <el-radio-group v-model="formData.type" class="type-group">
            <el-radio label="video" border>视频咨询</el-radio>
            <el-radio label="voice" border>语音咨询</el-radio>
            <el-radio label="offline" border>线下咨询</el-radio>
          </el-radio-group>

          <h3>2. 选择日期和时段</h3>
          <el-calendar v-model="selectedDate">
            <template #date-cell="{ data }">
              <div class="calendar-day" :class="{ available: isAvailableDate(data.date) }">
                {{ data.date.getDate() }}
              </div>
            </template>
          </el-calendar>

          <div class="time-slots">
            <h4>可选时段</h4>
            <div v-if="availableSlots.length === 0" class="no-slots">暂无可预约时段</div>
            <el-radio-group v-model="formData.timeSlot" class="slots-group">
              <el-radio
                v-for="slot in availableSlots"
                :key="slot.time"
                :label="slot.time"
                border
              >
                {{ slot.time }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 步骤2: 填写信息 -->
        <div v-show="currentStep === 1" class="step-content">
          <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
            <el-form-item label="您的姓名" prop="userName">
              <el-input v-model="formData.userName" placeholder="请输入姓名" />
            </el-form-item>

            <el-form-item label="联系方式" prop="contact">
              <el-input v-model="formData.contact" placeholder="请输入手机号" />
            </el-form-item>

            <el-form-item label="咨询问题" prop="description">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="4"
                placeholder="请简要描述您希望咨询的问题"
              />
            </el-form-item>

            <el-form-item label="费用">
              <div class="price-display">
                <span class="price">¥{{ price }}</span>
                <span class="unit">/小时</span>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button v-if="currentStep === 1" @click="currentStep--">上一步</el-button>
          <el-button
            v-if="currentStep === 0"
            type="primary"
            :disabled="!formData.timeSlot"
            @click="nextStep"
          >
            下一步
          </el-button>
          <el-button
            v-if="currentStep === 1"
            type="primary"
            :loading="submitting"
            @click="submitAppointment"
          >
            确认预约
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getCounselorDetail, getAvailableSlots, createAppointment } from '@/api/counselor'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const currentStep = ref(0)
const submitting = ref(false)

const counselorId = route.query.counselorId
const counselor = ref({})
const price = ref(0)

const selectedDate = ref(new Date())
const availableSlots = ref([])

const formData = reactive({
  counselorId,
  type: 'video',
  date: '',
  timeSlot: '',
  userName: '',
  contact: '',
  description: ''
})

const formRef = ref(null)

const rules = {
  userName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  contact: [
    { required: true, message: '请输入联系方式', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }]
}

const loadCounselor = async () => {
  try {
    const res = await getCounselorDetail(counselorId)
    counselor.value = res.data
    updatePrice()
  } catch (error) {
    ElMessage.error('加载咨询师信息失败')
  }
}

const updatePrice = () => {
  if (formData.type === 'video') {
    price.value = counselor.value.price_video || 0
  } else if (formData.type === 'voice') {
    price.value = counselor.value.price_voice || 0
  } else if (formData.type === 'offline') {
    price.value = counselor.value.price_offline || 0
  } else {
    price.value = 0
  }
}

const isAvailableDate = (date) => {
  const day = date.getDay()
  return day >= 1 && day <= 5 // 周一到周五
}

const loadSlots = async () => {
  if (!selectedDate.value) return
  try {
    const dateStr = selectedDate.value.toISOString().split('T')[0]
    const res = await getAvailableSlots(counselorId, dateStr)
    const slots = res.data || []
    availableSlots.value = slots.filter(item => item.available)
  } catch (error) {
    console.error('加载时段失败')
  }
}

const nextStep = () => {
  if (!formData.timeSlot) {
    ElMessage.warning('请选择时段')
    return
  }
  currentStep.value = 1
}

const submitAppointment = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    submitting.value = true

    const date = selectedDate.value.toISOString().split('T')[0]
    const startTime = formData.timeSlot.split('-')[0]
    const payload = {
      counselor_id: Number(counselorId),
      consultation_type: formData.type,
      appointment_date: `${date}T${startTime}:00`,
      user_name: formData.userName,
      user_contact: formData.contact,
      problem_description: formData.description
    }

    await createAppointment(payload)

    ElMessage.success('预约成功')
    router.push('/counselor/orders')
  } catch (error) {
    console.error('预约失败:', error)
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  if (!counselorId) {
    ElMessage.error('缺少咨询师ID')
    router.push('/counselor')
    return
  }

  Promise.all([loadCounselor(), loadSlots()]).finally(() => {
    loading.value = false
  })
})

watch(selectedDate, () => {
  formData.timeSlot = ''
  loadSlots()
})

watch(() => formData.type, () => {
  updatePrice()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.appointment-form { min-height: 100vh; background: $bg-color; }
.container { max-width: 800px; margin: 0 auto; padding: $spacing-lg; }
.page-header { display: flex; align-items: center; gap: $spacing-md; margin-bottom: $spacing-lg; h2 { flex: 1; margin: 0; } }
.steps { margin: $spacing-xl 0; }
.step-content { margin-top: $spacing-xl; }
.step-content h3 { margin: $spacing-lg 0 $spacing-md; }
.type-group { display: flex; gap: $spacing-lg; margin-bottom: $spacing-xl; }
.calendar-day { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.calendar-day.available { background: rgba(64, 158, 255, 0.1); color: $primary-color; }
.time-slots { margin-top: $spacing-lg; }
.time-slots h4 { margin-bottom: $spacing-md; }
.slots-group { display: flex; flex-wrap: wrap; gap: $spacing-md; }
.no-slots { color: $text-secondary; padding: $spacing-md; }
.price-display { font-size: 24px; }
.price-display .price { color: $primary-color; font-weight: 600; }
.action-buttons { display: flex; justify-content: center; gap: $spacing-md; margin-top: $spacing-xl; }
</style>
