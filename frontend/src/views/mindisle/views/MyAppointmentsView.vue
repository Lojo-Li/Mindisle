<template>
<section class="view active" data-view="appointments" ref="rootEl">

  <div class="page-head">
    <div>
      <div class="eyebrow">My Sessions</div>
      <h1>我的预约</h1>
      <p>你与咨询师之间的每一次约定，都在这里安静地等着。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-primary" @click="goBooking">＋ 预约咨询</button>
  </div>

  <!-- 状态筛选 -->
  <div class="filter-row">
    <button
      v-for="t in TABS"
      :key="t.key"
      class="pill"
      :class="{ on: activeTab === t.key }"
      @click="activeTab = t.key"
    >
      {{ t.label }}<span v-if="countOf(t.key)" class="pill-count">{{ countOf(t.key) }}</span>
    </button>
  </div>

  <!-- 加载中 -->
  <div v-if="loading" class="card">
    <div class="empty">
      <div class="empty-mark">◌</div>
      <div>正在加载…</div>
    </div>
  </div>

  <!-- 加载失败 -->
  <div v-else-if="error" class="card">
    <div class="empty">
      <div class="empty-mark">!</div>
      <div>预约列表加载失败，请检查网络</div>
      <button class="btn btn-ghost btn-sm" style="margin-top:14px" @click="load">重新加载</button>
    </div>
  </div>

  <!-- 无数据 -->
  <div v-else-if="!filtered.length" class="card">
    <div class="empty">
      <div class="empty-mark">✧</div>
      <div class="empty-title">{{ activeTab === 'all' ? '还没有预约记录' : '这个状态下暂无预约' }}</div>
      <div class="empty-sub">当你想找人聊聊的时候，我们一直在这里。</div>
      <button class="btn btn-primary btn-sm" style="margin-top:14px" @click="goBooking">去找咨询师</button>
    </div>
  </div>

  <!-- 预约卡片列表 -->
  <div v-else class="appt-list">
    <div v-for="a in filtered" :key="a.id" class="appt-card">
      <div class="appt-avatar">{{ initialOf(a) }}</div>

      <div class="appt-main">
        <div class="appt-title-row">
          <h4>{{ counselorNameOf(a) }}</h4>
          <span class="tag" :class="statusClass(a.status)">{{ statusLabel(a.status) }}</span>
        </div>
        <div class="appt-meta">
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9.5h18M8 3v3M16 3v3"/></svg>
            {{ fmtDate(a.appointment_date) }}
          </span>
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5l3 1.8"/></svg>
            {{ timeOf(a.appointment_date) }}
          </span>
          <span class="tag">{{ typeLabel(a.consultation_type) }}</span>
          <span class="tag sea">公益免费</span>
        </div>
        <div v-if="a.problem_description" class="appt-note">
          你的诉求：{{ a.problem_description }}
        </div>
        <div v-if="a.cancel_reason" class="appt-note cancel-note">
          取消原因：{{ a.cancel_reason }}
        </div>
        <div class="appt-no">订单号 {{ a.appointment_no }}</div>
      </div>

      <div class="appt-actions">
        <button
          v-if="canCancel(a)"
          class="btn btn-ghost btn-sm"
          :disabled="busyId === a.id"
          @click="doCancel(a)"
        >{{ busyId === a.id ? '处理中…' : '取消预约' }}</button>

        <button
          v-if="canEnter(a)"
          class="btn btn-primary btn-sm"
          @click="enterChat(a)"
        >进入咨询</button>

        <button
          v-if="a.status === 'completed'"
          class="btn btn-soft btn-sm"
          @click="goReview(a)"
        >评价咨询</button>
      </div>
    </div>
  </div>

</section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { getUserAppointments, cancelAppointment } from '@/api/counselor'
import { pickData, toast } from '../workspace'

const router = useRouter()
const rootEl = ref(null)

const loading = ref(true)
const error = ref(false)
const busyId = ref(null)
const activeTab = ref('all')
const list = ref([])

const TABS = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待确认' },
  { key: 'confirmed', label: '已确认' },
  { key: 'in_progress', label: '进行中' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' }
]

// ---------- 数据 ----------
function normalize(raw) {
  const arr = Array.isArray(raw) ? raw : (raw?.items || raw?.list || [])
  return arr.map(a => ({
    ...a,
    price: 0
  }))
}

