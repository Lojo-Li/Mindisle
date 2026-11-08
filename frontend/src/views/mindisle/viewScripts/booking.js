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
