import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 后端地址优先级：shell 环境变量 > .env.local/.env 中的 VITE_PROXY_TARGET > 默认 8000
  // 本机 8000 可能被 Windows 保留端口段占用，此时在 frontend/.env.local 里配置实际端口即可
  const env = loadEnv(mode, process.cwd(), '')
  const API_TARGET = process.env.VITE_PROXY_TARGET || env.VITE_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      // 关闭 modulepreload 注入：Element Plus 是异步块，
      // 默认会被写进 <link rel="modulepreload">，浏览器仍会立刻下载 1MB，
      // 首屏优化就白做了。
      modulePreload: false
    },
    server: {
      host: '0.0.0.0', // 允许通过IP地址访问
      port: 5173,
      strictPort: false, // 如果端口被占用，自动尝试下一个
      proxy: {
        '/api': {
          target: API_TARGET,
          changeOrigin: true
        },
        '/uploads': {
          target: API_TARGET,
          changeOrigin: true
        }
      }
    },
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios', 'element-plus'],
      exclude: []
    },
    build: {
      // 减少打包体积
      chunkSizeWarningLimit: 1500,
      rollupOptions: {
        output: {
          manualChunks: {
            // 注意：不要再把 element-plus 强制分块。
            // 强制分块会让 Rollup 在入口就静态引用该 chunk，
            // 于是它出现在 index.html 的 modulepreload 里，首屏照旧下载 1MB。
            // 保持默认行为，它才会作为动态 import 的异步块按需加载。
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            'echarts': ['echarts', 'vue-echarts']
          }
        }
      }
    }
  }
})
