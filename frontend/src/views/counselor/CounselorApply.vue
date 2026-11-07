<template>
  <div class="counselor-apply-page">

    <div class="container">
      <el-card class="apply-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="24" color="#67C23A"><Briefcase /></el-icon>
            <span>加入我们 - 成为心理咨询师</span>
          </div>
        </template>

        <div class="apply-content">
          <!-- 平台介绍 -->
          <div class="section intro-section">
            <h2>关于 SoulStation</h2>
            <div class="intro-text">
              <p>
                SoulStation 是一个专业的心理健康服务平台，致力于为用户提供优质的心理咨询服务。
                我们拥有一支经验丰富、专业资质过硬的咨询师团队，为用户提供在线咨询、心理测评、
                知识科普等全方位的心理健康服务。
              </p>
              <p>
                加入我们，您将获得：
              </p>
              <ul class="benefits-list">
                <li>✓ 灵活的工作时间和地点</li>
                <li>✓ 专业的技术平台支持</li>
                <li>✓ 持续的专业培训和成长机会</li>
                <li>✓ 丰厚的报酬和激励机制</li>
                <li>✓ 与优秀同行交流学习的机会</li>
              </ul>
            </div>
          </div>

          <el-divider />

          <!-- 申请表单 -->
          <div class="section form-section">
            <h2>咨询师申请表</h2>
            <p class="form-tip">请填写以下信息，我们将在3个工作日内完成审核</p>

            <el-form
              ref="formRef"
              :model="formData"
              :rules="formRules"
              label-width="140px"
              class="apply-form"
            >
              <!-- 基本信息 -->
              <div class="form-group">
                <h3>基本信息</h3>

                <el-form-item label="姓名" prop="name">
                  <el-input
                    v-model="formData.name"
                    placeholder="请输入您的真实姓名"
                    maxlength="50"
                  />
                </el-form-item>

                <el-form-item label="性别" prop="gender">
                  <el-radio-group v-model="formData.gender">
                    <el-radio label="male">男</el-radio>
                    <el-radio label="female">女</el-radio>
                    <el-radio label="secret">保密</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="职称" prop="title">
                  <el-select
                    v-model="formData.title"
                    placeholder="请选择职称"
                    style="width: 100%"
                  >
                    <el-option label="心理咨询师（初级）" value="心理咨询师（初级）" />
                    <el-option label="心理咨询师（中级）" value="心理咨询师（中级）" />
                    <el-option label="心理咨询师（高级）" value="心理咨询师（高级）" />
                    <el-option label="注册心理师" value="注册心理师" />
                    <el-option label="心理治疗师" value="心理治疗师" />
                    <el-option label="精神科医师" value="精神科医师" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>
              </div>

              <!-- 专业信息 -->
              <div class="form-group">
                <h3>专业信息</h3>

                <el-form-item label="从业年限" prop="experience_years">
                  <el-input-number
                    v-model="formData.experience_years"
                    :min="0"
                    :max="50"
                    :step="1"
                    style="width: 100%"
                  />
                  <span class="unit-text">年</span>
                </el-form-item>

                <el-form-item label="学历背景" prop="education">
                  <el-input
                    v-model="formData.education"
                    placeholder="例如：北京大学 心理学硕士"
                    maxlength="200"
                  />
                </el-form-item>

                <el-form-item label="资质证书" prop="certificate_images" required>
                  <el-upload
                    v-model:file-list="certificateList"
                    :auto-upload="false"
                    list-type="picture-card"
                    :on-preview="handlePicturePreview"
                    :on-remove="handleRemove"
                    :on-change="handleCertificateChange"
                    :before-upload="beforeCertificateUpload"
                    :limit="5"
                    accept="image/*"
                  >
                    <el-icon><Plus /></el-icon>
                  </el-upload>
                  <div class="form-tip-text">
                    请上传您的专业资质证书图片（最多5张，每张不超过5MB）
                  </div>

                  <!-- 图片预览对话框 -->
                  <el-dialog v-model="previewDialogVisible" title="证书预览" width="600px">
                    <img :src="previewImageUrl" style="width: 100%" />
                  </el-dialog>
                </el-form-item>

                <el-form-item label="擅长领域" prop="specialties" required>
                  <el-checkbox-group v-model="formData.specialties">
                    <el-checkbox label="情绪管理">情绪管理</el-checkbox>
                    <el-checkbox label="焦虑抑郁">焦虑抑郁</el-checkbox>
                    <el-checkbox label="婚恋家庭">婚恋家庭</el-checkbox>
                    <el-checkbox label="亲子教育">亲子教育</el-checkbox>
                    <el-checkbox label="职业规划">职业规划</el-checkbox>
                    <el-checkbox label="个人成长">个人成长</el-checkbox>
                    <el-checkbox label="人际关系">人际关系</el-checkbox>
                    <el-checkbox label="睡眠障碍">睡眠障碍</el-checkbox>
                    <el-checkbox label="创伤疗愈">创伤疗愈</el-checkbox>
                    <el-checkbox label="青少年心理">青少年心理</el-checkbox>
                    <el-checkbox label="性心理">性心理</el-checkbox>
                    <el-checkbox label="其他">其他</el-checkbox>
                  </el-checkbox-group>
                  <div class="form-tip-text">请至少选择一个擅长领域</div>
                </el-form-item>

                <el-form-item label="咨询方式" prop="consultation_types" required>
                  <el-checkbox-group v-model="formData.consultation_types">
                    <el-checkbox label="video">视频咨询</el-checkbox>
                    <el-checkbox label="voice">语音咨询</el-checkbox>
                    <el-checkbox label="offline">线下咨询</el-checkbox>
                  </el-checkbox-group>
                  <div class="form-tip-text">请至少选择一种咨询方式</div>
                </el-form-item>

                <el-form-item
                  v-if="formData.consultation_types.includes('video')"
                  label="视频咨询价格"
                  prop="price_video"
                >
                  <el-input-number
                    v-model="formData.price_video"
                    :min="0"
                    :max="2000"
                    :step="50"
                    style="width: 200px"
                  />
                  <span class="unit-text">元/小时</span>
                </el-form-item>

                <el-form-item
                  v-if="formData.consultation_types.includes('voice')"
                  label="语音咨询价格"
                  prop="price_voice"
                >
                  <el-input-number
                    v-model="formData.price_voice"
                    :min="0"
                    :max="2000"
                    :step="50"
                    style="width: 200px"
                  />
                  <span class="unit-text">元/小时</span>
                </el-form-item>

                <el-form-item
                  v-if="formData.consultation_types.includes('offline')"
                  label="线下咨询价格"
                  prop="price_offline"
                >
                  <el-input-number
                    v-model="formData.price_offline"
                    :min="0"
                    :max="2000"
                    :step="50"
                    style="width: 200px"
                  />
                  <span class="unit-text">元/小时</span>
                </el-form-item>
              </div>

              <!-- 详细信息 -->
              <div class="form-group">
                <h3>详细信息</h3>

                <el-form-item label="个人简介" prop="bio" required>
                  <el-input
                    v-model="formData.bio"
                    type="textarea"
                    :rows="6"
                    placeholder="请详细介绍您的专业背景、咨询风格、工作理念等（至少50字）"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="咨询流派/方法" prop="approach">
                  <el-input
                    v-model="formData.approach"
                    type="textarea"
                    :rows="4"
                    placeholder="请描述您主要使用的咨询流派和方法，如：认知行为疗法、精神分析、人本主义等"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="成就荣誉" prop="achievements">
                  <el-input
                    v-model="formData.achievements"
                    type="textarea"
                    :rows="4"
                    placeholder="请列举您获得的奖项、发表的论文、出版的著作等成就"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>
              </div>

              <!-- 专业问卷 -->
              <div class="form-group">
                <h3>专业问卷</h3>
                <p class="form-tip">请认真回答以下问题，帮助我们更好地了解您</p>

                <el-form-item label="从业初衷" prop="question1" required>
                  <el-input
                    v-model="formData.question1"
                    type="textarea"
                    :rows="4"
                    placeholder="您为什么选择成为一名心理咨询师？"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="咨询理念" prop="question2" required>
                  <el-input
                    v-model="formData.question2"
                    type="textarea"
                    :rows="4"
                    placeholder="您认为心理咨询的核心是什么？您的工作理念是什么？"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="典型案例" prop="question3" required>
                  <el-input
                    v-model="formData.question3"
                    type="textarea"
                    :rows="4"
                    placeholder="请分享一个您经手的典型案例（请注意保护来访者隐私，不使用真实信息），包括问题、方法、效果"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="自我评价" prop="question4" required>
                  <el-input
                    v-model="formData.question4"
                    type="textarea"
                    :rows="4"
                    placeholder="请描述您的专业优势、工作风格，以及您认为需要改进的地方"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="时间安排" prop="question5" required>
                  <el-input
                    v-model="formData.question5"
                    type="textarea"
                    :rows="4"
                    placeholder="您通常在什么时间段可以接受咨询预约？每周可提供多少小时的咨询时间？"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>
              </div>

              <!-- 提交按钮 -->
              <el-form-item>
                <div class="submit-buttons">
                  <el-button size="large" @click="goBack">
                    返回
                  </el-button>
                  <el-button
                    type="primary"
                    size="large"
                    :loading="submitting"
                    @click="submitApplication"
                  >
                    提交申请
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Briefcase } from '@element-plus/icons-vue'
import { submitApplication as submitCounselorApplication } from '@/api/counselor'

