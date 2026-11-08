/**
 * 从 mindisle.html 生成「心屿工作台」路由级组件（只读设计稿，不修改源文件）。
 * 用法：node frontend/scripts/gen-workspaces.mjs
 *
 * 产物：
 *   views/mindisle/MindisleShell.vue          共享外壳（按角色渲染侧栏）
 *   views/mindisle/views/*.vue                7 个用户视图 + 咨询师工作台
 *
 * 视图模板逐字来自设计稿，只在数据位插入 data-bind / data-list 标记，
 * 由 viewScripts/*.js 里的真实接口数据注入，兼顾「长相一致」与「数据真实」。
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import postcss from 'postcss'

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, '../..')
const base = path.join(root, 'frontend/src/views/mindisle')
const viewsDir = path.join(base, 'views')
const scriptDir = path.join(base, 'viewScripts')

const html = fs.readFileSync(path.join(root, 'prototype/mindisle.html'), 'utf8')
const cssRaw = html.match(/<style>([\s\S]*?)<\/style>/i)[1]
const rawBody = html.match(/<body>([\s\S]*?)<\/body>/i)[1]
const body = rawBody.slice(0, rawBody.indexOf('<script>'))

/* ---------- CSS：作用域前缀，动态 innerHTML 也能命中，且不污染其它页面 ---------- */
const DARK_CSS = `
/* 明暗主题：工作台沿用登录页的夜间配色 */
.mi-portal[data-theme="dark"]{
  --bg:#0C1213; --surface:#182223; --surface-2:#141E1F;
  --ink:#EAF0EE; --ink-2:#A9B9B8; --ink-3:#6F8282;
  --line:#243033; --line-2:#1C2729;
  --sea:#5AA79E; --sea-deep:#7BC2B8; --sea-soft:#1B302E;
  --lamp:#E0AE5A; --lamp-soft:#2A2519; --sand:#1E2422;
  --rose:#D08C82; --rose-soft:#2A1D1C;
  --shadow-s:0 1px 2px rgba(0,0,0,.25);
  --shadow-m:0 1px 2px rgba(0,0,0,.25),0 20px 48px -30px rgba(0,0,0,.8);
  --shadow-l:0 2px 6px rgba(0,0,0,.25),0 24px 56px -24px rgba(0,0,0,.8);
  color-scheme:dark; background:var(--bg); color:var(--ink)
}
.mi-portal[data-theme="dark"] .main,
.mi-portal[data-theme="dark"] .sidebar,
.mi-portal[data-theme="dark"] .topbar,
.mi-portal[data-theme="dark"] .card,
.mi-portal[data-theme="dark"] .stat,
.mi-portal[data-theme="dark"] .scale,
.mi-portal[data-theme="dark"] .doc,
.mi-portal[data-theme="dark"] .chat,
.mi-portal[data-theme="dark"] .sess-list,
.mi-portal[data-theme="dark"] .mood-card,
.mi-portal[data-theme="dark"] .quiz-card,
.mi-portal[data-theme="dark"] .ring-card,
.mi-portal[data-theme="dark"] .modal {
  background:var(--surface); color:var(--ink); border-color:var(--line)
}
.mi-portal[data-theme="dark"] .main{background:var(--bg)}
`

