import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { startTest, submitTest } from '@/api/test'
import { pickData, setText, setHtml, optCard, toast } from '../workspace'

const rootEl = ref(null)
const route = useRoute()
const router = useRouter()
let questions = []
let answers = {}
let idx = 0
let title = ''

onMounted(async () => {
  try {
    const d = pickData(await startTest(route.params.id))
    questions = d.questions || []
    title = d.title || '心理测评'
    if (!questions.length) {
      toast('暂无题目')
      router.push('/workspace/assess')
      return
    }
    render()
  } catch (e) {
    toast('题目加载失败')
    router.push('/workspace/assess')
  }
})

function render() {
  const root = rootEl.value
  const q = questions[idx]
  setText(root, '#quizName', title)
  setText(root, '#quizTitle', q.question_text)
  setText(root, '#quizNow', idx + 1)
  setText(root, '#quizTotal', questions.length)
  const bar = root.querySelector('#quizBar')
  if (bar) bar.style.width = ((idx + 1) / questions.length * 100) + '%'
  setHtml(root, '[data-list="options"]', (q.options || []).map(optCard).join(''))
}

async function finish() {
  const answersByNumber = {}
  questions.forEach((q, i) => {
    answersByNumber[String(q.question_number || (i + 1))] = answers[i] ?? 0
  })
  try {
    const result = pickData(await submitTest(route.params.id, { answers: answersByNumber }))
    sessionStorage.setItem('mindisle_result', JSON.stringify(result))
    router.push('/workspace/result/' + (result.id || 'latest'))
  } catch (e) {
    toast('提交失败，请重试')
  }
}

function onClick(e) {
  if (e.target.closest('#quizBack')) { router.push('/workspace/assess'); return }
  const o = e.target.closest('[data-opt]')
  if (o) {
    answers[idx] = Number(o.getAttribute('data-opt'))
    rootEl.value.querySelectorAll('[data-opt]').forEach(x => x.classList.remove('sel'))
    o.classList.add('sel')
    setTimeout(() => {
      if (idx < questions.length - 1) { idx++; render() } else finish()
    }, 220)
  }
}
