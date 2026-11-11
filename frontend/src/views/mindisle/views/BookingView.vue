<template>
<section class="view active" data-view="booking" ref="rootEl" @click="onClick">

      <div class="page-head">
        <div>
          <div class="eyebrow">Consultation</div>
          <h1>咨询预约</h1>
          <p>找到那个让你觉得「可以说下去」的人。首次咨询可免费更换一次。</p>
        </div>
      </div>

      <div class="filter-row">
        <button class="pill on" data-spec="all">全部</button>
        <button class="pill" data-spec="anxiety">焦虑与压力</button>
        <button class="pill" data-spec="mood">情绪低落</button>
        <button class="pill" data-spec="sleep">睡眠问题</button>
        <button class="pill" data-spec="relation">亲密关系</button>
        <button class="pill" data-spec="teen">青少年</button>
      </div>

      <div class="docs" data-list="docs" aria-busy="true">
        <!-- 加载骨架：接口返回前占位，避免先闪出一批写死的示例咨询师 -->
        <div class="doc doc-skeleton" v-for="n in 4" :key="n" aria-hidden="true">
          <div class="doc-top">
            <div class="sk-avatar"></div>
            <div style="flex:1">
              <div class="sk-line" style="width:42%;height:13px"></div>
              <div class="sk-line" style="width:62%;height:10px;margin-top:8px"></div>
            </div>
          </div>
          <div class="doc-tags">
            <span class="sk-pill"></span><span class="sk-pill"></span><span class="sk-pill"></span>
          </div>
          <div class="sk-line" style="width:100%;height:10px;margin-top:4px"></div>
          <div class="sk-line" style="width:78%;height:10px;margin-top:7px"></div>
          <div class="doc-meta">
            <span class="sk-line" style="width:52px;height:10px"></span>
            <span class="sk-line" style="width:44px;height:10px"></span>
          </div>
          <div class="sk-btn"></div>
        </div>
      </div>
    
<!-- ================= 预约弹窗 ================= -->
<div class="overlay" id="bookOverlay">
  <div class="modal">
    <div class="modal-head">
      <div>
        <h3 id="bookTitle">预约咨询</h3>
        <p style="font-size:12px;color:var(--ink-3);margin-top:2px">在线咨询</p>
      </div>
      <button class="close" id="bookClose">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
    </div>
    <div class="modal-body">
      <div style="font-size:12px;color:var(--ink-3);margin-bottom:9px">选择日期</div>
      <div class="days" id="days"></div>
      <div style="font-size:12px;color:var(--ink-3);margin-bottom:9px">可约时段</div>
      <div class="slots" id="slots"></div>

      <div class="book-note-wrap">
        <div class="book-note-head">
          <span>想聊些什么</span>
          <em>选填 · 咨询师会提前看到</em>
        </div>
        <textarea
          id="bookNote"
          class="book-note"
          rows="3"
          maxlength="1000"
          v-model="problemNote"
          placeholder="简单说说最近的困扰，比如：最近总是睡不好，白天没精神，想找个人聊聊（不会公开，只有咨询师能看到）"
        ></textarea>
        <div class="book-note-count">{{ problemNote.length }}/1000</div>
      </div>

      <div style="display:flex;gap:9px;margin-top:18px">
        <button class="btn btn-ghost" style="flex:1" id="bookCancel">取消</button>
        <button class="btn btn-primary" style="flex:1.4" id="bookConfirm">确认预约</button>
      </div>
      <p style="font-size:11px;color:var(--ink-3);margin-top:14px;text-align:center;line-height:1.8">
        需至少提前 15 分钟预约 · 公益免费，可随时取消
      </p>
    </div>
  </div>
</div>
</section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCounselorList, getAvailableSlots, createAppointment } from '@/api/counselor'
import { pickList, pickData, setHtml, setText, docCard, dayCardWithHint, slotCard, go, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
let counselors = []
let picked = null
let days = []
let dayIdx = 0
let slot = ''
// 问题描述（选填），提交时带给咨询师，也会显示在「我的预约」里
const problemNote = ref('')

// 擅长领域筛选：标签 → 命中关键词（按咨询师的擅长领域/简介/职称匹配）
const FILTERS = [
  { key: 'all', words: [] },
  { key: 'anxiety', words: ['焦虑', '压力', '强迫', '恐慌', '情绪管理'] },
  { key: 'mood', words: ['抑郁', '情绪', '低落', '创伤', '自我认同'] },
  { key: 'sleep', words: ['睡眠', '失眠'] },
  { key: 'relation', words: ['婚恋', '亲密', '家庭', '情感', '亲子'] },
  { key: 'teen', words: ['青少年', '学习', '儿童', '成瘾'] }
]
let activeKey = 'all'

function matchesFilter(c, filter) {
  if (!filter.words.length) return true
  const text = [c.specialties, c.bio, c.title].filter(Boolean).join(' ')
  return filter.words.some(w => text.includes(w))
}

function renderCounselors() {
  const filter = FILTERS.find(f => f.key === activeKey) || FILTERS[0]
  const list = counselors.filter(c => matchesFilter(c, filter))
  setHtml(
    rootEl.value,
    '[data-list="docs"]',
    list.length
      ? list.map(docCard).join('')
      : '<div class="doc"><h4>没有匹配的咨询师</h4>' +
        '<p style="font-size:12.5px;color:var(--ink-3);margin-top:8px">换一个标签看看，或点「全部」</p></div>'
  )
}

onMounted(async () => {
  days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    return d
  })
  try {
    counselors = pickList(await getCounselorList({ page: 1, page_size: 50 }))
    renderCounselors()
    // 数据已替换骨架屏，解除加载中标记
    const docsEl = rootEl.value?.querySelector('[data-list="docs"]')
    if (docsEl) docsEl.setAttribute('aria-busy', 'false')
  } catch (e) {
    toast('咨询师列表加载失败')
    // 出错时也要撤掉骨架屏，改为可读的错误提示，避免一直转圈
    const docsEl = rootEl.value?.querySelector('[data-list="docs"]')
    if (docsEl) {
      docsEl.setAttribute('aria-busy', 'false')
      setHtml(rootEl.value, '[data-list="docs"]',
        '<div class="doc"><h4>咨询师列表加载失败</h4>' +
        '<p style="font-size:12.5px;color:var(--ink-3);margin-top:8px">请检查网络后刷新页面重试</p></div>')
    }
  }
})

