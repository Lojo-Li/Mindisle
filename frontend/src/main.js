import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

// 导入全局样式（心屿界面所需，首屏必须）
import '@/styles/common.scss'
import '@/styles/ai-support.css'

['token', 'userInfo', 'userRole', 'adminToken', 'adminInfo'].forEach(key => {
  localStorage.removeItem(key)
})

const app = createApp(App)
app.use(createPinia())
app.use(router)

/**
 * Element Plus 延迟加载
 *
 * 原来在 main.js 顶部 import ElementPlus + index.css 再 app.use() 全量注册，
 * 导致 element-plus.js（约 1MB）与 index.css（约 340KB）必然进入首屏，
 * 云端带宽约 0.3MB/s，光静态资源就要等近 4 秒。
 *
 * 心屿新版界面（落地页、登录、/workspace、/counselor/dashboard）基本不用它，
 * 使用者主要是旧版页面与 /admin 后台。因此：
 * - 心屿路由不等 Element Plus，首屏立刻可见
 * - 进入其他路由前由守卫 await 完成注册
 */
let elementPlusReady = null

/** 动态注入 Element Plus 样式，避免被打进入口 CSS */
function loadElementPlusCss() {
  return new Promise((resolve) => {
    if (document.getElementById('ep-styles')) {
      resolve(true)
      return
    }
    const link = document.createElement('link')
    link.id = 'ep-styles'
    link.rel = 'stylesheet'
    link.href = '/ep.css'
    link.onload = () => resolve(true)
    link.onerror = () => resolve(false)
    document.head.appendChild(link)
  })
}

export function ensureElementPlus() {
  if (!elementPlusReady) {
    elementPlusReady = Promise.all([
      import('element-plus'),
      import('element-plus/es/locale/lang/zh-cn'),
      import('@element-plus/icons-vue'),
      loadElementPlusCss()
    ]).then(([ep, zhCn, icons]) => {
      app.use(ep.default, { locale: zhCn.default })
      for (const [key, component] of Object.entries(icons)) {
        app.component(key, component)
      }
      return true
    }).catch((e) => {
      console.error('[element-plus] 加载失败', e)
      elementPlusReady = null
      return false
    })
  }
  return elementPlusReady
}

window.__ensureElementPlus = ensureElementPlus

/**
 * 这些路由使用 Element Plus（旧版页面、后台、聊天页的 ElMessage），
 * 进入前必须确保已就绪；其余心屿页面直接放行。
 */
const NEEDS_EP_PREFIXES = ['/admin', '/consultation', '/counselor/', '/profile', '/knowledge']
const NEEDS_EP_EXACT = ['/workspace/chat', '/counselor/dashboard/chat']

function needsElementPlus(path) {
  if (NEEDS_EP_EXACT.some((p) => path.startsWith(p))) return true
  return NEEDS_EP_PREFIXES.some((p) => path.startsWith(p))
}

router.beforeResolve(async (to) => {
  if (needsElementPlus(to.path)) {
    await ensureElementPlus()
  }
  return true
})

/**
 * 等路由首次解析完成再挂载。
 *
 * 直接 mount 的话，首帧 route.meta 还是空的，App.vue 里
 * `showHeader = !route.meta.hideHeader` 会算成 true，
 * 于是旧版 PageHeader 先闪一下，等路由就绪才被移除——
 * 刷新 / 或退出登录时会看到「旧导航栏一闪而过」。
 */
router.isReady().then(() => {
  app.mount('#app')
  // 心屿页面空闲时后台预取，点进旧版/后台时无需等待
  const idle = window.requestIdleCallback || ((cb) => setTimeout(cb, 2000))
  idle(() => { ensureElementPlus() })
})
