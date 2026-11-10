import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestList } from '@/api/test'
import { setHtml, scaleCard, filterPill, go, toast, esc } from '../workspace'

const rootEl = ref(null)
const router = useRouter()

const CAT_LABEL = {
  anxiety: '焦虑', depression: '抑郁', personality: '人格',
  stress: '压力', emotion: '情绪', sleep: '睡眠', career: '职业', other: '其他'
}

const state = {
  page: 1,
  pageSize: 30,
  total: 0,
  all: [],
  cat: '全部',
  keyword: '',
  sort: 'latest',
  loading: false
}

const catLabel = c => (c === '全部' ? '全部' : CAT_LABEL[c] || c)

onMounted(async () => {
  injectToolbar()
  await load(true)
})

async function load(reset) {
  if (state.loading) return
  state.loading = true
  try {
    const res = await getTestList({
      page: reset ? 1 : state.page,
      page_size: state.pageSize,
      sort: state.sort,
      keyword: state.keyword || undefined
    })
    const body = (res && res.data) || {}
    const items = body.items || []
    state.total = body.total || items.length
    state.all = reset ? items : state.all.concat(items)
    state.page = reset ? 1 : state.page
    renderFilters()
    render()
  } catch (e) {
    toast('量表列表加载失败')
  } finally {
    state.loading = false
  }
}

function injectToolbar() {
  const root = rootEl.value
  const box = root.querySelector('[data-list="scales"]')
  if (!box || !box.parentNode || root.querySelector('#scaleToolbar')) return

  const bar = document.createElement('div')
  bar.id = 'scaleToolbar'
  bar.style.cssText = 'display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px'
  bar.innerHTML =
    '<input id="scaleSearch" placeholder="搜索量表名称" style="flex:1;min-width:180px;height:34px;padding:0 12px;border:1px solid var(--line);border-radius:10px;font-size:12.5px;outline:none" />' +
    '<div id="scaleSort" style="display:inline-flex;gap:4px;padding:3px;border-radius:99px;background:var(--surface-2,#f4f2ee);border:1px solid var(--line)">' +
    '<button data-sort="latest" style="border:none;background:transparent;border-radius:99px;padding:5px 14px;font-size:12px;cursor:pointer;transition:all .18s">最新</button>' +
    '<button data-sort="hot" style="border:none;background:transparent;border-radius:99px;padding:5px 14px;font-size:12px;cursor:pointer;transition:all .18s">最热</button>' +
    '</div>'
  box.parentNode.insertBefore(bar, box)

  // 结果摘要行：让点击排序后立刻有文字层面的反馈
  const tip = document.createElement('div')
  tip.id = 'scaleSummary'
  tip.style.cssText = 'font-size:11.5px;color:var(--ink-3);margin-bottom:12px'
  tip.textContent = '加载中…'
  bar.parentNode.insertBefore(tip, bar.nextSibling)

  let timer = null
  const input = bar.querySelector('#scaleSearch')
  input.value = state.keyword
  input.addEventListener('input', () => {
    clearTimeout(timer)
    timer = setTimeout(async () => {
      state.keyword = input.value.trim()
      await load(true)
    }, 300)
  })

  bar.addEventListener('click', async (ev) => {
    const s = ev.target.closest('[data-sort]')
    if (!s) return
    const next = s.getAttribute('data-sort')
    if (next === state.sort && state.all.length) return
    state.sort = next
    syncSortButtons()
    await load(true)
  })
  syncSortButtons()
}

function syncSortButtons() {
  const root = rootEl.value
  root.querySelectorAll('[data-sort]').forEach(b => {
    const on = b.getAttribute('data-sort') === state.sort
    b.style.background = on ? 'var(--sea)' : 'transparent'
    b.style.color = on ? '#fff' : 'var(--ink-2)'
    b.style.fontWeight = on ? '600' : '400'
    b.style.boxShadow = on ? '0 1px 4px rgba(46,110,104,.28)' : 'none'
  })
}

function updateSummary() {
  const root = rootEl.value
  const tip = root.querySelector('#scaleSummary')
  if (!tip) return
  const shown = state.cat === '全部' ? state.all.length : state.all.filter(t => t.category === state.cat).length
  const sortText = state.sort === 'hot' ? '最热优先' : '最新发布'
  tip.textContent = '共 ' + state.total + ' 个量表' +
    (state.keyword ? ' · 匹配「' + state.keyword + '」' : '') +
    ' · 按' + sortText +
    (shown !== state.total ? ' · 当前显示 ' + shown + ' 个' : '')
}

function renderFilters() {
  const root = rootEl.value
  const cats = ['全部'].concat(Array.from(new Set(state.all.map(t => t.category).filter(Boolean))))
  const box = root.querySelector('[data-list="filters"]')
  if (!box) return
  setHtml(root, '[data-list="filters"]', cats.map(c =>
    filterPill(catLabel(c), c === state.cat).replace('data-filter="' + esc(catLabel(c)) + '"',
      'data-filter="' + esc(c) + '"')
  ).join(''))
}

function render() {
  const root = rootEl.value
  const list = state.cat === '全部' ? state.all : state.all.filter(t => t.category === state.cat)
  setHtml(root, '[data-list="scales"]', list.length
    ? list.map(scaleCard).join('')
    : '<div class="scale"><h4>暂无量表</h4><p>换个分类或关键词试试</p></div>')

  // 重新渲染后给一个轻微淡入，避免"点了没变化"的错觉
  const host = root.querySelector('[data-list="scales"]')
  if (host) {
    host.style.opacity = '0'
    host.style.transform = 'translateY(4px)'
    host.style.transition = 'opacity .18s ease, transform .18s ease'
    requestAnimationFrame(() => {
      host.style.opacity = '1'
      host.style.transform = 'translateY(0)'
    })
  }

  // 加载更多
  const old = root.querySelector('#scaleMore')
  if (old) old.remove()
  if (state.all.length && state.all.length < state.total) {
    const more = document.createElement('button')
    more.id = 'scaleMore'
    more.textContent = '加载更多（已显示 ' + state.all.length + ' / ' + state.total + '）'
    more.style.cssText = 'margin:16px auto 0;display:block;border:1px solid var(--line);background:#fff;border-radius:99px;padding:7px 18px;font-size:12px;cursor:pointer'
    const host2 = root.querySelector('[data-list="scales"]')
    if (host2 && host2.parentNode) host2.parentNode.insertBefore(more, host2.nextSibling)
    more.addEventListener('click', async () => {
      state.page += 1
      await load(false)
    })
  }

  syncSortButtons()
  updateSummary()
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const p = e.target.closest('[data-filter]')
  if (p) {
    state.cat = p.getAttribute('data-filter')
    rootEl.value.querySelectorAll('[data-filter]').forEach(x => x.classList.toggle('on', x === p))
    render()
    return
  }
  const s = e.target.closest('[data-start]')
  if (s) router.push('/workspace/quiz/' + s.getAttribute('data-start'))
}