function dateStr(d) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

async function openBook(id) {
  picked = counselors.find(c => String(c.id) === String(id))
  if (!picked) return
  dayIdx = 0
  slot = ''
  problemNote.value = ''
  setText(rootEl.value, '#bookTitle', '预约 · ' + (picked.name || '咨询师'))
  await renderDays()
  const ov = rootEl.value.querySelector('#bookOverlay')
  if (ov) ov.classList.add('open')
}

async function renderDays() {
  setHtml(rootEl.value, '#days', days.map((d, i) =>
    dayCardWithHint(d, i, i === dayIdx, i === 0 ? '今天' : (i === 1 ? '明天' : ''))
  ).join(''))
  await renderSlots()
}

async function renderSlots() {
  if (!picked) return
  let list = []
  try {
    const d = pickData(await getAvailableSlots(picked.id, dateStr(days[dayIdx])))
    const raw = Array.isArray(d) ? d : (d.slots || d.items || [])
    // 保留全部时段（含不可约的），由 slotCard 渲染成置灰不可点，避免"时段凭空消失"
    list = raw
      .map(x => (typeof x === 'string'
        ? { time: x, available: true }
        : { time: x.time || x.slot || '', available: x.available !== false, reason: x.reason }))
      .filter(s => s.time)
  } catch (e) {
    // 接口不可用时按无可约时段处理
  }
  const openCount = list.filter(s => s.available).length
  setHtml(
    rootEl.value,
    '#slots',
    list.length
      ? list.map(s => slotCard(s.time, s.time === slot && s.available, !s.available)).join('') +
        (openCount === 0
          ? '<div style="font-size:12.5px;color:var(--ink-3);padding:10px 0;grid-column:1/-1">这一天已没有可约时段了，换一天看看吧</div>'
          : '')
      : '<div style="font-size:12.5px;color:var(--ink-3);padding:10px 0">该日期暂无可约时段，换一天看看</div>'
  )
}

async function confirm() {
  if (!picked || !slot) { toast('请先选择日期与时段'); return }
  try {
    // 时段可能是 "09:00-10:00"，取开始时间拼 datetime
    const start = slot.split('-')[0]
    await createAppointment({
      counselor_id: picked.id,
      consultation_type: 'video',
      appointment_date: dateStr(days[dayIdx]) + 'T' + start + ':00',
      problem_description: problemNote.value.trim() || null
    })
    toast('预约已提交')
    const ov = rootEl.value.querySelector('#bookOverlay')
    if (ov) ov.classList.remove('open')
    // 预约成功后直接跳到「我的预约」，方便确认状态
    router.push('/workspace/appointments')
  } catch (e) {
    toast('预约失败，请重试')
  }
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const p = e.target.closest('[data-spec]')
  if (p) {
    activeKey = p.getAttribute('data-spec')
    rootEl.value.querySelectorAll('[data-spec]').forEach(x => x.classList.toggle('on', x === p))
    renderCounselors()
    return
  }
  const b = e.target.closest('[data-book]')
  if (b) { openBook(b.getAttribute('data-book')); return }
  const d = e.target.closest('[data-day]')
  if (d) { dayIdx = Number(d.getAttribute('data-day')); slot = ''; renderDays(); return }
  const s = e.target.closest('[data-slot]')
  if (s) {
    if (s.disabled) return
    slot = s.getAttribute('data-slot')
    rootEl.value.querySelectorAll('[data-slot]').forEach(x => x.classList.toggle('on', x === s))
    return
  }
  if (e.target.closest('#bookConfirm')) { confirm(); return }
  if (e.target.closest('#bookClose') || e.target.closest('#bookCancel')) {
    const ov = rootEl.value.querySelector('#bookOverlay')
    if (ov) ov.classList.remove('open')
  }
}

</script>
