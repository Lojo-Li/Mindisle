import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { startTest, submitTest, saveProgress, getProgress, clearProgress } from '@/api/test'
import { pickData, setText, setHtml, optCard, toast } from '../workspace'

const rootEl = ref(null)
const route = useRoute()
const router = useRouter()
let questions = []
let answers = {}
let idx = 0
let title = ''
let saveTimer = null
let leaving = false
let submitting = false
let startedAt = 0
// 补答模式：用户存在漏答时进入，作答后自动跳到下一道未答，直到补齐即提交
let gapMode = false

const CHEV_LEFT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>'
const CLOSE_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'

onMounted(async () => {
  startedAt = Date.now()
  try {
    const d = pickData(await startTest(route.params.id))
    questions = d.questions || []
    title = d.title || '心理测评'
    if (!questions.length) {
      toast('暂无题目')
      router.push('/workspace/assess')
      return
    }

    // 「再测一次」会带 restart=1：必须先把上次的作答彻底清掉，
    // 否则 restore() 会把旧答案填回来，用户看到的是上次勾过的选项。
    if (isRestart()) {
      try { await clearProgress(route.params.id) } catch (e) { /* 无进度也可忽略 */ }
      sessionStorage.removeItem('mindisle_result')
    } else {
      await restore()
    }

    restyleExit()
    ensureQuestionNo()
    ensureActionBar()
    render()
  } catch (e) {
    toast('题目加载失败')
    router.push('/workspace/assess')
  }
})

onBeforeUnmount(() => {
  clearTimeout(saveTimer)
  // 离开页面兜底保存，避免丢进度（提交中/已完成时不再写回）
  if (!leaving && !submitting && Object.keys(answers).length) {
    saveProgress(route.params.id, { answers: buildAnswers() }).catch(() => {})
  }
})

function isRestart() {
  const v = route.query.restart
  return v === '1' || v === 'true'
}

/** 断点续答：把上次的答案填回去，并定位到第一道未答题 */
async function restore() {
  try {
    const p = pickData(await getProgress(route.params.id))
    if (!p || !p.answers) return
    questions.forEach((q, i) => {
      const v = p.answers[q.question_number]
      if (v != null && Number(v) > 0) answers[i] = Number(v)
    })
    const done = Object.keys(answers).length
    if (!done) return
    idx = Math.max(0, Math.min(questions.length - 1, (p.current_question || 1) - 1))
    // 续答时若中间有空洞（如 1,2,5 已答、3,4 缺），直接进入补答模式
    gapMode = hasInternalGap()
    toast('已恢复上次进度（' + done + '/' + questions.length + ' 题）')
  } catch (e) {
    /* 无进度则从头开始 */
  }
}

/**
 * 顶栏左侧图标原本是「<」返回箭头，和「上一题」的「<」完全一样，容易误点。
 * 这里换成「× 退出」，明确它是退出问卷而不是回退一题。
 */
function restyleExit() {
  const root = rootEl.value
  const back = root.querySelector('#quizBack')
  if (!back) return
  back.title = '退出测评（会保存进度）'
  back.style.cssText = [
    'display:inline-flex', 'align-items:center', 'gap:5px',
    'width:auto', 'min-width:0', 'flex:0 0 auto',
    'height:30px', 'padding:0 11px 0 9px', 'border-radius:99px',
    'border:1px solid var(--line)', 'background:var(--surface)',
    'color:var(--ink-3)', 'font-size:12px', 'cursor:pointer',
    'white-space:nowrap'
  ].join(';')
  back.innerHTML = CLOSE_ICON + '<span>退出</span>'
}

/** 题号：每道题上方显示「第 N 题」，并带上量表自身题号 */
function ensureQuestionNo() {
  const root = rootEl.value
  if (!root || root.querySelector('#quizNo')) return
  const anchor = root.querySelector('#quizTitle')
  if (!anchor) return
  const el = document.createElement('div')
  el.id = 'quizNo'
  el.style.cssText = [
    'display:inline-flex', 'align-items:center', 'gap:6px',
    'height:24px', 'padding:0 10px', 'margin-bottom:10px',
    'border-radius:99px', 'background:var(--sea-soft)', 'color:var(--sea-deep)',
    'font-size:11.5px', 'font-weight:600', 'letter-spacing:.3px'
  ].join(';')
  anchor.parentNode.insertBefore(el, anchor)
}

/** 底部操作条：「上一题」放在这里，与顶部的「退出」在位置和样式上都区分开 */
function ensureActionBar() {
  const root = rootEl.value
  if (!root || root.querySelector('#quizActions')) return
  const card = root.querySelector('.quiz-card')
  if (!card || !card.parentNode) return

  const bar = document.createElement('div')
  bar.id = 'quizActions'
  bar.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:16px'
  bar.innerHTML =
    '<button id="quizPrev" type="button" style="display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 14px 0 11px;border-radius:99px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);font-size:12.5px;cursor:pointer;transition:all .18s">' +
    CHEV_LEFT + '<span>上一题</span></button>' +
    '<span id="quizHint" style="font-size:11.5px;color:var(--ink-3)"></span>'
  card.parentNode.insertBefore(bar, card.nextSibling)
}

function buildAnswers() {
  const out = {}
  questions.forEach((q, i) => {
    if (answers[i] != null) out[String(q.question_number || i + 1)] = answers[i]
  })
  return out
}

/** 所有未作答题目的下标 */
function missingIndexes() {
  return questions.map((q, i) => (answers[i] == null ? i : null)).filter(v => v !== null)
}

/**
 * 是否存在「中间空洞」：即已经答到后面，但前面漏了题。
 * 这种状态下作答后应直接跳到下一道未答，而不是逐题往下走。
 */
