import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestHistory } from '@/api/test'
import { getUserAppointments } from '@/api/counselor'
import { pickList, setHtml, setText, testTl, apptTl, go } from '../workspace'

const rootEl = ref(null)
const router = useRouter()

onMounted(async () => {
  try {
    const [h, a] = await Promise.all([
      getTestHistory({ page: 1, page_size: 20 }),
      getUserAppointments({ page: 1, page_size: 20 })
    ])
    const tests = pickList(h)
    const appts = pickList(a)
    setText(rootEl.value, '[data-bind="recordsSummary"]',
      tests.length + ' 次测评，' + appts.length + ' 次咨询。变化是慢慢发生的。')
    setHtml(rootEl.value, '[data-list="testHistory"]', tests.length
      ? tests.map(testTl).join('')
      : '<div class="tl-item"><b>还没有测评记录</b></div>')
    setHtml(rootEl.value, '[data-list="appointments"]', appts.length
      ? appts.map(apptTl).join('')
      : '<div class="tl-item"><b>还没有咨询记录</b></div>')
  } catch (e) {
    // 接口不可用时保留设计稿静态内容
  }
})

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}
