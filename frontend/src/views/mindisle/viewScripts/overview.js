import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserStatistics } from '@/api/user'
import { getTestHistory } from '@/api/test'
import { getUserAppointments } from '@/api/counselor'
import { useUserStore } from '@/stores/user'
import { pickList, pickData, setText, setHtml, fmtDate, testTl, go, statusText } from '../workspace'
import { mountOverviewDecorations, animateNumber } from '../decorations'

const rootEl = ref(null)
const router = useRouter()
const userStore = useUserStore()
let disposeDecorations = null

function greeting() {
  const h = new Date().getHours()
  return h < 11 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
}

onMounted(async () => {
  const root = rootEl.value
  const info = userStore.userInfo || {}
  setText(root, '[data-bind="greeting"]', greeting() + '，' + (info.nickname || info.username || '朋友'))
  disposeDecorations = mountOverviewDecorations(root)
  try {
    const [s, h, a] = await Promise.all([
      getUserStatistics(),
      getTestHistory({ page: 1, page_size: 5 }),
      getUserAppointments({ page: 1, page_size: 10 })
    ])
    const st = pickData(s)
    animateNumber(root.querySelector('[data-bind="testCount"]'), st.test_count ?? 0)
    animateNumber(root.querySelector('[data-bind="moodScore"]'),
      st.test_count ? Math.min(100, 60 + st.test_count * 2) : 0)
    const tests = pickList(h)
    setHtml(root, '[data-list="homeTests"]', tests.length
      ? tests.map(testTl).join('')
      : '<div class="tl-item"><b>还没有测评记录</b></div>')
    const appts = pickList(a)
    const next = appts.find(x => ['pending', 'confirmed', 'in_progress'].includes(x.status))
    setText(root, '[data-bind="nextAppointment"]', next ? fmtDate(next.appointment_date) : '暂无安排')
    setText(root, '[data-bind="nextNote"]', next
      ? ((next.counselor && next.counselor.name) || '咨询师') + ' · ' + statusText(next.status)
      : '去预约一次咨询吧')
  } catch (e) {
    // 接口不可用时保留设计稿静态内容
  }
})

onUnmounted(() => { if (disposeDecorations) disposeDecorations() })

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}
