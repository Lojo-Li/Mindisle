<template>
  <div class="login-page">
    <!-- 左侧装饰面板 -->
    <div class="login-panel-left">
      <div class="panel-brand">
        <div class="brand-icon">🌸</div>
        <h1 class="brand-name">心灵驿站</h1>
        <p class="brand-tagline">SoulStation</p>
      </div>
      <div class="panel-quote">
        <blockquote>
          <p>"每一次倾诉，都是与自己的和解；每一次聆听，都是对内心的温柔相待。"</p>
        </blockquote>
      </div>
      <div class="panel-features">
        <div class="feature-item" v-for="feat in panelFeatures" :key="feat.icon">
          <span class="feat-icon">{{ feat.icon }}</span>
          <span class="feat-text">{{ feat.text }}</span>
        </div>
      </div>
      <!-- 装饰圆圈 -->
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
      <div class="deco-circle deco-3"></div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-panel-right">
      <div class="login-form-wrap">
        <div class="form-header">
          <h2>欢迎回来 👋</h2>
          <p>登录您的账户，继续您的心灵之旅</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="email">
            <el-input
              v-model="loginForm.email"
              placeholder="请输入邮箱"
              prefix-icon="Message"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" @click="goToForgotPassword">忘记密码？</el-link>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <el-link type="primary" @click="goToRegister">立即注册</el-link>
        </div>
      </div>

      <footer class="page-bottom">
        © 2026 心灵驿站 · 守护您的心理健康
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const panelFeatures = [
  { icon: '🤖', text: 'AI 智能心理问答' },
  { icon: '📝', text: '专业心理测试量表' },
  { icon: '👨‍⚕️', text: '预约专业咨询师' },
  { icon: '📚', text: '心理健康知识库' },
]

const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

const validateEmail = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!value.includes('@')) {
    callback(new Error('请输入正确的邮箱格式'))
  } else {
    callback()
  }
}

const loginRules = {
  email: [
    { required: true, validator: validateEmail, trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
    loading.value = true
    const res = await userStore.login({
      email: loginForm.email,
      password: loginForm.password
    })
    ElMessage.success('登录成功！')
    setTimeout(() => {
      const redirectPath = res.redirect || '/'
      router.push(redirectPath)
    }, 500)
  } catch (error) {
    // 错误提示已在请求拦截器中处理，此处无需重复显示
  } finally {
    loading.value = false
  }
}

const goToRegister = () => router.push('/register')
const goToForgotPassword = () => router.push('/forgot-password')
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.login-page {
  display: flex;
  min-height: 100vh;
}

// ---- 左侧装饰面板 ----
.login-panel-left {
  flex: 0 0 45%;
  background: linear-gradient(160deg, #fde8d8 0%, #fbd4c0 40%, #e8c4d8 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 48px;
  position: relative;
  overflow: hidden;

  .panel-brand {
    text-align: center;
    margin-bottom: 48px;
    position: relative;
    z-index: 1;

    .brand-icon {
      font-size: 64px;
      margin-bottom: 16px;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12));
    }

    .brand-name {
      font-size: 36px;
      font-weight: 700;
      color: #3d2b1f;
      letter-spacing: 4px;
      margin-bottom: 4px;
    }

    .brand-tagline {
      font-size: 14px;
      color: #9e8070;
      letter-spacing: 6px;
      text-transform: uppercase;
    }
  }

  .panel-quote {
    position: relative;
    z-index: 1;
    background: rgba(255, 255, 255, 0.45);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 40px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    max-width: 360px;

    blockquote p {
      font-size: 15px;
      line-height: 1.8;
      color: #5a3c2b;
      font-style: italic;
      text-align: center;
    }
  }

  .panel-features {
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 280px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.4);
      border-radius: 40px;
      padding: 10px 20px;
      backdrop-filter: blur(4px);
      border: 1px solid rgba(255,255,255,0.5);

      .feat-icon { font-size: 20px; }
      .feat-text { font-size: 14px; color: #4a3020; font-weight: 500; }
    }
  }

  // 装饰圆圈
  .deco-circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.18);
    pointer-events: none;
  }

  .deco-1 {
    width: 280px; height: 280px;
    top: -80px; right: -60px;
  }

  .deco-2 {
    width: 180px; height: 180px;
    bottom: -40px; left: -50px;
    background: rgba(155, 139, 180, 0.15);
  }

  .deco-3 {
    width: 100px; height: 100px;
    bottom: 120px; right: 30px;
    background: rgba(232, 132, 90, 0.12);
  }
}

// ---- 右侧表单面板 ----
.login-panel-right {
  flex: 1;
  background: #fffcf8;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  position: relative;
}

.login-form-wrap {
  width: 100%;
  max-width: 400px;

  .form-header {
    margin-bottom: 36px;

    h2 {
      font-size: 28px;
      font-weight: 700;
      color: #3d2b1f;
      margin-bottom: 8px;
    }

    p {
      font-size: 15px;
      color: #9e8070;
    }
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-input__wrapper) {
    border-radius: 14px !important;
    padding: 4px 16px;
    box-shadow: 0 0 0 1px #e8d5c5 inset !important;

    &.is-focus {
      box-shadow: 0 0 0 2px rgba(232, 132, 90, 0.3) inset !important;
    }
  }

  :deep(.el-input__inner) {
    font-size: 15px;
    height: 42px;
  }

  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    margin-top: -4px;
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
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(232, 132, 90, 0.45) !important;
    }

    &:active {
      transform: translateY(0);
    }
  }
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #9e8070;

  .el-link {
    margin-left: 4px;
    font-weight: 600;
    font-size: 14px;
  }
}

.page-bottom {
  position: absolute;
  bottom: 24px;
  font-size: 13px;
  color: #c4b0a4;
}

// ---- 响应式 ----
@media (max-width: 768px) {
  .login-panel-left {
    display: none;
  }

  .login-panel-right {
    padding: 32px 24px;
  }
}
</style>
