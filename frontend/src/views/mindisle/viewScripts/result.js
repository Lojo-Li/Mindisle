import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTestResult, favoriteResult, unfavoriteResult, clearProgress } from '@/api/test'
import { pickData, setText, setHtml, dimCard, go, toast, esc } from '../workspace'

const rootEl = ref(null)
const route = useRoute()
const router = useRouter()
let current = null

onMounted(async () => {
  let d = null
  const id = route.params.id

  // 仅在缓存与 URL 指向同一条结果时才用缓存，避免串号
  const cached = sessionStorage.getItem('mindisle_result')
  if (cached) {
    try {
      const c = JSON.parse(cached)
      if (id === 'latest' || String(c.id) === String(id)) d = c
    } catch (e) { d = null }
  }

  if (!d && id !== 'latest') {
    try {
      d = pickData(await getTestResult(id))
    } catch (e) {
      d = null
    }
  }
  if (!d || !d.id) {
    toast('暂无结果')
    router.push('/workspace/records')
    return
  }

  current = d
  const root = rootEl.value
  const interp = d.interpretation || null
  const level = (interp && interp.level) || {}
  const levelLabel = level.label || d.result_title || d.result_level || '已完成'

  setText(root, '#resScore', d.total_score ?? 0)
  setText(root, '#resMax', d.max_score || 100)
  setText(root, '#resLevel', levelLabel)
  setText(root, '#resSummary', level.summary || d.result_description || d.ai_suggestion || '')

  const stroke = root.querySelector('#ringStroke')
  if (stroke) {
    const max = Number(d.max_score || 100) || 100
    const ratio = Math.min(1, Number(d.total_score || 0) / max)
    stroke.style.strokeDashoffset = String(389.6 * (1 - ratio))
  }

  const dims = d.dimension_scores || []
  setHtml(root, '[data-list="dims"]', dims.length
    ? dims.map(dimCard).join('')
    : '<div style="font-size:12px;color:var(--ink-3)">暂无维度数据</div>')

  // 维度标题不再写死「四个维度」
  const dimTitle = Array.from(root.querySelectorAll('.card-head h3'))
    .find(el => el.textContent.indexOf('维度') >= 0)
  if (dimTitle) dimTitle.textContent = dims.length ? dims.length + ' 个维度' : '维度'

  renderSignal(root, interp && interp.signal)
  renderAdvice(root, interp && interp.advice)
  renderActions(root, d)
  renderTrace(root, d, interp)
})

function renderSignal(root, signal) {
  if (!signal || !signal.text) return
  let box = root.querySelector('#resSignalBox')
  if (!box) {
    const summary = root.querySelector('#resSummary')
    if (!summary) return
    box = document.createElement('div')
    box.id = 'resSignalBox'
    box.style.cssText = 'margin-top:12px;padding:10px 12px;border:1px solid #EFE4CE;border-radius:12px;background:#FDF9F0'
    box.innerHTML = '<b id="resSignalTitle" style="display:block;font-size:12px;margin-bottom:4px"></b>' +
      '<span id="resSignal" style="font-size:12px;color:var(--ink-2);line-height:1.75"></span>'
    summary.parentNode.insertBefore(box, summary.nextSibling)
  }
  setText(root, '#resSignalTitle', signal.title || '')
  setText(root, '#resSignal', signal.text)
  box.style.borderColor = signal.level === 'prompt' ? '#E3B4AE' : signal.level === 'watch' ? '#EFE4CE' : '#CFE0DD'
  box.style.background = signal.level === 'prompt' ? '#FBEFED' : signal.level === 'watch' ? '#FDF9F0' : '#F0F7F5'
}

function renderAdvice(root, advice) {
  if (!advice) return
  const items = [].concat(advice.today || [], advice.week || [], advice.professional || [])
  if (!items.length) return
  const card = Array.from(root.querySelectorAll('.card'))
    .find(c => c.textContent.indexOf('接下来可以做什么') >= 0)
  const ul = card && card.querySelector('ul')
  if (!ul) return
  ul.innerHTML = items
    .map(t => '<li style="display:flex;gap:8px"><span style="color:var(--sea)">·</span>' + esc(t) + '</li>')
    .join('')
}

