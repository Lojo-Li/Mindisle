<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button link @click="goToLogin">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </el-button>
      </div>

      <!-- 标题 -->
      <div class="header">
        <el-icon :size="48" color="#e8845a">
          <Lock />
        </el-icon>
        <h1 class="title">重置密码</h1>
        <p class="subtitle">找回您的账户密码</p>
      </div>

      <!-- 步骤指示器 -->
      <div class="steps">
        <el-steps :active="currentStep" align-center finish-status="success">
          <el-step title="验证邮箱" />
          <el-step title="设置新密码" />
          <el-step title="完成" />
        </el-steps>
      </div>

      <!-- 步骤1: 验证邮箱 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-form
          ref="emailFormRef"
          :model="emailForm"
          :rules="emailRules"
          class="form"
        >
          <!-- 邮箱输入 -->
          <el-form-item prop="email">
            <el-input
              v-model="emailForm.email"
              placeholder="请输入注册邮箱"
              prefix-icon="Message"
              size="large"
              clearable
            />
          </el-form-item>

          <!-- 验证码输入 -->
          <el-form-item prop="code">
            <div class="code-input-wrapper">
              <el-input
                v-model="emailForm.code"
                placeholder="请输入验证码"
                prefix-icon="Key"
                size="large"
                maxlength="6"
              />
              <el-button
                type="primary"
                size="large"
                :disabled="countdown > 0"
                :loading="sendingCode"
                @click="sendVerificationCode"
              >
                {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
              </el-button>
            </div>
          </el-form-item>

          <!-- 下一步按钮 -->
          <el-button
            type="primary"
            size="large"
            class="action-button"
            :loading="verifying"
            @click="verifyEmail"
          >
            下一步
          </el-button>
        </el-form>
      </div>

      <!-- 步骤2: 设置新密码 -->
      <div v-show="currentStep === 1" class="step-content">
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          class="form"
        >
          <!-- 新密码输入 -->
          <el-form-item prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              placeholder="请输入新密码（6-20位）"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <!-- 确认新密码 -->
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <!-- 操作按钮 -->
          <div class="button-group">
            <el-button
              size="large"
              class="action-button"
              @click="currentStep = 0"
            >
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              class="action-button"
              :loading="resetting"
              @click="resetPassword"
            >
              确认重置
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 步骤3: 完成 -->
      <div v-show="currentStep === 2" class="step-content success-content">
        <el-result
          icon="success"
          title="密码重置成功！"
          sub-title="您现在可以使用新密码登录了"
        >
          <template #extra>
            <el-button
              type="primary"
              size="large"
              class="action-button"
              @click="goToLogin"
            >
              立即登录
            </el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Lock } from '@element-plus/icons-vue'
import { sendEmailCode, verifyEmailForReset, resetPassword as resetPasswordApi } from '@/api/auth'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 表单引用
const emailFormRef = ref(null)
const passwordFormRef = ref(null)

// 加载状态
const sendingCode = ref(false)
const verifying = ref(false)
const resetting = ref(false)

// 倒计时
const countdown = ref(0)
let countdownTimer = null

// 步骤1: 邮箱表单
const emailForm = reactive({
  email: '',
  code: ''
})

// 步骤2: 密码表单
const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 自定义校验规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 步骤1校验规则
const emailRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      type: 'email',
      message: '请输入正确的邮箱格式',
      trigger: ['blur', 'change']
    }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码应为6位数字', trigger: 'blur' }
  ]
}

// 步骤2校验规则
const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 发送验证码
const sendVerificationCode = async () => {
  // 校验邮箱
  if (!emailForm.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }

  const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailReg.test(emailForm.email)) {
    ElMessage.error('请输入正确的邮箱格式')
    return
  }

  try {
    sendingCode.value = true
    await sendEmailCode(emailForm.email, 'reset')
    ElMessage.success('验证码已发送至您的邮箱')

    // 开始倒计时
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
  } finally {
    sendingCode.value = false
  }
}

// 验证邮箱
const verifyEmail = async () => {
  if (!emailFormRef.value) return

  try {
    // 表单校验
    await emailFormRef.value.validate()

    // 验证邮箱
    verifying.value = true
    await verifyEmailForReset({
      email: emailForm.email,
      code: emailForm.code
    })

    ElMessage.success('邮箱验证成功')
    currentStep.value = 1
  } catch (error) {
    console.error('邮箱验证失败:', error)
  } finally {
    verifying.value = false
  }
}

// 重置密码
const resetPassword = async () => {
  if (!passwordFormRef.value) return

  try {
    // 表单校验
    await passwordFormRef.value.validate()

    // 重置密码
    resetting.value = true
    await resetPasswordApi({
      email: emailForm.email,
      newPassword: passwordForm.newPassword
    })

    ElMessage.success('密码重置成功')
    currentStep.value = 2
  } catch (error) {
    console.error('密码重置失败:', error)
  } finally {
    resetting.value = false
  }
}

// 返回登录页
const goToLogin = () => {
  router.push('/login')
}

// 组件销毁时清除定时器
onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #fde8d8 0%, #fbd4c0 45%, #e8c4d8 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -80px; left: -60px;
    width: 250px; height: 250px;
    background: rgba(155,139,180,0.15);
    border-radius: 50%;
  }
}

.forgot-password-box {
  width: 100%;
  max-width: 480px;
  background: $bg-white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(61,43,31,0.15);
  padding: 40px;
  position: relative;
  z-index: 1;
}

.back-button {
  margin-bottom: 24px;
}

.header {
  text-align: center;
  margin-bottom: 32px;

  .title {
    font-size: 26px;
    font-weight: 700;
    color: $text-primary;
    margin: 16px 0 8px;
  }

  .subtitle {
    font-size: 14px;
    color: $text-secondary;
  }
}

.steps {
  margin-bottom: 32px;

  :deep(.el-step__head.is-finish .el-step__icon) {
    border-color: $primary-color;
    color: $primary-color;
  }

  :deep(.el-step__head.is-process .el-step__icon) {
    background: $primary-color;
    border-color: $primary-color;
  }

  :deep(.el-step__title.is-finish),
  :deep(.el-step__title.is-process) {
    color: $primary-color;
  }
}

.step-content {
  &.success-content {
    text-align: center;
  }
}

.form {
  .code-input-wrapper {
    display: flex;
    gap: 12px;

    .el-input {
      flex: 1;
    }

    .el-button {
      white-space: nowrap;
    }
  }

  .el-form-item {
    margin-bottom: 24px;
  }

  .action-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 500;
  }

  .button-group {
    display: flex;
    gap: 12px;

    .action-button {
      flex: 1;
    }
  }
}

@media (max-width: 768px) {
  .forgot-password-box {
    padding: 32px 24px;
  }

  .code-input-wrapper {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }

  .button-group {
    flex-direction: column !important;
  }
}
</style>

