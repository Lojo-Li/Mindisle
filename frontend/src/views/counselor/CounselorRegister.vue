<template>
  <div class="counselor-register">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>咨询师入驻申请</h2>
          <p class="subtitle">填写以下信息，申请成为心理咨询师</p>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        label-position="top"
      >
        <!-- 基本信息 -->
      <div class="section">
        <h3 class="section-title">基本信息</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input
                v-model="formData.name"
                placeholder="请输入真实姓名"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
                <el-radio label="secret">保密</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="职称" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="如：心理咨询师、心理治疗师等"
            maxlength="100"
          />
        </el-form-item>
      </div>

      <!-- 专业信息 -->
      <div class="section">
        <h3 class="section-title">专业信息</h3>

        <el-form-item label="擅长领域" prop="specialties" required>
          <el-checkbox-group v-model="formData.specialties">
            <el-checkbox label="anxiety">焦虑情绪</el-checkbox>
            <el-checkbox label="depression">抑郁情绪</el-checkbox>
            <el-checkbox label="emotion">情绪管理</el-checkbox>
            <el-checkbox label="career">职业发展</el-checkbox>
            <el-checkbox label="family">家庭关系</el-checkbox>
            <el-checkbox label="marriage">婚姻情感</el-checkbox>
            <el-checkbox label="adolescent">青少年心理</el-checkbox>
            <el-checkbox label="growth">个人成长</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="咨询方式" prop="consultation_types" required>
          <el-checkbox-group v-model="formData.consultation_types">
            <el-checkbox label="video">视频咨询</el-checkbox>
            <el-checkbox label="voice">语音咨询</el-checkbox>
            <el-checkbox label="offline">线下咨询</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="从业年限" prop="experience_years">
              <el-input-number
                v-model="formData.experience_years"
                :min="0"
                :max="50"
                controls-position="right"
                class="full-width"
              />
              <span class="unit">年</span>
            </el-form-item>
          </el-col>

          <el-col :span="16">
            <el-form-item label="学历背景" prop="education">
              <el-select v-model="formData.education" placeholder="请选择学历" class="full-width">
                <el-option label="专科" value="专科" />
                <el-option label="本科" value="本科" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="资质证书" prop="qualifications">
          <el-input
            v-model="formData.qualifications"
            type="textarea"
            :rows="3"
            placeholder="请输入您获得的心理咨询相关资质证书，如：国家二级心理咨询师、心理治疗师等"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </div>

      <!-- 定价信息 -->
      <div class="section">
        <h3 class="section-title">定价信息（元/小时）</h3>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="视频咨询价格">
              <el-input-number
                v-model="formData.price_video"
                :min="0"
                :max="5000"
                :precision="0"
                controls-position="right"
                class="full-width"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="语音咨询价格">
              <el-input-number
                v-model="formData.price_voice"
                :min="0"
                :max="5000"
                :precision="0"
                controls-position="right"
                class="full-width"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="线下咨询价格">
              <el-input-number
                v-model="formData.price_offline"
                :min="0"
                :max="5000"
                :precision="0"
                controls-position="right"
                class="full-width"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 详细信息 -->
      <div class="section">
        <h3 class="section-title">详细介绍</h3>

        <el-form-item label="个人简介" prop="bio" required>
          <el-input
            v-model="formData.bio"
            type="textarea"
            :rows="6"
            placeholder="请详细介绍您的专业背景、从业经验、咨询理念等（至少50字）"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="咨询流派/方法">
          <el-input
            v-model="formData.approach"
            type="textarea"
            :rows="4"
            placeholder="如：认知行为疗法(CBT)、精神分析、人本主义等"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="成就荣誉">
          <el-input
            v-model="formData.achievements"
            type="textarea"
            :rows="4"
            placeholder="请列举您获得的荣誉、发表的论文、参与的项目等"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </div>

      <!-- 提交按钮 -->
      <el-form-item>
        <div class="button-group">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            {{ submitting ? '提交中...' : '提交申请' }}
          </el-button>
        </div>
      </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { submitApplication, getApplicationStatus } from '@/api/counselor'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const existingStatus = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  gender: 'secret',
  title: '',
  specialties: [],
  consultation_types: [],
  experience_years: 0,
  education: '',
  qualifications: '',
  price_video: null,
  price_voice: null,
  price_offline: null,
  bio: '',
  approach: '',
  achievements: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  specialties: [
    { type: 'array', required: true, message: '请至少选择一个擅长领域', trigger: 'change' }
  ],
  consultation_types: [
    { type: 'array', required: true, message: '请至少选择一种咨询方式', trigger: 'change' }
  ],
  experience_years: [
    { required: true, message: '请输入从业年限', trigger: 'blur' }
  ],
  education: [
    { required: true, message: '请选择学历', trigger: 'change' }
  ],
  qualifications: [
    { required: true, message: '请输入资质证书', trigger: 'blur' },
    { min: 5, max: 500, message: '资质证书长度在5-500个字符', trigger: 'blur' }
  ],
  bio: [
    { required: true, message: '请输入个人简介', trigger: 'blur' },
    { min: 50, max: 2000, message: '个人简介长度在50-2000个字符', trigger: 'blur' }
  ]
}