async function load() {
  loading.value = true
  error.value = false
  try {
    const d = pickData(await getUserAppointments({ page: 1, page_size: 100 }))
    list.value = normalize(d)
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ---------- 计算 ----------
const filtered = computed(() => {
  if (activeTab.value === 'all') return list.value
  return list.value.filter(a => a.status === activeTab.value)
})

function countOf(key) {
  if (key === 'all') return list.value.length
  return list.value.filter(a => a.status === key).length
}

// ---------- 展示辅助 ----------
function counselorNameOf(a) {
  return a?.counselor?.name || a?.counselor_name || '咨询师'
}

function initialOf(a) {
  const n = counselorNameOf(a)
  return String(n).slice(0, 1)
}

const STATUS_LABEL = {
  pending: '待确认',
  confirmed: '已确认',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消'
}

function statusLabel(s) {
  return STATUS_LABEL[s] || s || '未知'
}

function statusClass(s) {
  if (s === 'pending') return 'lamp'
  if (s === 'completed') return 'sea'
  if (s === 'cancelled') return 'rose'
  return 'sea'
}

function typeLabel(t) {
  return { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }[t] || '咨询'
}

function parseDate(v) {
  if (!v) return null
  const d = new Date(String(v).replace(' ', 'T'))
  return isNaN(d.getTime()) ? null : d
}

function fmtDate(v) {
  const d = parseDate(v)
  if (!d) return '—'
  const w = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${w}`
}

function timeOf(v) {
  const d = parseDate(v)
  if (!d) return '—'
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// ---------- 行为 ----------
function canCancel(a) {
  return a.status === 'pending' || a.status === 'confirmed'
}

function canEnter(a) {
  return a.status === 'confirmed' || a.status === 'in_progress'
}

async function doCancel(a) {
  try {
    await ElMessageBox.confirm(
      `确定取消与「${counselorNameOf(a)}」的预约吗？取消后该时段会重新开放。`,
      '取消预约',
      { confirmButtonText: '确定取消', cancelButtonText: '再想想', type: 'warning' }
    )
  } catch (e) {
    return
  }
  busyId.value = a.id
  try {
    await cancelAppointment(a.id)
    toast('预约已取消')
    await load()
  } catch (e) {
    toast('取消失败，请重试')
  } finally {
    busyId.value = null
  }
}

function goBooking() {
  router.push('/workspace/booking')
}

function enterChat(a) {
  router.push('/workspace/chat/' + a.id)
}

function goReview(a) {
  router.push('/counselor/review/' + a.id)
}
</script>

<style scoped>
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 22px 0 20px;
}

.pill-count {
  margin-left: 6px;
  font-size: 10.5px;
  opacity: .7;
}

.appt-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.appt-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 22px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-s);
  transition: border-color .2s, box-shadow .2s;
}

.appt-card:hover {
  border-color: #CFDCD9;
  box-shadow: 0 6px 22px -14px rgba(34, 82, 78, .5);
}

.appt-avatar {
  flex: 0 0 auto;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(160deg, #357B74, #22524E);
  letter-spacing: .5px;
}

.appt-main {
  flex: 1 1 auto;
  min-width: 0;
}

.appt-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.appt-title-row h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: .2px;
}

.appt-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  font-size: 12.5px;
  color: var(--ink-2);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.appt-note {
  margin-top: 9px;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.7;
}

.cancel-note {
  color: #96574E;
}

.appt-no {
  margin-top: 8px;
  font-size: 11px;
  color: var(--ink-3);
  letter-spacing: .3px;
}

.appt-actions {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: stretch;
}

/* 空态：沿用 .mi-portal .card 卡片外壳 + .mi-portal .empty 居中文字，
   仅补充图标与标题的层级，不引入新边框/背景，保证与列表态观感一致 */
.empty-mark {
  font-size: 26px;
  color: var(--sea);
  opacity: .42;
  margin-bottom: 10px;
}

.empty-title {
  font-size: 14px;
  font-weight: 590;
  color: var(--ink);
  letter-spacing: .2px;
}

.empty-sub {
  margin-top: 6px;
  font-size: 12.5px;
  color: var(--ink-3);
}

@media (max-width: 720px) {
  .appt-card {
    flex-wrap: wrap;
  }
  .appt-actions {
    flex-direction: row;
    width: 100%;
    margin-top: 6px;
  }
  .appt-actions .btn {
    flex: 1;
  }
}
</style>
