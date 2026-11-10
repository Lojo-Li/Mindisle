<template>
  <LandingPage :login-handler="handleLogin" :navigate="handleNavigate" />
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { adminLogin } from '@/api/admin'
import LandingPage from '@/views/mindisle/LandingPage.vue'

const router = useRouter()
const userStore = useUserStore()

/**
 * 登录入口
 * portal: 'user'（用户/咨询师共用）| 'admin'（管理员）
 * 之前忽略了 portal，管理员身份也会打到 /auth/login，必然 401，表现就是「点了没反应」。
 */
async function handleLogin({ account, password, portal }) {
  if (!account || !password) {
    ElMessage.warning(portal === 'admin' ? '请输入管理员账号和密码' : '请输入账号和密码')
    return
  }

  if (portal === 'admin') {
    try {
      const res = await adminLogin({ username: account, password })
      const data = (res && res.data) || {}
      const admin = data.admin || {}
      userStore.setToken(data.access_token)
      userStore.setUserInfo({
        id: admin.id,
        username: admin.username,
        nickname: admin.real_name || admin.username || '管理员',
        email: admin.email,
        role: 'admin'
      })
      ElMessage.success('登录成功！')
      router.push('/admin/dashboard')
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.message
      if (detail && !String(detail).includes('401')) ElMessage.error(detail)
      else if (!e?.response) ElMessage.error('登录失败，请稍后重试')
    }
    return
  }

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
