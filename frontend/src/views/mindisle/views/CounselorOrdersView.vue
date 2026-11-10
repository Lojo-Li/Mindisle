<template>
<section class="view active" data-view="counselor-orders" ref="rootEl" @click="onClick">

  <div class="page-head">
    <div>
      <div class="eyebrow">Orders</div>
      <h1>预约订单</h1>
      <p>待确认的预约请尽快处理，学生可以随时取消未开始的订单。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost btn-sm" data-refresh>刷新</button>
  </div>

  <div class="filter-row" style="margin-bottom:16px">
    <button
      v-for="t in statusTabs"
      :key="t.value"
      class="pill"
      :class="{ on: statusTab === t.value }"
      :data-status="t.value"
    >{{ t.label }}<span v-if="counts[t.value]" class="pill-count">{{ counts[t.value] }}</span></button>
  </div>

  <div v-if="loading" class="card card-pad empty-box">
    <h4>正在加载订单…</h4>
  </div>

  <div v-else-if="!orders.length" class="card card-pad empty-box">
    <h4>暂无订单</h4>
    <p>{{ statusTab === 'all' ? '还没有学生预约你的咨询。' : '这个状态下暂时没有订单。' }}</p>
  </div>

  <div v-else class="stack" style="gap:12px">
    <div v-for="o in orders" :key="o.id" class="card card-pad order-card">
      <div class="order-top">
        <div class="avatar av-b">{{ (userName(o) || '学').slice(0, 1) }}</div>
        <div class="order-main">
          <h4>
            {{ userName(o) }}
            <span class="tag" :class="statusTagClass(o.status)">{{ statusText(o.status) }}</span>
          </h4>
          <div class="order-sub">{{ typeText(o.consultation_type) }} · 50 分钟</div>
        </div>
        <div class="order-time">{{ fmtDate(o.appointment_date) }}</div>
      </div>

      <div v-if="o.problem_description || o.appointment_no" class="order-meta">
        <span v-if="o.appointment_no">订单号 {{ o.appointment_no }}</span>
        <span v-if="o.problem_description">学生诉求：{{ o.problem_description }}</span>
        <span v-if="o.cancel_reason" class="cancel-reason">取消原因：{{ o.cancel_reason }}</span>
      </div>

      <div class="order-actions">
        <template v-if="o.status === 'pending'">
          <button class="btn btn-ghost btn-sm" :data-reject="o.id">拒绝</button>
          <button class="btn btn-primary btn-sm" :data-agree="o.id">接受预约</button>
        </template>
        <template v-else-if="o.status === 'confirmed' || o.status === 'in_progress'">
          <button class="btn btn-soft btn-sm" :data-chat="o.id">进入咨询</button>
        </template>
        <template v-else-if="o.status === 'completed'">
          <button class="btn btn-ghost btn-sm" :data-detail="o.id">查看详情</button>
        </template>
      </div>
    </div>
  </div>

</section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCounselorOrders, handleOrder } from '@/api/consultation'
import { pickList } from '../workspace'

const router = useRouter()
const rootEl = ref(null)

const loading = ref(false)
const orders = ref([])
const counts = ref({})
const statusTab = ref('all')

const STATUS_LABELS = {
  pending: '待确认',
  confirmed: '已确认',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消'
}
const statusTabs = [
  { label: '全部', value: 'all' },
  ...Object.entries(STATUS_LABELS).map(([value, label]) => ({ label, value }))
]

onMounted(() => {
  loadOrders()
  loadCounts()
})