const router = useRouter()

// 表单引用
const formRef = ref(null)

// 提交状态
const submitting = ref(false)

// 表单数据
const formData = reactive({
  // 基本信息
  name: '',
  gender: 'secret',
  title: '',

  // 专业信息
  specialties: [],
  consultation_types: [],
  experience_years: 0,
  education: '',
  certificate_images: [], // 改为证书图片数组

  // 定价信息
  price_video: null,
  price_voice: null,
  price_offline: null,

  // 详细信息
  bio: '',
  approach: '',
  achievements: '',

  // 专业问卷
  question1: '', // 从业初衷
  question2: '', // 咨询理念
  question3: '', // 典型案例
  question4: '', // 自我评价
  question5: '', // 时间安排
})

// 证书上传相关
const certificateList = ref([])
const previewDialogVisible = ref(false)
const previewImageUrl = ref('')

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  experience_years: [
    { required: true, message: '请输入从业年限', trigger: 'blur' },
    { type: 'number', min: 0, max: 50, message: '从业年限在0-50年', trigger: 'blur' }
  ],
  education: [
    { required: true, message: '请输入学历背景', trigger: 'blur' },
    { max: 200, message: '最多200个字符', trigger: 'blur' }
  ],
  certificate_images: [
    {
      type: 'array',
      required: true,
      message: '请至少上传一张资质证书',
      trigger: 'change'
    }
  ],
  specialties: [
    {
      type: 'array',
      required: true,
      message: '请至少选择一个擅长领域',
      trigger: 'change'
    }
  ],
  consultation_types: [
    {
      type: 'array',
      required: true,
      message: '请至少选择一种咨询方式',
      trigger: 'change'
    }
  ],
  bio: [
    { required: true, message: '请输入个人简介', trigger: 'blur' },
    { min: 50, max: 2000, message: '个人简介在50-2000个字符', trigger: 'blur' }
  ],
  question1: [
    { required: true, message: '请回答从业初衷', trigger: 'blur' },
    { min: 20, max: 1000, message: '回答在20-1000个字符', trigger: 'blur' }
  ],
  question2: [
    { required: true, message: '请回答咨询理念', trigger: 'blur' },
    { min: 20, max: 1000, message: '回答在20-1000个字符', trigger: 'blur' }
  ],
  question3: [
    { required: true, message: '请回答典型案例', trigger: 'blur' },
    { min: 50, max: 1000, message: '回答在50-1000个字符', trigger: 'blur' }
  ],
  question4: [
    { required: true, message: '请回答自我评价', trigger: 'blur' },
    { min: 20, max: 1000, message: '回答在20-1000个字符', trigger: 'blur' }
  ],
  question5: [
    { required: true, message: '请回答时间安排', trigger: 'blur' },
    { min: 20, max: 1000, message: '回答在20-1000个字符', trigger: 'blur' }
  ]
}