// 获取申请状态
const checkApplicationStatus = async () => {
  try {
    const response = await getApplicationStatus()
    existingStatus.value = response.data

    // 如果已经有申请且不是被拒绝状态，提示用户
    if (response.data.has_applied && response.data.application_status === 'pending') {
      ElMessageBox.alert(
        '您的申请正在审核中，请耐心等待',
        '申请状态',
        {
          confirmButtonText: '我知道了',
          type: 'info'
        }
      ).then(() => {
        router.push('/counselor/list')
      })
    } else if (response.data.has_applied && response.data.application_status === 'approved') {
      ElMessageBox.alert(
        '您已经是认证咨询师，无需重复申请',
        '申请状态',
        {
          confirmButtonText: '前往咨询师列表',
          type: 'success'
        }
      ).then(() => {
        router.push('/counselor/list')
      })
    }
  } catch (error) {
    console.error('获取申请状态失败:', error)
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    // 验证表单
    await formRef.value.validate()

    // 验证至少填写一种价格
    if (!formData.price_video && !formData.price_voice && !formData.price_offline) {
      ElMessage.warning('请至少填写一种咨询方式的价格')
      return
    }

    // 如果之前被拒绝过，确认是否重新提交
    if (existingStatus.value?.has_applied && existingStatus.value?.application_status === 'rejected') {
      await ElMessageBox.confirm(
        '您之前的申请已被拒绝，确定要重新提交申请吗？',
        '重新申请',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    }

    submitting.value = true

    // 提交申请
    await submitApplication(formData)

    ElMessage.success('申请提交成功，请等待管理员审核')

    // 延迟跳转
    setTimeout(() => {
      router.push('/counselor/list')
    }, 1500)

  } catch (error) {
    if (error !== 'cancel') { // 用户取消操作不报错
      console.error('提交申请失败:', error)
      ElMessage.error(error.response?.data?.detail || '提交申请失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

onMounted(() => {
  checkApplicationStatus()
})
</script>

<style scoped lang="scss">
.counselor-register {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.register-card {
  .card-header {
    text-align: center;

    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
    }

    .subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }
}

.section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #dcdfe6;

  &:last-of-type {
    border-bottom: none;
  }

  .section-title {
    margin: 0 0 20px 0;
    font-size: 18px;
    font-weight: 500;
    color: #409eff;
    position: relative;
    padding-left: 12px;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 18px;
      background: #409eff;
      border-radius: 2px;
    }
  }
}

.el-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.unit {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;

  .el-button {
    min-width: 120px;
  }
}

.full-width {
  width: 100%;
}
</style>
