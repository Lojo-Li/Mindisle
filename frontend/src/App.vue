<template>
  <div id="app">
    <PageHeader v-if="showHeader" />
    <router-view />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'

const route = useRoute()

// 路由是否已完成首次解析。未解析时 route.meta 为空对象，
// 若此时按 !hideHeader 判断会误显示旧导航栏，因此先不渲染。
const routeReady = ref(false)
onMounted(() => { routeReady.value = true })

const showHeader = computed(() => routeReady.value && !route.meta.hideHeader)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 14px;
  line-height: 1.6;
  color: #1B2A2C;
  background-color: #F6F5F1;
  min-height: 100vh;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #DDDAD1;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb:hover {
  background: #C9C5BA;
}
</style>
