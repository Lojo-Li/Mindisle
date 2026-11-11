<template>
<section class="view active" data-view="counselor-sessions" ref="rootEl" @click="onClick">

  <div class="page-head">
    <div>
      <div class="eyebrow">{{ isOrders ? 'Orders' : 'Sessions' }}</div>
      <h1>{{ isOrders ? '预约订单' : '咨询会话' }}</h1>
      <p v-if="isOrders">所有来访者的预约都在这里，待确认的订单可以接单或拒绝。所有咨询均为公益活动，不收费。</p>
      <p v-else>已确认和进行中的咨询会出现在这里，点「进入会话」开始沟通。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost" data-refresh>刷新</button>
  </div>

  <div class="filter-row">
    <button class="pill on" data-filter="all">全部</button>
    <button v-if="isOrders" class="pill" data-filter="pending">待确认</button>
    <button class="pill" data-filter="confirmed">已确认</button>
    <button class="pill" data-filter="in_progress">进行中</button>
    <button class="pill" data-filter="completed">已完成</button>
    <button v-if="isOrders" class="pill" data-filter="cancelled">已取消</button>
  </div>

  <div class="sess-feed" data-list="sessions"></div>
</section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCounselorOrders, handleOrder } from '@/api/consultation'
import { pickList, setHtml, esc, statusText, fmtDate, toast } from '../workspace'

const props = defineProps({ mode: { type: String, default: 'orders' } })
const isOrders = computed(() => props.mode !== 'sessions')

const rootEl = ref(null)
const router = useRouter()
let orders = []
let activeFilter = 'all'

const STATUS_TAG = {
  pending: 'sea',
  confirmed: 'sea',
  in_progress: 'sea',
  completed: 'sea',
  cancelled: 'sea'
}

const TYPE_LABEL = { video: '在线咨询', voice: '在线咨询', offline: '线下咨询' }

const EMPTY_TEXT = {
  all: '还没有预约记录，来访者下单后会出现在这里。',
  pending: '没有待确认的预约。',
  confirmed: '没有已确认的预约。',
  in_progress: '当前没有进行中的咨询。',
  completed: '还没有已完成的咨询。',
  cancelled: '没有已取消的预约。'
}

// 单列横向卡片。两种模式共用结构，但内容侧重点不同：
// - 订单模式（审核用途）：突出学生诉求与时间，操作为 接受 / 拒绝
// - 会话模式（接待用途）：突出当前状态与进入入口
function sessionCard(o) {
  const u = (o.user_info && o.user_info.nickname) || o.user_name || '来访者'
  const type = TYPE_LABEL[o.consultation_type] || '咨询'
  const actions = []
  if (isOrders.value && o.status === 'pending') {
    actions.push('<button class="btn btn-primary btn-sm" data-agree="' + o.id + '">接受预约</button>')
    actions.push('<button class="btn btn-ghost btn-sm" data-reject="' + o.id + '">拒绝</button>')
  } else if (o.status === 'confirmed' || o.status === 'in_progress') {
    actions.push('<button class="btn btn-soft btn-sm" data-enter="' + o.id + '">' +
      (isOrders.value ? '进入咨询' : '进入会话') + '</button>')
  } else if (o.status === 'completed') {
    actions.push('<button class="btn btn-ghost btn-sm" data-enter="' + o.id + '">查看记录</button>')
  }

  const statusCls = STATUS_TAG[o.status] || 'sea'
  // 订单页把诉求作为主体强调；会话页弱化诉求，专注状态
  const noteCls = isOrders.value ? 'sess-note emphasis' : 'sess-note'
  const note = o.problem_description
    ? '<div class="' + noteCls + '"><b>学生诉求</b>' + esc(o.problem_description) + '</div>'
    : '<div class="sess-note empty">学生未填写诉求描述</div>'

  const cancelNote = (isOrders.value && o.cancel_reason)
    ? '<div class="sess-note cancel">取消原因：' + esc(o.cancel_reason) + '</div>'
    : ''

  return '<div class="sess-card' + (isOrders.value ? ' is-order' : '') + '">' +
    '<div class="sess-avatar">' + esc(u.slice(0, 1)) + '</div>' +
    '<div class="sess-main">' +
      '<div class="sess-title-row"><h4>' + esc(u) + '</h4>' +
        '<span class="tag ' + statusCls + '">' + esc(statusText(o.status)) + '</span></div>' +
      '<div class="sess-meta">' +
        '<span class="meta-item">' + ICON_CAL + esc(fmtDate(o.appointment_date)) + '</span>' +
        '<span class="tag">' + esc(type) + '</span>' +
      '</div>' +
      note + cancelNote +
    '</div>' +
    (actions.length
      ? '<div class="sess-actions">' + actions.join('') + '</div>'
      : '<div class="sess-actions"><span class="sess-ended">已结束</span></div>') +
    '</div>'
}

