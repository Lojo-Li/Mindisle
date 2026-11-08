<template>
<section class="view active" data-view="booking" ref="rootEl" @click="onClick">

      <div class="page-head">
        <div>
          <div class="eyebrow">Consultation</div>
          <h1>咨询预约</h1>
          <p>找到那个让你觉得「可以说下去」的人。首次咨询可免费更换一次。</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost">我的预约</button>
      </div>

      <div class="filter-row">
        <button class="pill on">全部</button>
        <button class="pill">焦虑与压力</button>
        <button class="pill">情绪低落</button>
        <button class="pill">睡眠问题</button>
        <button class="pill">亲密关系</button>
        <button class="pill">青少年</button>
      </div>

      <div class="docs" data-list="docs">
        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-a">陈</div>
            <div>
              <h4>陈曦
                <span class="tag sea" style="font-size:10px;padding:1.5px 7px">认证</span>
              </h4>
              <div class="sub">临床心理学硕士 · 8 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.9</div>
          </div>
          <div class="doc-tags">
            <span class="tag">焦虑</span><span class="tag">正念</span><span class="tag">情绪调节</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            擅长用认知行为与正念结合的方式，陪你把"停不下来的脑子"慢慢调慢。
          </p>
          <div class="doc-meta">
            <span>本周可约 4 个时段</span>
            <span class="price">¥480 <small>/ 50 分钟</small></span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="陈曦">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-b">周</div>
            <div>
              <h4>周予安</h4>
              <div class="sub">国家二级心理咨询师 · 6 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.8</div>
          </div>
          <div class="doc-tags">
            <span class="tag">亲密关系</span><span class="tag">自我认同</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            相信关系里的痛，也要在关系里被修好。风格温和，擅长长程陪伴。
          </p>
          <div class="doc-meta">
            <span>本周可约 6 个时段</span>
            <span class="price">¥420 <small>/ 50 分钟</small></span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="周予安">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-c">林</div>
            <div>
              <h4>林知夏
                <span class="tag lamp" style="font-size:10px;padding:1.5px 7px">精神科</span>
              </h4>
              <div class="sub">副主任医师 · 12 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 5.0</div>
          </div>
          <div class="doc-tags">
            <span class="tag">睡眠障碍</span><span class="tag">抑郁</span><span class="tag">药物评估</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            医学背景，适合症状较重或需要药物联合评估的情况。
          </p>
          <div class="doc-meta">
            <span>本周可约 2 个时段</span>
            <span class="price">¥680 <small>/ 50 分钟</small></span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="林知夏">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-d">苏</div>
            <div>
              <h4>苏漾</h4>
              <div class="sub">心理咨询师 · 4 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.7</div>
          </div>
          <div class="doc-tags">
            <span class="tag">学业压力</span><span class="tag">青少年</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            和 12–22 岁的年轻人工作，懂那种"被期待推着走"的窒息感。
          </p>
          <div class="doc-meta">
            <span>本周可约 8 个时段</span>
            <span class="price">¥360 <small>/ 50 分钟</small></span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="苏漾">选择时段</button>
        </div>
      </div>
    
<!-- ================= 预约弹窗 ================= -->
<div class="overlay" id="bookOverlay">
  <div class="modal">
    <div class="modal-head">
      <div>
        <h3 id="bookTitle">预约 · 陈曦</h3>
        <p style="font-size:12px;color:var(--ink-3);margin-top:2px">50 分钟 · 视频咨询</p>
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
      <div style="display:flex;gap:9px;margin-top:22px">
        <button class="btn btn-ghost" style="flex:1" id="bookCancel">取消</button>
        <button class="btn btn-primary" style="flex:1.4" id="bookConfirm">确认预约</button>
      </div>
      <p style="font-size:11px;color:var(--ink-3);margin-top:14px;text-align:center">
        开始前 24 小时可免费取消
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
import { pickList, pickData, setHtml, setText, docCard, dayCard, slotCard, go, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
let counselors = []
let picked = null
let days = []
let dayIdx = 0
let slot = ''

onMounted(async () => {
  days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    return d
  })
  try {
    counselors = pickList(await getCounselorList({ page: 1, page_size: 20 }))
    setHtml(rootEl.value, '[data-list="docs"]', counselors.length
      ? counselors.map(docCard).join('')
      : '<div class="doc"><h4>暂无咨询师</h4></div>')
  } catch (e) {
    toast('咨询师列表加载失败')
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
  setText(rootEl.value, '#bookTitle', '预约 · ' + (picked.name || '咨询师'))
  await renderDays()
  const ov = rootEl.value.querySelector('#bookOverlay')
  if (ov) ov.classList.add('on')
}

async function renderDays() {
  setHtml(rootEl.value, '#days', days.map((d, i) => dayCard(d, i, i === dayIdx)).join(''))
  await renderSlots()
}

async function renderSlots() {
  if (!picked) return
  let list = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00', '18:00']
  try {
    const d = pickData(await getAvailableSlots(picked.id, dateStr(days[dayIdx])))
    const raw = Array.isArray(d) ? d : (d.slots || d.items || [])
    if (raw.length) {
      list = raw.map(x => typeof x === 'string' ? x : (x.time || x.slot || '')).filter(Boolean)
    }
  } catch (e) {
    // 接口不可用时用默认时段
  }
  setHtml(rootEl.value, '#slots', list.map(s => slotCard(s, s === slot)).join(''))
}

async function confirm() {
  if (!picked || !slot) { toast('请先选择日期与时段'); return }
  try {
    await createAppointment({
      counselor_id: picked.id,
      consultation_type: 'video',
      appointment_date: dateStr(days[dayIdx]) + 'T' + slot + ':00'
    })
    toast('预约已提交')
    const ov = rootEl.value.querySelector('#bookOverlay')
    if (ov) ov.classList.remove('on')
  } catch (e) {
    toast('预约失败，请重试')
  }
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const b = e.target.closest('[data-book]')
  if (b) { openBook(b.getAttribute('data-book')); return }
  const d = e.target.closest('[data-day]')
  if (d) { dayIdx = Number(d.getAttribute('data-day')); slot = ''; renderDays(); return }
  const s = e.target.closest('[data-slot]')
  if (s) {
    slot = s.getAttribute('data-slot')
    rootEl.value.querySelectorAll('[data-slot]').forEach(x => x.classList.toggle('on', x === s))
    return
  }
  if (e.target.closest('#bookConfirm')) { confirm(); return }
  if (e.target.closest('#bookClose') || e.target.closest('#bookCancel')) {
    const ov = rootEl.value.querySelector('#bookOverlay')
    if (ov) ov.classList.remove('on')
  }
}

</script>