function renderActions(root, d) {
  if (root.querySelector('#resActions')) return
  const back = root.querySelector('[data-go="assess"]')
  if (!back) return
  const wrap = document.createElement('div')
  wrap.id = 'resActions'
  wrap.style.cssText = 'display:inline-flex;gap:8px;margin-left:8px'
  wrap.innerHTML =
    '<button class="btn btn-ghost" id="resAgain">再测一次</button>' +
    '<button class="btn btn-ghost" id="resFav">' + (d.is_favorite ? '已收藏' : '收藏') + '</button>'
  back.parentNode.insertBefore(wrap, back.nextSibling)

  wrap.querySelector('#resAgain').addEventListener('click', async () => {
    if (!d.test_id) return
    // restart=1 让答题页先清空上一次的作答进度，保证从一份空白问卷开始
    sessionStorage.removeItem('mindisle_result')
    try { await clearProgress(d.test_id) } catch (e) { /* 无进度时忽略 */ }
    router.push('/workspace/quiz/' + d.test_id + '?restart=1')
  })
  wrap.querySelector('#resFav').addEventListener('click', async (ev) => {
    const btn = ev.currentTarget
    try {
      if (btn.textContent === '已收藏') {
        await unfavoriteResult(d.id)
        btn.textContent = '收藏'
      } else {
        await favoriteResult(d.id)
        btn.textContent = '已收藏'
      }
    } catch (e) {
      toast('操作失败')
    }
  })
}

/** 评分明细：原始作答 + 等级阈值命中 + 追溯说明 */
function renderTrace(root, d, interp) {
  if (root.querySelector('#traceCard')) return
  const dimsCard = (root.querySelector('[data-list="dims"]') || {}).closest
    ? root.querySelector('[data-list="dims"]').closest('.card')
    : null
  const host = dimsCard ? dimsCard.parentNode : root.querySelector('.stack') || root
  if (!host) return

  const answers = d.answers || {}
  const keys = Object.keys(answers).map(Number).filter(n => !isNaN(n)).sort((a, b) => a - b)
  const trace = (interp && interp.trace) || {}
  const thresholds = trace.thresholds || []
  const notes = trace.notes || []
  const reverse = (d.scoring_rules && d.scoring_rules.reverse_questions) || []

  const card = document.createElement('div')
  card.id = 'traceCard'
  card.className = 'card card-pad'
  card.style.marginTop = '16px'
  card.innerHTML =
    '<div class="card-head"><h3>评分明细</h3>' +
    '<span style="font-size:11.5px;color:var(--ink-3);margin-left:auto;cursor:pointer" id="traceToggle">展开</span></div>' +
    '<div id="traceBody" style="display:none">' +
    '<div id="traceMeta" style="font-size:12px;color:var(--ink-2);line-height:1.9"></div>' +
    '<div id="traceGrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(56px,1fr));gap:6px;margin-top:12px"></div>' +
    '<div id="traceLevels" style="margin-top:14px"></div>' +
    '<div id="traceNotes" style="margin-top:10px;font-size:11px;color:var(--ink-3);line-height:1.8"></div>' +
    '</div>'
  host.appendChild(card)

  setText(card, '#traceMeta',
    '共 ' + (d.total_questions || keys.length) + ' 题 · ' + (d.option_type || '4选项') +
    (reverse.length ? ' · 含 ' + reverse.length + ' 道反向题（已折算）' : '') +
    ' · 计分方式：' + (d.score_type === 'dimension' ? '维度分合计' : '总分求和'))

  if (keys.length) {
    setHtml(card, '#traceGrid', keys.map(k =>
      '<div style="display:flex;justify-content:space-between;padding:6px 8px;border:1px solid var(--line-2);border-radius:8px;font-size:11.5px">' +
      '<span style="color:var(--ink-3)">' + k + '</span><b style="color:var(--sea-deep)">' + esc(answers[k]) + '</b></div>'
    ).join(''))
  } else {
    setHtml(card, '#traceGrid', '<div style="font-size:11.5px;color:var(--ink-3)">该结果未记录原始作答</div>')
  }

  if (thresholds.length) {
    setHtml(card, '#traceLevels', thresholds.map(t =>
      '<div style="display:flex;gap:12px;align-items:center;padding:8px 12px;border-radius:8px;font-size:12px;margin-bottom:4px;' +
      (t.matched ? 'background:#F0F7F5;border:1px solid rgba(46,110,104,.35);color:var(--sea-deep);font-weight:600'
                 : 'border:1px solid var(--line-2);color:var(--ink-3)') + '">' +
      '<span style="flex:0 0 88px">' + esc(t.label || t.code) + '</span>' +
      '<span style="flex:1">' + (t.min ?? '—') + ' – ' + (t.max ?? '—') + '</span>' +
      (t.matched ? '<span style="font-size:10.5px">命中</span>' : '') +
      '</div>'
    ).join(''))
  }

  if (notes.length) {
    setHtml(card, '#traceNotes', notes.map(n => '<div>· ' + esc(n) + '</div>').join(''))
  }

  const toggle = card.querySelector('#traceToggle')
  const body = card.querySelector('#traceBody')
  if (toggle && body) {
    toggle.addEventListener('click', () => {
      const open = body.style.display !== 'none'
      body.style.display = open ? 'none' : 'block'
      toggle.textContent = open ? '展开' : '收起'
    })
  }
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
}