function scopeCss(src) {
  // 设计稿按 html font-size:16px 计算 rem，项目全局把 html 设为 14px 会缩小字号
  const normalizeRem = (raw) => raw.replace(/(-?\d*\.?\d+)rem\b/g, (_, n) => (parseFloat(n) * 16) + 'px')
  let css = normalizeRem(src)
    .replace(/\[data-theme="(dark|light)"\]/g, '.mi-portal[data-theme="$1"]')
    .replace(/^(\s*):root\s*\{/gm, '$1.mi-portal{')
    .replace(/html\s*,\s*body\s*\{[^}]*\}/g, '')
    .replace(/^(\s*)body\s*\{/gm, '$1.mi-portal{')

  const parsed = postcss.parse(css)
  parsed.walkRules(rule => {
    const parent = rule.parent
    if (parent && parent.type === 'atrule' && /keyframes/i.test(parent.name)) return
    rule.selectors = rule.selectors.map(sel => {
      const s = sel.trim()
      if (!s) return s
      if (s.startsWith('.mi-portal')) return s
      if (/^(from|to|\d+%)$/.test(s)) return s
      if (/^::/.test(s)) return s
      return '.mi-portal ' + s
    })
  })

  const isolation = [
    '.mi-portal .card { padding:0; border:0; border-radius:0; box-shadow:none; background:transparent; transition:none; }',
    '.mi-portal .card:hover { transform:none; box-shadow:none; border-color:transparent; }',
    '.mi-portal .avatar { position:relative; }',
    ''
  ].join('\n')
  return isolation + parsed.toString() + DARK_CSS
}

/* ---------- 切出设计稿片段 ---------- */
const bg = body.slice(0, body.indexOf('<div class="app">')).trim()
const overlayStart = body.indexOf('<!-- ================= 预约弹窗 ================= -->')
const toastStart = body.indexOf('<div class="toast"')
const overlayHtml = body.slice(overlayStart, toastStart).trim()
const toastHtml = body.slice(toastStart).trim()

const sections = {}
const re = /<section class="view[^"]*" data-view="([\w-]+)">([\s\S]*?)<\/section>/g
let m
while ((m = re.exec(body))) sections[m[1]] = m[2]

/* ---------- 数据位标记 ---------- */
const RULES = {
  home: [
    ['<h1>下午好，林深</h1>', '<h1 data-bind="greeting">下午好，林深</h1>'],
    ['<span data-count="74">0</span>', '<span data-bind="moodScore">0</span>'],
    ['<span data-count="12">0</span>', '<span data-bind="testCount">0</span>'],
    ['<div class="v" style="font-size:23px">11月12日<small>周三 20:00</small></div>', '<div class="v" style="font-size:23px" data-bind="nextAppointment">11月12日</div>'],
    ['<div class="d">陈曦 · 第 7 次 · 还剩 5 天</div>', '<div class="d" data-bind="nextNote">陈曦 · 第 7 次 · 还剩 5 天</div>']
  ],
  assess: [
    ['<div class="filter-row">', '<div class="filter-row" data-list="filters">'],
    ['<div class="scales">', '<div class="scales" data-list="scales">']
  ],
  'assess-quiz': [
    ['<div class="quiz-opts" id="quizOpts"></div>', '<div class="quiz-opts" id="quizOpts" data-list="options"></div>']
  ],
  'assess-result': [
    ['<div id="dims" style="display:flex;flex-direction:column;gap:15px"></div>', '<div id="dims" data-list="dims" style="display:flex;flex-direction:column;gap:15px"></div>']
  ],
  lamp: [
    ['<div class="sess-list">', '<div class="sess-list" data-list="sessions">']
  ],
  booking: [
    ['<div class="docs">', '<div class="docs" data-list="docs">']
  ],
  records: [
    ['<p>128 天，12 次测评，6 次咨询。变化是慢慢发生的。</p>', '<p data-bind="recordsSummary">128 天，12 次测评，6 次咨询。变化是慢慢发生的。</p>']
  ]
}

function mark(key, inner) {
  let s = inner
  for (const [from, to] of (RULES[key] || [])) s = s.split(from).join(to)
  if (key === 'home') {
    s = s.replace('<div class="tl">', '<div class="tl" data-list="homeTests">')
  }
  if (key === 'records') {
    let n = 0
    s = s.replace(/<div class="tl">/g, () => {
      n += 1
      return '<div class="tl" data-list="' + (n === 1 ? 'testHistory' : 'appointments') + '">'
    })
  }
  if (key === 'booking') s += '\n' + overlayHtml
  return s
}

