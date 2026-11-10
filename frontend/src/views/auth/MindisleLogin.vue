<template>
  <LandingPage :login-handler="handleLogin" :navigate="handleNavigate" />
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { adminLogin } from '@/api/admin'
import { logout as logoutApi } from '@/api/auth'
import LandingPage from '@/views/mindisle/LandingPage.vue'

const router = useRouter()
const userStore = useUserStore()

// 登录入口与角色的对应关系：用户入口放行普通用户(学生)与咨询师，管理员入口仅放行管理员
const ROLE_LABELS = { user: '用户', counselor: '咨询师', admin: '管理员' }
const TARGET_PORTAL = { user: '用户登录', counselor: '用户登录', admin: '管理员' }

// 角色只认后端返回的登录结果；userInfo 缺字段时用落地页兜底
function detectRole(res) {
  const role = res?.userInfo?.role
  if (role === 'admin' || role === 'counselor' || role === 'user') return role
  if (res?.redirect === '/admin') return 'admin'
  if (res?.redirect === '/counselor/dashboard') return 'counselor'
  return 'user'
}

function mismatchMessage(role) {
  const label = ROLE_LABELS[role] || '其他'
  const target = TARGET_PORTAL[role] || '用户登录'
  return `该账号为${label}账号，请使用「${target}」入口登录`
}

// 入口不匹配时：后端已签发 token，先让其失效再清空前端登录态，避免残留有效凭证
async function clearMismatchSession() {
  try {
    await logoutApi()
  } catch {
    // 提示是主要目标，拉黑失败不阻塞后续清理
  } finally {
    userStore.setToken('')
    userStore.setUserInfo(null)
  }
}

/**
 * 管理员入口登录失败时，/admin/login 只返回 401、不带角色。
 * 用原生 fetch 静默探测一次 /auth/login（绕过 axios 的全局错误弹窗），
 * 以便给出「该账号为 xxx 账号」的精确提示；探测签发的 token 会暂存，
 * 随后由 clearMismatchSession 拉黑，避免残留有效凭证。
 */
async function probeRole(account, password) {
  try {
    const resp = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: account, password })
    })
    if (!resp.ok) return null
    const body = await resp.json()
    const data = body?.data || body
    const role = data?.userInfo?.role
    if (role !== 'user' && role !== 'counselor' && role !== 'admin') return null
    if (data?.token) sessionStorage.setItem('token', data.token)
    return role
  } catch {
    return null
  }
}

/**
 * 登录入口
 * portal: 'user'（用户/咨询师共用）| 'admin'（管理员）
 * 管理员走独立的 /admin/login；用户/咨询师走 /auth/login，
 * 并依据后端返回的真实角色校验入口，用错入口时给出明确提示。
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
      // 账号属于用户/咨询师：给出精确提示，不跳转、不保留登录态
      const role = await probeRole(account, password)
      if (role === 'user' || role === 'counselor') {
        await clearMismatchSession()
        ElMessage({ type: 'warning', message: mismatchMessage(role), duration: 4500, showClose: true })
        return
      }
      // 探测也失败 = 账号或密码本身有误，沿用原有错误处理
      const detail = e?.response?.data?.detail || e?.message
      if (detail && !String(detail).includes('401')) ElMessage.error(detail)
      else if (!e?.response) ElMessage.error('登录失败，请稍后重试')
    }
    return
  }

  try {
    const res = await userStore.login({ email: account, password })
    const role = detectRole(res)
    // 用户入口填了管理员账号：不跳转、不保留登录态，并说明应使用的入口
    if (role === 'admin') {
      await clearMismatchSession()
      ElMessage({ type: 'warning', message: mismatchMessage(role), duration: 4500, showClose: true })
      return
    }
    ElMessage.success('登录成功！')
    // 后端对普通用户返回 redirect='/'。当登录页本身就挂在根路径时，
    // push('/') 会被引擎判定为重复导航、不触发守卫，页面停在原处，
    // 看起来像「登录没反应」。这里按角色给出明确的落地页。
    const fallback = role === 'counselor' ? '/counselor/dashboard' : '/workspace/home'
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
