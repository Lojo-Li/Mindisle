/**
 * 从两个设计稿 HTML 生成 Vue SFC（只读设计稿，不修改源文件）。
 * 用法：node frontend/scripts/gen-mindisle.mjs
 *
 * 设计稿更新后重新执行即可同步；生成物为：
 *   frontend/src/views/mindisle/LandingPage.vue  （登录落地页）
 *   frontend/src/views/mindisle/PortalPage.vue    （用户工作台）
 *
 * 关键点：CSS 用「作用域类前缀」而非 scoped，这样 innerHTML 动态创建的
 * 元素（逐字标题、答题选项、聊天气泡等）也能命中样式，且不会污染其它页面。
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import postcss from 'postcss'

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, '../..')
const outDir = path.join(root, 'frontend/src/views/mindisle')

const TARGETS = [
  { file: 'prototype/mindisle-home.html', out: 'LandingPage.vue', scope: 'mi-landing', landing: true },
  { file: 'prototype/mindisle.html', out: 'PortalPage.vue', scope: 'mi-portal', landing: false }
]

const helpers = `  const listeners = []
  const timers = []
  let rafId = null
  function winOn(t, f, o) { window.addEventListener(t, f, o); listeners.push(['window', t, f, o]) }
  function docOn(t, f, o) { document.addEventListener(t, f, o); listeners.push(['document', t, f, o]) }
  function trackTimeout(f, ms) { const id = setTimeout(f, ms); timers.push(id); return id }
  function trackInterval(f, ms) { const id = setInterval(f, ms); timers.push(id); return id }
`

const destroyFn = `
  return function destroy() {
    if (rafId != null) cancelAnimationFrame(rafId)
    timers.forEach(id => { clearTimeout(id); clearInterval(id) })
    listeners.forEach(l => {
      const target = l[0] === 'window' ? window : document
      target.removeEventListener(l[1], l[2], l[3])
    })
  }
`

/** 把作用于 html/body/:root 的规则收敛到组件根节点，并给其余选择器加作用域前缀 */
function scopeCss(cssRaw, scope) {
  // 设计稿按 html font-size:16px 计算 rem，而项目全局把 html 设为 14px，
  // 会把 clamp() 大标题缩小。这里换算成 px，保证与原稿字号完全一致。
  const normalizeRem = (src) => src.replace(/(-?\d*\.?\d+)rem\b/g, (_, n) => (parseFloat(n) * 16) + 'px')
  let css = normalizeRem(cssRaw)
    .replace(/\[data-theme="(dark|light)"\]/g, `.${scope}[data-theme="$1"]`)
    .replace(/^(\s*):root\s*\{/gm, `$1.${scope}{`)
    .replace(/html\s*,\s*body\s*\{[^}]*\}/g, '')
    .replace(/^(\s*)body\s*\{/gm, `$1.${scope}{`)

  const parsed = postcss.parse(css)
  parsed.walkRules(rule => {
    const parent = rule.parent
    if (parent && parent.type === 'atrule' && /keyframes/i.test(parent.name)) return
    rule.selectors = rule.selectors.map(sel => {
      const s = sel.trim()
      if (!s) return s
      if (s.startsWith(`.${scope}`)) return s
      if (/^(from|to|\d+%)$/.test(s)) return s
      if (/^::/.test(s)) return s
      return `.${scope} ${s}`
    })
  })

  // 全局 common.scss 定义了 .card；先中和，设计稿自身的 .card 声明位于其后
  // 且优先级相同，会正常覆盖这些占位值。
  const isolation = [
    `.${scope} .card { padding:0; border:0; border-radius:0; box-shadow:none; background:transparent; transition:none; }`,
    `.${scope} .card:hover { transform:none; box-shadow:none; border-color:transparent; }`,
    ''
  ].join('\n')

  return isolation + parsed.toString()
}

/** 把 IIFE 改成可挂载、可清理的函数，并给登录页注入真实业务回调 */
function scopeJs(jsRaw, isLanding) {
  let js = jsRaw.trim()
  js = js
    .replace(/window\.addEventListener\(/g, 'winOn(')
    .replace(/document\.addEventListener\(/g, 'docOn(')
    .replace(/document\.querySelectorAll\(/g, 'rootEl.querySelectorAll(')
    .replace(/document\.documentElement/g, 'rootEl')
    .replace(/setInterval\(/g, 'trackInterval(')
    .replace(/setTimeout\(/g, 'trackTimeout(')
    .replace(/requestAnimationFrame\(([^)]*)\)/g, 'rafId = requestAnimationFrame($1)')

  if (isLanding) {
    js = js.replace(
      'if(validate(account, pwd, m.label2)) toast(m.ok);',
      `if(validate(account, pwd, m.label2)){
    if(typeof loginHandler === 'function'){ loginHandler({ account: account.value.trim(), password: pwd.value, portal: portalMode }); }
    else { toast(m.ok); }
  }`
    )
    js = js.replace(
      "toast(ACTS[t.getAttribute('data-act')]);",
      `var act = t.getAttribute('data-act');
  if(typeof navigate === 'function' && navigate(act)) return;
  toast(ACTS[act]);`
    )
  }

  return js
    .replace(/^\s*\(function\(\)\s*\{/, `function mountLanding(rootEl, loginHandler, navigate) {\n${helpers}`)
    .replace(/\}\)\(\);\s*$/, `${destroyFn}}`)
}

function build(target) {
  const html = fs.readFileSync(path.join(root, target.file), 'utf8')
  const cssRaw = html.match(/<style>([\s\S]*?)<\/style>/i)[1]
  const bodyRaw = html.match(/<body>([\s\S]*?)<\/body>/i)[1]
  const jsRaw = html.match(/<script>([\s\S]*?)<\/script>/i)[1]

  const tpl = bodyRaw.replace(/<script>[\s\S]*?<\/script>/gi, '').trim()
  const css = scopeCss(cssRaw, target.scope)
  const js = scopeJs(jsRaw, target.landing)

  const themeAttr = target.landing ? ' data-theme="light"' : ''

  const sfc = `<template>
  <div class="${target.scope}"${themeAttr} ref="rootEl">
${tpl}
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  loginHandler: { type: Function, default: null },
  navigate: { type: Function, default: null }
})

const rootEl = ref(null)
let cleanup = null

${js}

onMounted(() => { cleanup = mountLanding(rootEl.value, props.loginHandler, props.navigate) })
onUnmounted(() => { if (cleanup) { cleanup(); cleanup = null } })
</script>

<style>
${css}
</style>
`

  const out = path.join(outDir, target.out)
  fs.writeFileSync(out, sfc, 'utf8')
  console.log('generated:', target.out, sfc.length, 'chars')
}

fs.mkdirSync(outDir, { recursive: true })
TARGETS.forEach(build)
