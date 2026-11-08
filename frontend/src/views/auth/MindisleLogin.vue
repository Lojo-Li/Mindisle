<template>
  <LandingPage :login-handler="handleLogin" :navigate="handleNavigate" />
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import LandingPage from '@/views/mindisle/LandingPage.vue'

const router = useRouter()
const userStore = useUserStore()

async function handleLogin({ account, password }) {
  try {
    const res = await userStore.login({ email: account, password })
    ElMessage.success('登录成功！')
    router.push(res.redirect || '/')
  } catch {
    // 错误提示已由 axios 响应拦截器统一处理
  }
}

function handleNavigate(act) {
  const map = {
    register: '/register',
    forgot: '/forgot-password',
    help: '/knowledge'
  }
  if (map[act]) {
    router.push(map[act])
    return true
  }
  return false
}
</script>
