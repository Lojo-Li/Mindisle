<template>
  <div class="notification-page">
    <div class="container">
      <div class="page-header">
        <h2>消息通知</h2>
        <el-button v-if="notifStore.unreadCount > 0" type="primary" @click="handleMarkAllRead" :loading="marking">
          全部标记已读
        </el-button>
      </div>

      <div v-loading="loading" class="notification-list">
        <el-empty v-if="!loading && notifStore.notifications.length === 0" description="暂无通知" :image-size="120" />

        <div
          v-for="item in notifStore.notifications"
          :key="item.id"
          class="notif-card"
          :class="{ unread: !item.is_read }"
          @click="handleClick(item)"
        >
          <div class="card-dot" v-if="!item.is_read" />
          <div class="card-body">
            <div class="card-top">
              <span class="card-type">
                <el-tag :type="getTypeTag(item.type)" size="small">{{ getTypeLabel(item.type) }}</el-tag>
              </span>
              <span class="card-time">{{ formatTime(item.created_at) }}</span>
            </div>
            <h4 class="card-title">{{ item.title }}</h4>
            <p class="card-content">{{ item.content }}</p>
          </div>
        </div>
      </div>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { ElMessage } from 'element-plus'

const router = useRouter()
const notifStore = useNotificationStore()

const loading = ref(false)
const marking = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadData = async () => {
  try {
    loading.value = true
    await notifStore.fetchList(page.value, pageSize.value)
    total.value = notifStore.total
  } finally {
    loading.value = false
  }
}

const handleClick = async (item) => {
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
  try {
    marking.value = true
    await notifStore.markAllRead()
    ElMessage.success('已全部标记为已读')
  } finally {
    marking.value = false
  }
}

const getTypeTag = (type) => {
  const map = {
    appointment_confirmed: 'success',
    appointment_rejected: 'danger',
    appointment_cancelled: 'info',
    appointment_completed: 'success',
    new_appointment: 'warning',
    new_message: 'primary',
    counselor_approved: 'success',
    counselor_rejected: 'danger',
    new_counselor_application: 'warning',
    system: 'info'
  }
  return map[type] || 'info'
}

const getTypeLabel = (type) => {
  const map = {
    appointment_confirmed: '预约确认',
    appointment_rejected: '预约拒绝',
    appointment_cancelled: '预约取消',
    appointment_completed: '咨询完成',
    new_appointment: '新预约',
    new_message: '新消息',
    counselor_approved: '入驻通过',
    counselor_rejected: '入驻被拒',
    new_counselor_application: '新申请',
    system: '系统通知'
  }
  return map[type] || '通知'
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => loadData())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.notification-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 680px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 120px;
}

.notif-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  border: 1px solid $border-lighter;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $primary-light;
    box-shadow: 0 4px 16px rgba(107, 82, 68, 0.08);
  }

  &.unread {
    background: rgba(232, 132, 90, 0.03);
    border-color: rgba(232, 132, 90, 0.15);
  }

  .card-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: $primary-color;
    flex-shrink: 0;
    margin-top: 6px;
  }

  .card-body {
    flex: 1;
    min-width: 0;
  }

  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .card-time {
    font-size: 12px;
    color: $text-placeholder;
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 6px 0;
  }

  .card-content {
    font-size: 14px;
    color: $text-secondary;
    margin: 0;
    line-height: 1.6;
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
</style>
