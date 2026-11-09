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
    // 后端对普通用户返回 redirect='/'。当登录页本身就挂在根路径时，
    // push('/') 会被引擎判定为重复导航、不触发守卫，页面停在原处，
    // 看起来像「登录没反应」。这里按角色给出明确的落地页。
    const role = res.userInfo?.role
    const fallback = role === 'admin'
      ? '/admin'
      : role === 'counselor'
        ? '/counselor/dashboard'
        : '/workspace/home'
    router.push(res.redirect && res.redirect !== '/' ? res.redirect : fallback)
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