function hasInternalGap() {
  const miss = missingIndexes()
  if (!miss.length) return false
  const answeredIdx = Object.keys(answers).map(Number)
  if (!answeredIdx.length) return false
  const lastAnswered = Math.max(...answeredIdx)
  return miss.some(i => i < lastAnswered)
}

function persist() {
  clearTimeout(saveTimer)
  if (submitting) return
  saveTimer = setTimeout(() => {
    const payload = buildAnswers()
    if (!Object.keys(payload).length) return
    saveProgress(route.params.id, { answers: payload }).catch(() => {})
  }, 600)
}

function render() {
  const root = rootEl.value
  const q = questions[idx]
  const done = Object.keys(answers).length
  setText(root, '#quizName', title)
  setText(root, '#quizTitle', q.question_text)
  setText(root, '#quizNow', idx + 1)
  setText(root, '#quizTotal', questions.length)

  // 题号徽标
  const no = root.querySelector('#quizNo')
  if (no) {
    const serial = q.question_number || idx + 1
    no.textContent = '第 ' + (idx + 1) + ' 题' + (serial !== idx + 1 ? '（量表题号 ' + serial + '）' : '') + ' / 共 ' + questions.length + ' 题'
  }

  const bar = root.querySelector('#quizBar')
  if (bar) bar.style.width = (done / questions.length * 100) + '%'

  setHtml(root, '[data-list="options"]', (q.options || []).map(optCard).join(''))
  // 回填已选项，便于回上一题时确认
  const chosen = answers[idx]
  if (chosen != null) {
    const el = root.querySelector('[data-opt="' + chosen + '"]')
    if (el) el.classList.add('sel')
  }

  const prev = root.querySelector('#quizPrev')
  if (prev) {
    const first = idx === 0
    prev.disabled = first
    prev.style.opacity = first ? '.35' : '1'
    prev.style.cursor = first ? 'not-allowed' : 'pointer'
  }
  const hint = root.querySelector('#quizHint')
  if (hint) {
    const rest = questions.length - done
    hint.textContent = '已答 ' + done + ' / ' + questions.length + ' 题' +
      (rest > 0 ? ' · 还剩 ' + rest + ' 题' : ' · 答完自动出结果')
  }
}

async function finish() {
  // 后端要求全部作答，缺答会返回 400；这里先拦住并跳到第一道未答。
  // 进入「补答模式」后，每补完一题会自动跳到下一道未答；全部补齐即刻提交，
  // 不需要用户再一题一题翻到最后一题。
  const missing = missingIndexes()
  if (missing.length) {
    gapMode = true
    idx = missing[0]
    render()
    const preview = missing.length > 1 ? `，还有 ${missing.length - 1} 题` : ''
    toast('还有 ' + missing.length + ' 题未作答' + preview)
    return
  }

  // 提交期间禁止再写进度：否则 600ms 防抖可能在「后端已清空进度」之后
  // 把上一次的作答又写回去，导致下次进入被恢复成旧答案。
  submitting = true
  leaving = true
  clearTimeout(saveTimer)

  try {
    const result = pickData(await submitTest(route.params.id, { answers: buildAnswers() }))
    sessionStorage.setItem('mindisle_result', JSON.stringify(result))
    router.push('/workspace/result/' + (result.id || 'latest'))
  } catch (e) {
    submitting = false
    leaving = false
    toast((e && e.response && e.response.data && e.response.data.detail) || '提交失败，请重试')
  }
}

function onClick(e) {
  if (e.target.closest('#quizBack')) {
    leaving = true
    const payload = buildAnswers()
    const done = Object.keys(payload).length
    const leave = () => router.push('/workspace/assess')
    if (done) {
      saveProgress(route.params.id, { answers: payload }).finally(leave)
      toast('进度已保存（' + done + '/' + questions.length + ' 题）')
    } else {
      leave()
    }
    return
  }

  if (e.target.closest('#quizPrev')) {
    if (gapMode) {
      // 补答模式下「上一题」跳到上一道未答题，避免在已答题目里空转
      const prevMiss = missingIndexes().filter(i => i < idx)
      if (prevMiss.length) { idx = prevMiss[prevMiss.length - 1]; render() }
      return
    }
    if (idx > 0) { idx--; render() }
    return
  }

  const o = e.target.closest('[data-opt]')
  if (o) {
    // 记录这道题此前是否已作答：用于区分「补漏」和「回头改答案」
    const wasAnswered = answers[idx] != null
    answers[idx] = Number(o.getAttribute('data-opt'))

    rootEl.value.querySelectorAll('[data-opt]').forEach(x => x.classList.remove('sel'))
    o.classList.add('sel')

    const bar = rootEl.value.querySelector('#quizBar')
    if (bar) bar.style.width = (Object.keys(answers).length / questions.length * 100) + '%'
    persist()

    setTimeout(() => {
      const miss = missingIndexes()

      // 全部答完 → 立刻提交出结果（不管当前停在第几题）
      if (!miss.length) { finish(); return }

      // 补答模式，或这是一道新题：直接跳到下一道未答，跳过已答的
      if (gapMode || !wasAnswered) {
        idx = nextUnanswered(idx)
        render()
        if (gapMode) toast('还剩 ' + miss.length + ' 题，已跳到第 ' + (idx + 1) + ' 题')
        return
      }

      // 普通模式下回头修改一道已答的题：不打扰，停在原地
    }, 220)
  }
}

/** 从当前题往后找第一道未答的题，找不到就从头找（处理"跳着答"的情况） */
function nextUnanswered(from) {
  for (let i = from + 1; i < questions.length; i++) {
    if (answers[i] == null) return i
  }
  for (let i = 0; i < questions.length; i++) {
    if (answers[i] == null) return i
  }
  return from
}
