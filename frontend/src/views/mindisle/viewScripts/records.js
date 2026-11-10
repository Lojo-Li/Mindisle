import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestHistory, deleteTestResult, favoriteResult, unfavoriteResult } from '@/api/test'
import { getUserAppointments } from '@/api/counselor'
import { pickList, setHtml, setText, testTl, apptTl, go, toast, esc } from '../workspace'

const rootEl = ref(null)
const router = useRouter()

const LEVELS = [
  { key: '', label: '全部等级' },
  { key: 'none', label: '平稳' },
  { key: 'mild', label: '轻度' },
  { key: 'moderate', label: '中度' },
  { key: 'severe', label: '偏重' }
]

const state = { page: 1, pageSize: 10, total: 0, testId: '', level: '', favOnly: false, tests: [] }

onMounted(refresh)

async function refresh() {
  const root = rootEl.value
  try {
    const params = { page: state.page, page_size: state.pageSize }
    if (state.testId) params.test_id = state.testId
    if (state.level) params.level = state.level
    if (state.favOnly) params.favorite_only = true

    const [h, a] = await Promise.all([
      getTestHistory(params),
      getUserAppointments({ page: 1, page_size: 20 })
    ])
    const body = (h && h.data) || {}
    state.tests = body.items || []
    state.total = body.total || 0

    const appts = pickList(a)
    setText(root, '[data-bind="recordsSummary"]',
      state.total + ' 次测评，' + appts.length + ' 次咨询。变化是慢慢发生的。')
    setHtml(root, '[data-list="appointments"]', appts.length
      ? appts.map(apptTl).join('')
      : '<div class="tl-item"><b>还没有咨询记录</b></div>')

    renderList()
    renderFilters()
    renderPager()
  } catch (e) {
    toast('记录加载失败')
  }
}

function renderList() {
  const root = rootEl.value
  const box = root.querySelector('[data-list="testHistory"]')
  if (!box) return

  setHtml(root, '[data-list="testHistory"]', state.tests.length
    ? state.tests.map(testTl).join('')
    : '<div class="tl-item"><b>还没有符合条件的记录</b></div>')

  // 每条记录补「收藏 / 删除」，不影响点击进详情
  box.querySelectorAll('.tl-item[data-go]').forEach(el => {
    const id = (el.getAttribute('data-go') || '').split('/').pop()
    const rec = state.tests.find(t => String(t.id) === String(id))
    if (!rec) return
    el.style.position = 'relative'
    const ops = document.createElement('span')
    ops.style.cssText = 'position:absolute;right:0;top:0;display:flex;gap:8px'
    ops.innerHTML =
      '<button data-act="fav" data-id="' + id + '" style="border:none;background:none;cursor:pointer;font-size:11px;color:var(--sea)">' +
      (rec.is_favorite ? '已收藏' : '收藏') + '</button>' +
      '<button data-act="del" data-id="' + id + '" style="border:none;background:none;cursor:pointer;font-size:11px;color:var(--ink-3)">删除</button>'
    el.appendChild(ops)
  })
}

function renderFilters() {
  const root = rootEl.value
  const old = root.querySelector('#recordFilters')
  if (old) old.remove()
  const box = root.querySelector('[data-list="testHistory"]')
  if (!box || !box.parentNode) return

  const pill = (text, on, attr) =>
    '<button ' + attr + ' style="border:1px solid ' + (on ? 'var(--sea)' : 'var(--line)') +
    ';background:' + (on ? 'var(--sea-soft)' : '#fff') + ';color:' + (on ? 'var(--sea-deep)' : 'var(--ink-2)') +
    ';border-radius:99px;padding:3px 11px;font-size:11.5px;cursor:pointer">' + esc(text) + '</button>'

  const bar = document.createElement('div')
  bar.id = 'recordFilters'
  bar.style.cssText = 'display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:10px'
  bar.innerHTML =
    LEVELS.map(l => pill(l.label, state.level === l.key, 'data-level="' + l.key + '"')).join('') +
    pill(state.favOnly ? '只看收藏 ✓' : '只看收藏', state.favOnly, 'data-fav="1"')
  box.parentNode.insertBefore(bar, box)

  bar.addEventListener('click', async (ev) => {
    const lv = ev.target.closest('[data-level]')
    if (lv) { state.level = lv.getAttribute('data-level'); state.page = 1; await refresh(); return }
    if (ev.target.closest('[data-fav]')) { state.favOnly = !state.favOnly; state.page = 1; await refresh() }
  })
}

function renderPager() {
  const root = rootEl.value
  const old = root.querySelector('#recordPager')
  if (old) old.remove()
  const pages = Math.max(1, Math.ceil(state.total / state.pageSize))
  if (pages <= 1) return
  const box = root.querySelector('[data-list="testHistory"]')
  if (!box || !box.parentNode) return

  const pager = document.createElement('div')
  pager.id = 'recordPager'
  pager.style.cssText = 'display:flex;justify-content:center;align-items:center;gap:12px;margin-top:14px;font-size:12px;color:var(--ink-3)'
  pager.innerHTML =
    '<button data-page="prev"' + (state.page <= 1 ? ' disabled' : '') +
    ' style="border:1px solid var(--line);background:#fff;border-radius:99px;padding:4px 12px;cursor:pointer">上一页</button>' +
    '<span>' + state.page + ' / ' + pages + '</span>' +
    '<button data-page="next"' + (state.page >= pages ? ' disabled' : '') +
    ' style="border:1px solid var(--line);background:#fff;border-radius:99px;padding:4px 12px;cursor:pointer">下一页</button>'
  box.parentNode.appendChild(pager)

  pager.addEventListener('click', async (ev) => {
    const b = ev.target.closest('[data-page]')
    if (!b || b.disabled) return
    state.page += b.getAttribute('data-page') === 'next' ? 1 : -1
    await refresh()
  })
}

async function onAction(act, id) {
  const rec = state.tests.find(t => String(t.id) === String(id))
  try {
    if (act === 'fav') {
      if (rec && rec.is_favorite) { await unfavoriteResult(id); toast('已取消收藏') }
      else { await favoriteResult(id); toast('已收藏') }
      await refresh()
    } else if (act === 'del') {
      if (!window.confirm('删除后该记录不再显示，确定删除吗？')) return
      await deleteTestResult(id)
      toast('已删除')
      if (state.tests.length === 1 && state.page > 1) state.page -= 1
      await refresh()
    }
  } catch (e) {
    toast('操作失败')
  }
}

function onClick(e) {
  const act = e.target.closest('[data-act]')
  if (act) {
    e.stopPropagation()
    onAction(act.getAttribute('data-act'), act.getAttribute('data-id'))
    return
  }
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}