/* ---------- 共享外壳 ---------- */
const ICONS = {
  home: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z"/></svg>',
  assess: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M9.5 9h5M9.5 13h5M9.5 17h3"/></svg>',
  lamp: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>',
  booking: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/></svg>',
  records: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H19v3H6.5"/></svg>'
}

const shellScript = `import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { mountShellDecorations } from './decorations'

const props = defineProps({ role: { type: String, default: 'user' } })
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const ICONS = ${JSON.stringify(ICONS, null, 2)}

const MENUS = {
  user: [
    { label: '工作台', text: '概览', path: '/workspace/home', icon: ICONS.home },
    { text: '心理测评', path: '/workspace/assess', icon: ICONS.assess },
    { text: '屿灯 · 情绪支持', path: '/workspace/lamp', icon: ICONS.lamp, badge: 'AI' },
    { text: '咨询预约', path: '/workspace/booking', icon: ICONS.booking },
    { label: '我的', text: '我的记录', path: '/workspace/records', icon: ICONS.records }
  ],
  counselor: [
    { label: '咨询师工作台', text: '概览', path: '/counselor/dashboard', icon: ICONS.home },
    { text: '预约订单', path: '/consultation/counselor/orders', icon: ICONS.booking },
    { text: '咨询会话', path: '/chat', icon: ICONS.lamp },
    { label: '我的', text: '个人中心', path: '/profile', icon: ICONS.records }
  ]
}

const menu = computed(() => MENUS[props.role] || MENUS.user)
const crumb = computed(() => route.meta.crumb || '概览')
const nickname = computed(() => {
  const i = userStore.userInfo || {}
  return i.nickname || i.username || '朋友'
})
const initial = computed(() => nickname.value.slice(0, 1))
const roleLabel = computed(() => ({ user: '普通用户', counselor: '咨询师', admin: '管理员' }[props.role] || '普通用户'))

const theme = ref('light')
let disposeDecorations = null

onMounted(() => {
  theme.value = localStorage.getItem('mindisle-theme') === 'dark' ? 'dark' : 'light'
  const host = document.querySelector('.mi-portal')
  if (host) host.setAttribute('data-theme', theme.value)
  disposeDecorations = mountShellDecorations()
})
onUnmounted(() => { if (disposeDecorations) disposeDecorations() })

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('mindisle-theme', theme.value)
  const host = document.querySelector('.mi-portal')
  if (host) host.setAttribute('data-theme', theme.value)
}

function isActive(item) {
  return route.path === item.path || route.path.startsWith(item.path + '/')
}
function navigate(item) { router.push(item.path) }
function doSearch(e) { router.push({ path: '/knowledge', query: { q: e.target.value } }) }
function logout() { userStore.logout() }
`

const shellSfc = `<template>
<div class="mi-portal">
${bg}
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M3 17.5c2.2 0 2.6-3.5 4.8-3.5s2.4 2.4 4.4 2.4 2.5-4.2 4.8-4.2c1.4 0 2.4.9 3 1.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
          <circle cx="16.6" cy="7" r="2.1" fill="#F6D08A"/>
        </svg>
      </div>
      <div class="brand-text"><b>心屿</b><span>Mindisle</span></div>
    </div>

    <nav class="nav">
      <template v-for="(item, i) in menu" :key="item.path + i">
        <div class="nav-label" v-if="item.label">{{ item.label }}</div>
        <button class="nav-item" :class="{ active: isActive(item) }" @click="navigate(item)">
          <span class="nav-ico" v-html="item.icon"></span>{{ item.text }}
          <span class="badge" v-if="item.badge">{{ item.badge }}</span>
        </button>
      </template>
    </nav>

    <div class="sidebar-foot">
      <div class="divider"></div>
      <button class="user-card" @click="router.push('/profile')">
        <div class="avatar av-a">{{ initial }}<i class="mood-pip" id="userMoodPip"></i></div>
        <div class="user-meta"><b>{{ nickname }}</b><span>{{ roleLabel }}</span></div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round" style="margin-left:auto"><path d="M9 6l6 6-6 6"/></svg>
      </button>
    </div>
  </aside>

  <main class="main" id="main">
    <div class="topbar" id="topbar">
      <div class="crumb">心屿<b id="crumbNow">{{ crumb }}</b></div>
      <div class="top-actions">
        <div class="search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/></svg>
          <input placeholder="搜索量表、咨询师…" @keyup.enter="doSearch">
        </div>
        <button class="icon-btn" :title="theme === 'light' ? '切换到夜间' : '切换到日间'" @click="toggleTheme">
          <svg v-if="theme === 'light'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        </button>
        <button class="icon-btn" title="通知" @click="router.push('/notifications')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 8-3 8h18s-3-1-3-8"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>
          <span class="pip"></span>
        </button>
        <button class="icon-btn" title="退出登录" @click="logout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/></svg>
        </button>
      </div>
    </div>
    <router-view />
  </main>
</div>
${toastHtml}
</div>
</template>

<script setup>
${shellScript}
</script>

<style>
${scopeCss(cssRaw)}
</style>
`