// 提交申请
const submitApplication = async () => {
  if (!formRef.value) return

  try {
    // 验证表单
    await formRef.value.validate()

    // 将证书图片转换为 base64
    const certificatePromises = formData.certificate_images.map(file => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    })

    const certificateBase64Array = await Promise.all(certificatePromises)

    // 构建提交数据
    const submitData = {
      name: formData.name,
      gender: formData.gender,
      title: formData.title,
      specialties: formData.specialties,
      consultationTypes: formData.consultation_types,
      experienceYears: formData.experience_years,
      education: formData.education,
      qualifications: certificateBase64Array.join(','), // 将多张图片用逗号分隔
      priceVideo: formData.price_video,
      priceVoice: formData.price_voice,
      priceOffline: formData.price_offline,
      bio: `${formData.bio}\n\n【从业初衷】\n${formData.question1}\n\n【咨询理念】\n${formData.question2}\n\n【典型案例】\n${formData.question3}\n\n【自我评价】\n${formData.question4}\n\n【时间安排】\n${formData.question5}`,
      approach: formData.approach,
      achievements: formData.achievements
    }

    submitting.value = true

    // 调用API
    await submitCounselorApplication(submitData)

    ElMessage.success('申请提交成功！我们将在3个工作日内完成审核')

    // 跳转回个人中心
    setTimeout(() => {
      router.push('/profile')
    }, 2000)
  } catch (error) {
    if (error !== false) { // 排除表单验证失败
      console.error('提交申请失败:', error)
      ElMessage.error(error.response?.data?.message || '提交失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 图片预览
const handlePicturePreview = (uploadFile) => {
  previewImageUrl.value = uploadFile.url
  previewDialogVisible.value = true
}

// 删除图片
const handleRemove = (uploadFile, uploadFiles) => {
  formData.certificate_images = uploadFiles.map(file => file.raw)
}

// 图片改变时更新表单数据
const handleCertificateChange = (uploadFile, uploadFiles) => {
  formData.certificate_images = uploadFiles.map(file => file.raw)
}

// 上传前验证
const beforeCertificateUpload = (rawFile) => {
  const isImage = rawFile.type.startsWith('image/')
  const isLt5M = rawFile.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }
  return true
}

// 返回
const goBack = () => {
  router.back()
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-apply-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.apply-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    font-size: $font-size-extra-large;
    font-weight: 600;
    color: $text-primary;
  }
}

.apply-content {
  .section {
    margin-bottom: $spacing-xl;

    h2 {
      font-size: $font-size-large;
      color: $text-primary;
      margin-bottom: $spacing-lg;
      padding-bottom: $spacing-sm;
      border-bottom: 2px solid $primary-color;
    }

    h3 {
      font-size: $font-size-medium;
      color: $text-primary;
      margin-bottom: $spacing-lg;
      padding-left: $spacing-md;
      border-left: 4px solid $primary-color;
    }
  }
}

.intro-section {
  .intro-text {
    p {
      color: $text-regular;
      line-height: 1.8;
      margin-bottom: $spacing-md;
    }

    .benefits-list {
      list-style: none;
      padding: 0;

      li {
        padding: $spacing-sm 0;
        color: $text-regular;
        font-size: $font-size-medium;

        &:before {
          content: '✓';
          color: $success-color;
          font-weight: bold;
          margin-right: $spacing-sm;
        }
      }
    }
  }
}

.form-section {
  .form-tip {
    color: $text-secondary;
    margin-bottom: $spacing-lg;
  }

  .apply-form {
    .form-group {
      margin-bottom: $spacing-xl;
      padding: $spacing-xl;
      background: #f9fafb;
      border-radius: $border-radius-md;

      .unit-text {
        margin-left: $spacing-sm;
        color: $text-secondary;
      }

      .form-tip-text {
        margin-top: $spacing-sm;
        font-size: $font-size-small;
        color: $text-secondary;
      }

      // 上传组件样式
      :deep(.el-upload-list--picture-card) {
        .el-upload-list__item {
          width: 100px;
          height: 100px;
        }
      }

      :deep(.el-upload--picture-card) {
        width: 100px;
        height: 100px;
      }
    }
  }

  .submit-buttons {
    display: flex;
    justify-content: center;
    gap: $spacing-lg;
    margin-top: $spacing-xl;

    .el-button {
      min-width: 150px;
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .container {
    padding: $spacing-md;
  }

  .apply-form {
    .form-group {
      padding: $spacing-md;
    }
  }
}
</style>
