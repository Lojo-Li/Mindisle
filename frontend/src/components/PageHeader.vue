<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <div class="logo" @click="goHome">
          <span class="logo-icon">
            <svg width="23" height="23" viewBox="0 0 24 24" fill="none">
              <path d="M3 17.5c2.2 0 2.6-3.5 4.8-3.5s2.4 2.4 4.4 2.4 2.5-4.2 4.8-4.2c1.4 0 2.4.9 3 1.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
              <circle cx="16.6" cy="7" r="2.1" fill="#F6D08A"/>
            </svg>
          </span>
          <span class="brand-text">
            <b>心屿</b>
            <span>Mindisle</span>
          </span>
        </div>

        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            router
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/chat">智能问答</el-menu-item>
            <el-menu-item index="/test">心理测试</el-menu-item>
            <el-menu-item index="/counselor">找咨询师</el-menu-item>
            <el-menu-item index="/knowledge">心理知识</el-menu-item>
          </el-menu>
        </nav>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索..."
              prefix-icon="Search"
              clearable
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <el-button text class="auth-btn-login" @click="goToLogin">登录</el-button>
            <el-button type="primary" class="auth-btn-register" @click="goToRegister">注册</el-button>
          </template>

          <!-- 已登录状态 -->
          <template v-else>
            <!-- 通知 -->
            <el-popover
              placement="bottom-end"
              :width="360"
              trigger="click"
              @show="loadNotificationsForPopover"
            >
              <template #reference>
                <el-badge :value="notifStore.unreadCount" :hidden="notifStore.unreadCount === 0" class="notification-badge">
                  <el-button circle :icon="Bell" />
                </el-badge>
              </template>
              <div class="notification-popover">
                <div class="popover-header">
                  <span class="popover-title">消息通知</span>
                  <el-button v-if="notifStore.unreadCount > 0" type="primary" link size="small" @click="handleMarkAllRead">全部已读</el-button>
                </div>
                <div class="popover-list">
                  <div
                    v-for="item in popoverNotifications"
                    :key="item.id"
                    class="popover-item"
                    :class="{ unread: !item.is_read }"
                    @click="handleNotificationClick(item)"
                  >
                    <div class="item-dot" v-if="!item.is_read" />
                    <div class="item-content">
                      <div class="item-title">{{ item.title }}</div>
                      <div class="item-text">{{ item.content }}</div>
                      <div class="item-time">{{ formatTime(item.created_at) }}</div>
                    </div>
                  </div>
                  <el-empty v-if="popoverNotifications.length === 0" description="暂无通知" :image-size="60" />
                </div>
                <div class="popover-footer">
                  <el-button type="primary" link @click="goToNotifications">查看全部通知</el-button>
                </div>
              </div>
            </el-popover>

            <!-- 用户下拉菜单 -->
            <el-dropdown @command="handleCommand" :key="userInfo?.role">
              <div class="user-info">
                <el-avatar :size="36" :src="userInfo?.avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="username">{{ userInfo?.nickname || '用户' }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="orders" v-if="!isCounselor">
                    <el-icon><Calendar /></el-icon>
                    我的预约
                  </el-dropdown-item>
                  <el-dropdown-item command="counselor-dashboard" v-if="isCounselor">
                    <el-icon><Calendar /></el-icon>
                    工作台
                  </el-dropdown-item>
                  <el-dropdown-item command="admin" v-if="isAdmin">
                    <el-icon><Setting /></el-icon>
                    后台管理
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Bell,
  User,
  ArrowDown,
  Calendar,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notifStore = useNotificationStore()

// 搜索关键词
const searchKeyword = ref('')

const popoverNotifications = ref([])

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 是否登录
const isLoggedIn = computed(() => userStore.isLoggedIn)

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 是否是咨询师
const isCounselor = computed(() => userStore.isCounselor)

// 是否是管理员
const isAdmin = computed(() => userStore.isAdmin)

// 回到首页
const goHome = () => {
  router.push('/')
}

// 搜索处理
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({
      path: '/search',
      query: { keyword: searchKeyword.value }
    })
  }
}

// —— 通知相关 ——
const loadNotificationsForPopover = async () => {
  await notifStore.fetchList(1, 5)
  popoverNotifications.value = notifStore.notifications
}

const handleNotificationClick = async (item) => {
  if (!item.is_read) await notifStore.markRead(item.id)
  if (item.related_id && (item.type?.startsWith('appointment') || item.type === 'new_message')) {
    const role = sessionStorage.getItem('userRole')
    const prefix = role === 'counselor' ? '/consultation/counselor' : '/consultation/user'
    router.push(`${prefix}/${item.related_id}`)
  } else if (item.type?.startsWith('counselor')) {
    router.push('/counselor/dashboard')
  }
}

const handleMarkAllRead = async () => {
  await notifStore.markAllRead()
  popoverNotifications.value.forEach(n => { n.is_read = true })
}