/* ---------- 视图组件 ---------- */
const VIEWS = [
  { key: 'home', file: 'OverviewView.vue', script: 'overview.js' },
  { key: 'assess', file: 'AssessmentView.vue', script: 'assessment.js' },
  { key: 'assess-quiz', file: 'QuizView.vue', script: 'quiz.js' },
  { key: 'assess-result', file: 'ResultView.vue', script: 'result.js' },
  { key: 'lamp', file: 'LampView.vue', script: 'lamp.js' },
  { key: 'booking', file: 'BookingView.vue', script: 'booking.js' },
  { key: 'records', file: 'RecordsView.vue', script: 'records.js' }
]

const counselorTpl = `<section class="view active" data-view="counselor" ref="rootEl" @click="onClick">
  <div class="page-head">
    <div>
      <div class="eyebrow">Counselor Workspace</div>
      <h1 data-bind="greeting">你好，咨询师</h1>
      <p>这里是你的咨询工作台。待处理的预约会第一时间出现在这里。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost" data-go="/consultation/counselor/orders">订单详情</button>
  </div>

  <div class="grid-3">
    <div class="stat"><div class="k">全部订单</div><div class="v"><span data-bind="totalOrders">0</span><small>笔</small></div><div class="d">来自真实预约数据</div></div>
    <div class="stat"><div class="k">待处理</div><div class="v"><span data-bind="pendingOrders">0</span><small>笔</small></div><div class="d">需要你确认或拒绝</div></div>
    <div class="stat"><div class="k">已完成</div><div class="v"><span data-bind="doneOrders">0</span><small>笔</small></div><div class="d">已结束的咨询</div></div>
  </div>

  <div class="card card-pad" style="margin-top:20px">
    <div class="card-head"><h3>最近的预约</h3></div>
    <div class="tl" data-list="counselorOrders"></div>
  </div>
</section>`

function sfc(templateBody, scriptText) {
  return `<template>
${templateBody}
</template>

<script setup>
${scriptText}
</script>
`
}

fs.mkdirSync(viewsDir, { recursive: true })
fs.writeFileSync(path.join(base, 'MindisleShell.vue'), shellSfc, 'utf8')

for (const v of VIEWS) {
  const inner = mark(v.key, sections[v.key])
  const scriptText = fs.readFileSync(path.join(scriptDir, v.script), 'utf8')
  const tpl = `<section class="view active" data-view="${v.key}" ref="rootEl" @click="onClick">\n${inner}\n</section>`
  fs.writeFileSync(path.join(viewsDir, v.file), sfc(tpl, scriptText), 'utf8')
  console.log('generated:', v.file)
}

fs.writeFileSync(
  path.join(viewsDir, 'CounselorOverview.vue'),
  sfc(counselorTpl, fs.readFileSync(path.join(scriptDir, 'counselor.js'), 'utf8')),
  'utf8'
)
console.log('generated: MindisleShell.vue, CounselorOverview.vue')