const ICON_CAL = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9.5h18M8 3v3M16 3v3"/></svg>'

function render() {
  const base = isOrders.value
    ? orders
    : orders.filter(o => ['confirmed', 'in_progress', 'completed'].includes(o.status))
  const list = activeFilter === 'all' ? base : base.filter(o => o.status === activeFilter)
  setHtml(
    rootEl.value,
    '[data-list="sessions"]',
    list.length
      ? list.map(sessionCard).join('')
      : '<div class="doc"><h4>暂无会话</h4>' +
        '<p style="font-size:12.5px;color:var(--ink-3);margin-top:8px">' +
        esc(isOrders.value ? (EMPTY_TEXT[activeFilter] || EMPTY_TEXT.all) : '还没有可进入的会话，先在「预约订单」里接单。') + '</p></div>'
  )
}

async function load() {
  try {
    orders = pickList(await getCounselorOrders({ page: 1, page_size: 50 }))
    render()
  } catch (e) {
    toast('会话加载失败')
  }
}

async function decide(id, action) {
  try {
    const payload = action === 'reject' ? { action, reason: '咨询师暂无法接单' } : { action }
    await handleOrder(id, payload)
    toast(action === 'agree' ? '已接受预约' : '已拒绝预约')
    await load()
  } catch (e) {
    toast('操作失败')
  }
}

function onClick(e) {
  const f = e.target.closest('[data-filter]')
  if (f) {
    activeFilter = f.getAttribute('data-filter')
    rootEl.value.querySelectorAll('[data-filter]').forEach(x => x.classList.toggle('on', x === f))
    render()
    return
  }
  if (e.target.closest('[data-refresh]')) { load(); return }
  const a = e.target.closest('[data-agree]')
  if (a) { decide(a.getAttribute('data-agree'), 'agree'); return }
  const r = e.target.closest('[data-reject]')
  if (r) { decide(r.getAttribute('data-reject'), 'reject'); return }
  const en = e.target.closest('[data-enter]')
  if (en) { router.push('/counselor/dashboard/chat/' + en.getAttribute('data-enter')); return }
}

onMounted(load)
</script>

<style>
/* 注意：不能用 scoped —— 卡片由 sessionCard() 拼成字符串后经 innerHTML 注入，
   scoped 生成的 data-v-xxx 属性不会出现在这些动态节点上，样式会全部失效。 */

/* 单列横向卡片：与「预约订单」同结构，便于两页之间保持一致的视觉语言 */
.sess-feed { display: flex; flex-direction: column; gap: 12px; }
.sess-feed .sess-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 22px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-s);
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}
.sess-feed .sess-card:hover {
  border-color: #CFDCD9;
  box-shadow: 0 6px 22px -14px rgba(34, 82, 78, .5);
}
.sess-feed .sess-avatar {
  flex: 0 0 auto;
  width: 46px; height: 46px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 600; color: #fff;
  background: linear-gradient(160deg, #357B74, #22524E);
  letter-spacing: .5px;
}
.sess-feed .sess-main { flex: 1 1 auto; min-width: 0; }
.sess-feed .sess-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.sess-feed .sess-main h4 { font-size: 15px; font-weight: 500; }
.sess-feed .sess-meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
  font-size: 12.5px; color: var(--ink-2);
}
.sess-feed .sess-meta .meta-item {
  display: inline-flex; align-items: center; gap: 5px;
  font-variant-numeric: tabular-nums;
}
.sess-feed .sess-meta .meta-item svg { color: var(--ink-3); flex: 0 0 auto; }
.sess-feed .sess-note {
  margin-top: 11px;
  padding: 10px 13px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid var(--line-2);
  font-size: 13px;
  line-height: 1.7;
  color: var(--ink);
  word-break: break-word;
}
.sess-feed .sess-note.empty { color: var(--ink-3); }

/* 订单模式：诉求是审核的主要依据，用品牌色描边强调，标签加粗分隔 */
.sess-feed .sess-note.emphasis {
  border-left: 3px solid var(--sea);
  padding-left: 12px;
  background: var(--sea-soft, #EAF3F1);
}
.sess-feed .sess-note.emphasis b {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: var(--sea-deep, #22524E);
  margin-bottom: 4px;
  letter-spacing: .3px;
}
.sess-feed .sess-note.cancel { color: var(--rose); background: transparent; border-color: transparent; padding-left: 0; }
.sess-feed .sess-actions {
  flex: 0 0 auto;
  display: flex; flex-direction: column; gap: 8px;
  min-width: 96px;
}
.sess-feed .sess-ended { font-size: 12px; color: var(--ink-3); text-align: right; }

@media (max-width: 720px) {
.sess-feed .sess-card { flex-wrap: wrap; padding: 16px; }
.sess-feed .sess-actions { flex-direction: row; width: 100%; justify-content: flex-end; }
.sess-feed .sess-actions .btn { flex: 1; }
}
</style>
