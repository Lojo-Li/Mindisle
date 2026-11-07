import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getUnreadCount, getNotifications, markNotificationRead, markAllNotificationsRead } from '@/api/notification'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)
  const notifications = ref([])
  const total = ref(0)
  const loading = ref(false)

  let pollTimer = null

  async function fetchUnreadCount() {
    try {
      const res = await getUnreadCount()
      unreadCount.value = res.data.count || 0
    } catch {
      // silent fail
    }
  }

  async function fetchList(page = 1, pageSize = 20) {
    try {
      loading.value = true
      const res = await getNotifications({ page, page_size: pageSize })
      notifications.value = res.data.items || []
      total.value = res.data.total || 0
      unreadCount.value = res.data.unread_count || 0
    } finally {
      loading.value = false
    }
  }

  async function markRead(id) {
    try {
      await markNotificationRead(id)
      const item = notifications.value.find(n => n.id === id)
      if (item) item.is_read = true
      if (unreadCount.value > 0) unreadCount.value--
    } catch {
      // silent fail
    }
  }

  async function markAllRead() {
    try {
      await markAllNotificationsRead()
      notifications.value.forEach(n => { n.is_read = true })
      unreadCount.value = 0
    } catch {
      // silent fail
    }
  }

  function startPolling(intervalMs = 30000) {
    stopPolling()
    fetchUnreadCount()
    pollTimer = setInterval(fetchUnreadCount, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    unreadCount, notifications, total, loading,
    fetchUnreadCount, fetchList, markRead, markAllRead,
    startPolling, stopPolling
  }
})
