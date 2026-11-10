<template>
<section class="view active" data-view="counselor" ref="rootEl" @click="onClick">
  <div class="page-head">
    <div>
      <div class="eyebrow">Counselor Workspace</div>
      <h1 data-bind="greeting">你好，咨询师</h1>
      <p>这里是你的咨询工作台。待处理的预约会第一时间出现在这里。</p>
    </div>
    <div class="spacer"></div>
  </div>

  <div class="grid-3">
    <div class="stat"><div class="k">全部订单</div><div class="v"><span data-bind="totalOrders">0</span><small>笔</small></div><div class="d">来自真实预约数据</div></div>
    <div class="stat"><div class="k">待处理</div><div class="v"><span data-bind="pendingOrders">0</span><small>笔</small></div><div class="d">需要你确认或拒绝</div></div>
    <div class="stat"><div class="k">已完成</div><div class="v"><span data-bind="doneOrders">0</span><small>笔</small></div><div class="d">已结束的咨询</div></div>
  </div>

  <div class="card card-pad" style="margin-top:20px">
    <div class="card-head"><h3>最近的预约</h3></div>
    <div class="tl" data-list="counselorOrders"></div>
  </div>
</section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCounselorOrders, handleOrder } from '@/api/consultation'
import { useUserStore } from '@/stores/user'
import { pickList, setHtml, setText, esc, statusText, fmtDate, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
const userStore = useUserStore()
let orders = []

onMounted(async () => {
  const info = userStore.userInfo || {}
  setText(rootEl.value, '[data-bind="greeting"]', '你好，' + (info.nickname || info.username || '咨询师'))
  await load()
})

function orderCard(o) {
  const u = (o.user_info && o.user_info.nickname) || o.user_name || '来访者'
  const actions = o.status === 'pending'
    ? '<div style="display:flex;gap:8px;margin-top:8px">' +
      '<button class="btn btn-primary btn-sm" data-agree="' + o.id + '">同意</button>' +
      '<button class="btn btn-ghost btn-sm" data-reject="' + o.id + '">拒绝</button></div>'
    : ''
  return '<div class="tl-item"><b>' + esc(u) + ' · ' + statusText(o.status) + '</b>' +
    '<span>' + fmtDate(o.appointment_date) + ' · ' + esc(o.problem_description || '未填写问题描述') + '</span>' +
    actions + '</div>'
}

async function load() {
  try {
    orders = pickList(await getCounselorOrders({ page: 1, page_size: 20 }))
    setText(rootEl.value, '[data-bind="totalOrders"]', orders.length)
    setText(rootEl.value, '[data-bind="pendingOrders"]', orders.filter(o => o.status === 'pending').length)
    setText(rootEl.value, '[data-bind="doneOrders"]', orders.filter(o => o.status === 'completed').length)
    setHtml(rootEl.value, '[data-list="counselorOrders"]', orders.length
      ? orders.map(orderCard).join('')
      : '<div class="tl-item"><b>暂无预约订单</b></div>')
  } catch (e) {
    toast('订单加载失败')
  }
}

async function decide(id, action) {
  try {
    const payload = action === 'reject'
      ? { action, reason: '咨询师暂无法接单' }
      : { action }
    await handleOrder(id, payload)
    toast(action === 'agree' ? '已接受预约' : '已拒绝预约')
    await load()
  } catch (e) {
    toast('操作失败')
  }
}

function onClick(e) {
  const a = e.target.closest('[data-agree]')
  if (a) { decide(a.getAttribute('data-agree'), 'agree'); return }
  const r = e.target.closest('[data-reject]')
  if (r) { decide(r.getAttribute('data-reject'), 'reject'); return }
  const g = e.target.closest('[data-go]')
  if (g) router.push(g.getAttribute('data-go'))
}

</script>
