<template>
<section class="view active" data-view="assess-quiz" ref="rootEl" @click="onClick">

      <div class="quiz-shell">
        <div class="quiz-top">
          <button class="icon-btn" id="quizBack" title="退出">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
          </button>
          <div class="quiz-progress"><i id="quizBar"></i></div>
          <div class="quiz-count"><span id="quizNow">1</span> / <span id="quizTotal">9</span></div>
        </div>
        <div class="quiz-card">
          <div class="quiz-q" id="quizName">PHQ-9 · 情绪状态</div>
          <div class="quiz-title" id="quizTitle">—</div>
          <div class="quiz-opts" id="quizOpts" data-list="options"></div>
        </div>
        <p style="text-align:center;font-size:12px;color:var(--ink-3);margin-top:18px">
          没有对错，选最接近「最近两周」真实感受的那一个就好。
        </p>
      </div>
    
</section>
</template>

<script setup>
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

</script>