async function loadOrders() {
  loading.value = true
  try {
    const status = statusTab.value === 'all' ? '' : statusTab.value
    const res = await getCounselorOrders({ status, page_size: 100 })
    orders.value = pickList(res)
  } catch (e) {
    orders.value = []
    ElMessage.error('订单加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function loadCounts() {
  const statuses = ['all', ...Object.keys(STATUS_LABELS)]
  const results = await Promise.allSettled(
    statuses.map(s => getCounselorOrders({ status: s === 'all' ? '' : s, page_size: 1 }))
  )
  const next = {}
  results.forEach((r, i) => {
    if (r.status === 'fulfilled') {
      const total = (r.value && r.value.data && r.value.data.total) || 0
      if (total) next[statuses[i]] = total
    }
  })
  counts.value = next
}

function userName(o) {
  const u = o.user_info || o.user
  return (u && (u.nickname || u.email)) || '学生'
}
function statusText(s) { return STATUS_LABELS[s] || s || '未知' }
function statusTagClass(s) {
  if (s === 'pending') return 'lamp'
  if (s === 'confirmed' || s === 'in_progress' || s === 'completed') return 'sea'
  return ''
}
function typeText(t) {
  const map = { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }
  return map[t] || t || '咨询'
}
function fmtDate(v) {
  if (!v) return ''
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v).replace('T', ' ').slice(0, 16)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

async function doAgree(id) {
  try {
    await ElMessageBox.confirm('确定接受这笔预约吗？接受后学生将收到确认通知。', '接受预约', {
      confirmButtonText: '确认接受',
      cancelButtonText: '再看看',
      type: 'warning'
    })
  } catch { return }
  try {
    await handleOrder(id, { action: 'agree' })
    ElMessage.success('已接受预约')
    refresh()
  } catch (e) {
    const d = e && e.response && e.response.data && e.response.data.detail
    ElMessage.error(typeof d === 'string' ? d : '操作失败，请重试')
  }
}

async function doReject(id) {
  let reason = ''
  try {
    const { value } = await ElMessageBox.prompt('请说明拒绝原因，学生会看到这段说明。', '拒绝预约', {
      confirmButtonText: '确认拒绝',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：该时段已有安排',
      inputValidator: v => (v && v.trim() ? true : '请填写拒绝原因')
    })
    reason = (value || '').trim()
  } catch { return }
  try {
    await handleOrder(id, { action: 'reject', reason })
    ElMessage.success('已拒绝该预约')
    refresh()
  } catch (e) {
    const d = e && e.response && e.response.data && e.response.data.detail
    ElMessage.error(typeof d === 'string' ? d : '操作失败，请重试')
  }
}

async function doDetail(id) {
  const o = orders.value.find(x => String(x.id) === String(id))
  if (!o) return
  const lines = [
    '学生：' + userName(o),
    '时间：' + fmtDate(o.appointment_date),
    '方式：' + typeText(o.consultation_type),
    '订单号：' + (o.appointment_no || '—')
  ]
  if (o.problem_description) lines.push('学生诉求：' + o.problem_description)
  ElMessageBox.alert(lines.join('\n'), '订单详情', {
    confirmButtonText: '知道了',
    customStyle: { whiteSpace: 'pre-line' }
  })
}

function refresh() {
  loadOrders()
  loadCounts()
}

function onClick(e) {
  if (e.target.closest('[data-refresh]')) { refresh(); return }

  const st = e.target.closest('[data-status]')
  if (st) {
    const v = st.getAttribute('data-status')
    if (v !== statusTab.value) { statusTab.value = v; loadOrders() }
    return
  }

  const a = e.target.closest('[data-agree]')
  if (a) { doAgree(a.getAttribute('data-agree')); return }

  const r = e.target.closest('[data-reject]')
  if (r) { doReject(r.getAttribute('data-reject')); return }

  const c = e.target.closest('[data-chat]')
  if (c) { router.push('/counselor/chat/' + c.getAttribute('data-chat')); return }

  const d = e.target.closest('[data-detail]')
  if (d) { doDetail(d.getAttribute('data-detail')); return }
}
</script>

<style scoped>
.empty-box h4 { font-size: 14.5px; font-weight: 590; }
.empty-box p { font-size: 13px; color: var(--ink-3); margin-top: 8px; }

.order-card { transition: box-shadow .2s var(--ease); }
.order-card:hover { box-shadow: var(--shadow-m); }

.order-top { display: flex; align-items: center; gap: 13px; }
.order-main { flex: 1; min-width: 0; }
.order-main h4 {
  font-size: 14.5px; font-weight: 590; letter-spacing: .2px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.order-sub { font-size: 12.5px; color: var(--ink-3); margin-top: 4px; }
.order-time {
  font-size: 12.5px; color: var(--ink-2);
  font-variant-numeric: tabular-nums; white-space: nowrap;
}

.order-meta {
  display: flex; flex-wrap: wrap; gap: 14px;
  margin-top: 12px; font-size: 12px; color: var(--ink-3);
}
.cancel-reason { color: var(--rose); }

.order-actions {
  display: flex; gap: 9px; justify-content: flex-end;
  margin-top: 14px; padding-top: 14px;
  border-top: 1px solid var(--line-2);
}

.pill-count {
  margin-left: 6px; font-size: 11px; opacity: .72;
  font-variant-numeric: tabular-nums;
}
</style>
