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

  <div class="docs" data-list="sessions"></div>
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

const TYPE_LABEL = { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }

const EMPTY_TEXT = {
  all: '还没有预约记录，来访者下单后会出现在这里。',
  pending: '没有待确认的预约。',
  confirmed: '没有已确认的预约。',
  in_progress: '当前没有进行中的咨询。',
  completed: '还没有已完成的咨询。',
  cancelled: '没有已取消的预约。'
}

function sessionCard(o) {
  const u = (o.user_info && o.user_info.nickname) || o.user_name || '来访者'
  const type = TYPE_LABEL[o.consultation_type] || '咨询'
  const actions = []
  if (o.status === 'pending') {
    actions.push('<button class="btn btn-primary btn-sm" data-agree="' + o.id + '">接单</button>')
    actions.push('<button class="btn btn-ghost btn-sm" data-reject="' + o.id + '">拒绝</button>')
  } else if (o.status === 'confirmed' || o.status === 'in_progress') {
    actions.push('<button class="btn btn-primary btn-sm" data-enter="' + o.id + '">进入会话</button>')
  }

  return '<div class="doc">' +
    '<div class="doc-top">' +
      '<div class="avatar av-a">' + esc(u.slice(0, 1)) + '</div>' +
      '<div><h4>' + esc(u) + '<span class="tag ' + (STATUS_TAG[o.status] || 'sea') + '" style="font-size:10px;padding:1.5px 7px">' +
        esc(statusText(o.status)) + '</span></h4>' +
      '<div class="sub">' + esc(type) + ' · ' + esc(fmtDate(o.appointment_date)) + '</div></div>' +
    '</div>' +
    '<div class="doc-tags"><span class="tag">公益免费</span><span class="tag">' + esc(o.appointment_no || '') + '</span></div>' +
    '<p class="doc-bio">' + esc(o.problem_description || '来访者未填写问题描述。') + '</p>' +
    (actions.length
      ? '<div style="display:flex;gap:8px;margin-top:14px">' + actions.join('') + '</div>'
      : '<div class="doc-meta"><span>本次咨询已结束</span></div>') +
    '</div>'
}

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
  if (en) { router.push('/consultation/counselor/' + en.getAttribute('data-enter')); return }
}

onMounted(load)
</script>