const goToNotifications = () => {
  router.push('/notifications')
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// 下拉菜单命令处理
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'orders':
      router.push('/counselor/orders')
      break
    case 'counselor-dashboard':
      router.push('/counselor/dashboard')
      break
    case 'admin':
      router.push('/admin/dashboard')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await userStore.logout()
      } catch {
        // 取消退出
      }
      break
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}

// 启动通知轮询
watch(isLoggedIn, (val) => {
  if (val) notifStore.startPolling()
  else notifStore.stopPolling()
}, { immediate: true })

onUnmounted(() => {
  notifStore.stopPolling()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-header {
  background: rgba(246, 245, 241, 0.86);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid transparent;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: $transition-base;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: $header-height;
  gap: $spacing-lg;
}

.logo {
  display: flex;
  align-items: center;
  gap: 11px;
  cursor: pointer;
  flex-shrink: 0;
  padding: 4px 8px;
  border-radius: $border-radius-md;
  transition: $transition-base;

  &:hover {
    background: $bg-subtle;
  }

  .logo-icon {
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    border-radius: 13px;
    background: linear-gradient(150deg, #3B837C, #22524E);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px -8px rgba(46, 110, 104, 0.9);
  }

  .brand-text {
    b {
      display: block;
      font-family: $font-family-serif;
      font-size: 16px;
      font-weight: 650;
      letter-spacing: 2px;
      line-height: 1.3;
      color: $text-primary;
    }

    span {
      display: block;
      font-size: 10.5px;
      color: $text-secondary;
      letter-spacing: 1.6px;
      text-transform: uppercase;
    }
  }
}

.nav-menu {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;

  :deep(.el-menu--horizontal) {
    height: $header-height !important;
    border-bottom: none !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px;

    &.el-menu {
      border-bottom: none !important;
    }

    .el-menu-item {
      font-size: 14px;
      font-weight: 600;
      color: $text-regular !important;
      border-radius: $border-radius-full !important;
      margin: 0 2px;
      padding: 0 16px !important;
      height: 38px !important;
      line-height: 38px !important;
      transition: $transition-base !important;
      border-bottom: none !important;

      &:hover {
        color: $primary-color !important;
        background: $bg-subtle !important;
      }

      &.is-active {
        color: $primary-dark !important;
        background: rgba(46, 110, 104, 0.1) !important;
        border-bottom: none !important;
      }

      &::before,
      &::after {
        display: none !important;
      }
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-shrink: 0;

  .search-box {
    width: 180px;
    transition: $transition-base;

    :deep(.el-input__wrapper) {
      border-radius: $border-radius-full !important;
      background: $bg-subtle !important;
      box-shadow: none !important;
      border: 1px solid $border-lighter !important;

      &:hover, &.is-focus {
        border-color: $primary-light !important;
        background: white !important;
      }
    }
  }

  .notification-badge {
    :deep(.el-badge__content) {
      background: $primary-color;
    }
  }

  .auth-btn-login {
    color: $text-regular !important;
    font-weight: 500;
    border-radius: $border-radius-full !important;
    padding: 0 16px !important;

    &:hover {
      color: $primary-color !important;
      background: $bg-subtle !important;
    }
  }

  .auth-btn-register {
    border-radius: $border-radius-full !important;
    background: $primary-gradient !important;
    border: none !important;
    color: white !important;
    font-weight: 600;
    padding: 0 20px !important;
    box-shadow: 0 4px 12px rgba(46, 110, 104, 0.3) !important;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(46, 110, 104, 0.4) !important;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 6px 10px 6px 6px;
    border-radius: $border-radius-full;
    transition: $transition-base;
    border: 1px solid transparent;

    &:hover {
      background: $bg-subtle;
      border-color: $border-base;
    }

    .username {
      font-size: 14px;
      font-weight: 500;
      color: $text-primary;
      max-width: 90px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .dropdown-icon {
      font-size: 12px;
      color: $text-secondary;
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .nav-menu { display: none; }
  .search-box { width: 140px !important; }
  .username { display: none !important; }
}

@media (max-width: $breakpoint-sm) {
  .header-content { padding: 0 $spacing-md; }
  .search-box { display: none !important; }
  .brand-text { display: none; }
}

/* 通知弹窗样式 */
.notification-popover {
  .popover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid $border-lighter;
    margin-bottom: 8px;

    .popover-title {
      font-size: 15px;
      font-weight: 600;
      color: $text-primary;
    }
  }

  .popover-list {
    max-height: 320px;
    overflow-y: auto;
  }

  .popover-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;

    &:hover { background: $bg-subtle; }

    &.unread { background: rgba(46, 110, 104, 0.04); }

    .item-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: $primary-color;
      flex-shrink: 0;
      margin-top: 5px;
    }

    .item-content {
      flex: 1;
      min-width: 0;
    }

    .item-title {
      font-size: 14px;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: 4px;
    }

    .item-text {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 4px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .item-time {
      font-size: 11px;
      color: $text-placeholder;
    }
  }

  .popover-footer {
    padding-top: 12px;
    border-top: 1px solid $border-lighter;
    text-align: center;
    margin-top: 8px;
  }
}
</style>
