import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTestResult } from '@/api/test'
import { pickData, setText, setHtml, dimCard, go, toast } from '../workspace'

const rootEl = ref(null)
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  let d = null
  const cached = sessionStorage.getItem('mindisle_result')
  if (cached) {
    try { d = JSON.parse(cached) } catch (e) { d = null }
  }
  if (!d && route.params.id !== 'latest') {
    try { d = pickData(await getTestResult(route.params.id)) } catch (e) { d = null }
  }
  if (!d) {
    toast('暂无结果')
    router.push('/workspace/records')
    return
  }
  const root = rootEl.value
  setText(root, '#resScore', d.total_score ?? 0)
  setText(root, '#resMax', d.max_score || 100)
  setText(root, '#resLevel', d.result_level || d.result_title || '已完成')
  setText(root, '#resSummary', d.result_description || d.ai_suggestion || '')
  const stroke = root.querySelector('#ringStroke')
  if (stroke) {
    const max = Number(d.max_score || 100) || 100
    const ratio = Math.min(1, Number(d.total_score || 0) / max)
    stroke.style.strokeDashoffset = String(389.6 * (1 - ratio))
  }
  setHtml(root, '[data-list="dims"]', (d.dimension_scores || []).length
    ? d.dimension_scores.map(dimCard).join('')
    : '<div style="font-size:12px;color:var(--ink-3)">暂无维度数据</div>')
})

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}
