<template>
  <div class="admin-layout">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#fff"><ChatDotRound /></el-icon>
        <span class="logo-text">心理咨询平台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#2d1f17"
        text-color="#e8d5c5"
        active-text-color="#f4c49e"
        :collapse="isCollapse"
      >
        <el-menu-item index="/admin/dashboard" @click="navigateTo('/admin/dashboard')">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-menu-item index="/admin/users" @click="navigateTo('/admin/users')">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/counselor-review" @click="navigateTo('/admin/counselor-review')">
          <el-icon><UserFilled /></el-icon>
          <template #title>咨询师审核</template>
        </el-menu-item>

        <el-menu-item index="/admin/counselors" @click="navigateTo('/admin/counselors')">
          <el-icon><Avatar /></el-icon>
          <template #title>咨询师管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/orders" @click="navigateTo('/admin/orders')">
          <el-icon><List /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/knowledge" @click="navigateTo('/admin/knowledge')">
          <el-icon><Document /></el-icon>
          <template #title>知识管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/tests" @click="navigateTo('/admin/tests')">
          <el-icon><Notebook /></el-icon>
          <template #title>测试管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/dialogues" @click="navigateTo('/admin/dialogues')">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>对话管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/article-editor" @click="navigateTo('/admin/article-editor')">
          <el-icon><Edit /></el-icon>
          <template #title>文章编辑</template>
        </el-menu-item>

        <el-menu-item index="/admin/system" @click="navigateTo('/admin/system')">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <div class="top-navbar">
        <div class="navbar-left">
          <el-icon :size="24" class="collapse-icon" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="navbar-right">
          <span class="welcome-text">欢迎您, {{ userInfo?.nickname || userInfo?.username || '管理员' }}</span>
          <el-dropdown>
            <div class="avatar-container">
              <el-avatar :size="40" :icon="UserFilled" />
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfile">
                  <el-icon><HomeFilled /></el-icon>
                  进入前台
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled, User, UserFilled, Avatar, List, Document, Notebook,
  ChatDotRound, Edit, Setting, Fold, Expand, SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)
const userInfo = ref(null)

const activeMenu = computed(() => {
  return route.path
})

const currentPageTitle = computed(() => {
  const titleMap = {
    '/admin/dashboard': '首页',
    '/admin/users': '用户管理',
    '/admin/counselor-review': '咨询师审核',
    '/admin/counselors': '咨询师管理',
    '/admin/orders': '订单管理',
    '/admin/knowledge': '知识管理',
    '/admin/tests': '测试管理',
    '/admin/dialogues': '对话管理',
    '/admin/article-editor': '文章编辑',
    '/admin/system': '系统设置'
  }
  return titleMap[route.path] || '后台管理'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const navigateTo = (path) => {
  router.push(path)
}

const handleProfile = () => {
  // 跳转到前台首页
  router.push('/')
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 清除所有用户数据（同时清除 sessionStorage 和 localStorage）
    ;['token', 'adminToken', 'userInfo', 'adminInfo', 'userRole'].forEach(key => {
      sessionStorage.removeItem(key)
      localStorage.removeItem(key)
    })

    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  // 优先从 sessionStorage 读取，其次从 localStorage 读取
  const savedUserInfo = sessionStorage.getItem('userInfo') || localStorage.getItem('userInfo')
  if (savedUserInfo) {
    userInfo.value = JSON.parse(savedUserInfo)
  }
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

/* 整体布局 */
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

:deep(.el-container) {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边导航 */
.sidebar {
  width: 220px;
  min-width: 220px;
  background-color: #2d1f17;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar.is-collapsed {
  width: 64px;
  min-width: 64px;
}

.sidebar:has(.el-menu--collapse) {
  width: 64px;
  min-width: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  color: #f4c49e;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
  white-space: nowrap;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-menu {
  flex: 1;
  border: none !important;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #2d1f17 !important;

  &:not(.el-menu--collapse) {
    width: 220px;
  }

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }
}

:deep(.sidebar-menu .el-menu-item) {
  background-color: transparent !important;
  color: rgba(255,255,255,0.75) !important;
  border-radius: 10px;
  margin: 2px 8px;
}

:deep(.sidebar-menu .el-menu-item:hover) {
  background-color: rgba(232,132,90,0.15) !important;
  color: #f4a57a !important;
}

:deep(.sidebar-menu .el-menu-item.is-active) {
  background-color: rgba(232,132,90,0.25) !important;
  color: #f4a57a !important;
}

/* 右侧主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: $bg-page;
}

/* 顶部导航栏 */
.top-navbar {
  height: 60px;
  background-color: $bg-white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(107,82,68,0.08);
  flex-shrink: 0;
  border-bottom: 1px solid $border-lighter;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-icon {
  cursor: pointer;
  transition: color 0.3s;
  color: $text-secondary;
  &:hover { color: $primary-color; }
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 内容区 */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  min-height: 0;

  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: $border-base;
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: $border-lighter;
  }
}

/* 面包屑 */
.breadcrumb { margin-bottom: 20px; }

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .main-content {
    margin-left: 0;
  }

  .content-area {
    padding: 16px;
  }

  .navbar-left {
    gap: 8px;
  }

  .welcome-text {
    display: none;
  }
}

@media (max-width: 480px) {
  .top-navbar {
    padding: 0 16px;
  }

  .content-area {
    padding: 12px;
  }
}
</style>
