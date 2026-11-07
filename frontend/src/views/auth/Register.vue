<template>
  <div class="register-page">
    <!-- 左侧装饰面板 -->
    <div class="register-panel-left">
      <div class="panel-brand">
        <div class="brand-icon">🌸</div>
        <h1 class="brand-name">心灵驿站</h1>
        <p class="brand-tagline">SoulStation</p>
      </div>
      <div class="panel-card">
        <h3>开启您的心灵之旅</h3>
        <p>加入数千位用户，共同探索心理健康的奥秘，让专业陪伴您前行。</p>
      </div>
      <div class="panel-steps">
        <div class="step-item" v-for="(step, i) in steps" :key="i">
          <div class="step-num">{{ i + 1 }}</div>
          <span>{{ step }}</span>
        </div>
      </div>
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
    </div>

    <!-- 右侧注册表单 -->
    <div class="register-panel-right">
      <div class="register-form-wrap">
        <div class="form-header">
          <h2>创建账户 ✨</h2>
          <p>填写以下信息，开始您的心理健康旅程</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              prefix-icon="Message"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="code">
            <div class="code-input-wrapper">
              <el-input
                v-model="registerForm.code"
                placeholder="请输入验证码"
                prefix-icon="Key"
                size="large"
                maxlength="6"
              />
              <el-button
                type="primary"
                size="large"
                class="code-btn"
                :disabled="countdown > 0"
                :loading="sendingCode"
                @click="sendVerificationCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请设置密码（6-20位）"
              prefix-icon="Lock"
              size="large"
              show-password
              @input="checkPasswordStrength"
            />
            <div v-if="registerForm.password" class="password-strength">
              <span class="strength-label">密码强度：</span>
              <div class="strength-bar">
                <div
                  class="strength-bar-fill"
                  :class="passwordStrength.class"
                  :style="{ width: passwordStrength.width }"
                ></div>
              </div>
              <span class="strength-text" :class="passwordStrength.class">
                {{ passwordStrength.text }}
              </span>
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item prop="agreed">
            <el-checkbox v-model="registerForm.agreed">
              我已阅读并同意
              <el-link type="primary">《用户协议》</el-link>
              和
              <el-link type="primary">《隐私政策》</el-link>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleRegister"
            >
              {{ loading ? '注册中...' : '注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>已有账号？</span>
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
        </div>
      </div>

      <footer class="page-bottom">
        © 2026 心灵驿站 · 守护您的心理健康
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { sendEmailCode } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref(null)
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let countdownTimer = null

const steps = ['填写邮箱并获取验证码', '设置安全密码', '完成注册，立即使用']

const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreed: false
})

const passwordStrength = computed(() => {
  const password = registerForm.password
  if (!password) return { width: '0%', text: '', class: '' }
  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 10) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  if (strength <= 2) return { width: '33%', text: '弱', class: 'weak' }
  if (strength <= 3) return { width: '66%', text: '中', class: 'medium' }
  return { width: '100%', text: '强', class: 'strong' }
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreed = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码应为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
  agreed: [{ required: true, validator: validateAgreed, trigger: 'change' }]
}

const sendVerificationCode = async () => {
  if (!registerForm.email) { ElMessage.warning('请先输入邮箱地址'); return }
  const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailReg.test(registerForm.email)) { ElMessage.error('请输入正确的邮箱格式'); return }
  try {
    sendingCode.value = true
    await sendEmailCode(registerForm.email, 'register')
    ElMessage.success('验证码已发送至您的邮箱，请注意查收')
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) { clearInterval(countdownTimer); countdownTimer = null }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
  } finally {
    sendingCode.value = false
  }
}

