import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

// 导入全局样式
import '@/styles/common.scss'
import '@/styles/ai-support.css'
['token', 'userInfo', 'userRole', 'adminToken', 'adminInfo'].forEach(key => {
  localStorage.removeItem(key)
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

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
})