const checkPasswordStrength = () => {}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  try {
    await registerFormRef.value.validate()
    loading.value = true
    await userStore.register({
      email: registerForm.email,
      code: registerForm.code,
      password: registerForm.password
    })
    ElMessage.success('注册成功！欢迎加入心灵驿站 🌸')
    setTimeout(() => router.push('/'), 500)
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => router.push('/login')

onBeforeUnmount(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.register-page {
  display: flex;
  min-height: 100vh;
}

.register-panel-left {
  flex: 0 0 42%;
  background: linear-gradient(160deg, #e8d5f0 0%, #f4cdd8 50%, #fde8d0 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 44px;
  position: relative;
  overflow: hidden;

  .panel-brand {
    text-align: center;
    margin-bottom: 36px;
    position: relative;
    z-index: 1;

    .brand-icon { font-size: 56px; margin-bottom: 12px; }
    .brand-name { font-size: 32px; font-weight: 700; color: #3d2b1f; letter-spacing: 4px; margin-bottom: 4px; }
    .brand-tagline { font-size: 13px; color: #9e8070; letter-spacing: 6px; text-transform: uppercase; }
  }

  .panel-card {
    background: rgba(255,255,255,0.48);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 32px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.6);
    max-width: 320px;
    position: relative;
    z-index: 1;

    h3 { font-size: 17px; font-weight: 600; color: #3d2b1f; margin-bottom: 10px; }
    p { font-size: 14px; line-height: 1.7; color: #6b5244; }
  }

  .panel-steps {
    display: flex;
    flex-direction: column;
    gap: 14px;
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 280px;

    .step-item {
      display: flex;
      align-items: center;
      gap: 14px;
      background: rgba(255,255,255,0.38);
      border-radius: 40px;
      padding: 10px 18px;
      backdrop-filter: blur(4px);

      .step-num {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #e8845a;
        color: white;
        font-size: 13px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      span { font-size: 13px; color: #4a3020; font-weight: 500; }
    }
  }

  .deco-circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.18);
    pointer-events: none;
  }
  .deco-1 { width: 250px; height: 250px; top: -60px; right: -50px; }
  .deco-2 { width: 160px; height: 160px; bottom: -30px; left: -40px; background: rgba(155,139,180,0.15); }
}

.register-panel-right {
  flex: 1;
  background: #fffcf8;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 40px;
  position: relative;
  overflow-y: auto;
}

.register-form-wrap {
  width: 100%;
  max-width: 420px;

  .form-header {
    margin-bottom: 28px;
    h2 { font-size: 26px; font-weight: 700; color: #3d2b1f; margin-bottom: 6px; }
    p { font-size: 14px; color: #9e8070; }
  }
}

.register-form {
  :deep(.el-form-item) { margin-bottom: 18px; }

  :deep(.el-input__wrapper) {
    border-radius: 14px !important;
    padding: 4px 16px;
    box-shadow: 0 0 0 1px #e8d5c5 inset !important;
    &.is-focus { box-shadow: 0 0 0 2px rgba(232, 132, 90, 0.3) inset !important; }
  }

  :deep(.el-input__inner) { font-size: 14px; height: 40px; }

  .code-input-wrapper {
    display: flex;
    gap: 10px;

    :deep(.el-input) { flex: 1; }

    .code-btn {
      white-space: nowrap;
      border-radius: 14px !important;
      background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%) !important;
      border: none !important;
      font-weight: 600;
      min-width: 110px;
    }
  }

  .password-strength {
    display: flex;
    align-items: center;
    margin-top: 8px;
    font-size: 12px;

    .strength-label { color: #9e8070; margin-right: 8px; white-space: nowrap; }

    .strength-bar {
      flex: 1;
      height: 4px;
      background: #f0e0d0;
      border-radius: 2px;
      overflow: hidden;
      margin-right: 8px;
    }

    .strength-bar-fill {
      height: 100%;
      transition: width 0.3s;
      &.weak { background: #e87a7a; }
      &.medium { background: #e8b55a; }
      &.strong { background: #72b087; }
    }

    .strength-text {
      font-weight: 600;
      &.weak { color: #e87a7a; }
      &.medium { color: #e8b55a; }
      &.strong { color: #72b087; }
    }
  }

  .submit-btn {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 2px;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%) !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(232, 132, 90, 0.38) !important;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(232, 132, 90, 0.45) !important;
    }
  }
}

.form-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #9e8070;
  .el-link { margin-left: 4px; font-weight: 600; font-size: 14px; }
}

.page-bottom {
  position: absolute;
  bottom: 20px;
  font-size: 12px;
  color: #c4b0a4;
}

@media (max-width: 768px) {
  .register-panel-left { display: none; }
  .register-panel-right { padding: 28px 20px; }
}
</style>


