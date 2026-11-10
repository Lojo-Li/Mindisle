<template>
<div class="mi-portal">
<div class="ripple-bg" aria-hidden="true">
  <svg class="rb-texture" width="100%" height="100%">
    <defs>
      <pattern id="waveTile" width="168" height="72" patternUnits="userSpaceOnUse">
        <path d="M0,18 Q42,8 84,18 T168,18" fill="none" stroke="#2E6E68" stroke-width="1" opacity=".055"/>
        <path d="M0,50 Q42,40 84,50 T168,50" fill="none" stroke="#2E6E68" stroke-width="1" opacity=".032"/>
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#waveTile)"/>
  </svg>
  <svg class="rb-rings" viewBox="0 0 640 640">
    <circle cx="320" cy="320" r="70"/><circle cx="320" cy="320" r="120"/>
    <circle cx="320" cy="320" r="172"/><circle cx="320" cy="320" r="226"/>
    <circle cx="320" cy="320" r="282"/><circle class="core" cx="320" cy="320" r="4.5"/>
  </svg>
  <svg class="rb-rings-2" viewBox="0 0 340 340">
    <circle cx="170" cy="170" r="46"/><circle cx="170" cy="170" r="88"/>
    <circle cx="170" cy="170" r="132"/><circle cx="170" cy="170" r="178"/>
  </svg>
  <svg class="rb-waves" viewBox="0 0 1200 210" preserveAspectRatio="none">
    <path d="M0,80 Q75,52 150,80 T300,80 T450,80 T600,80 T750,80 T900,80 T1050,80 T1200,80"/>
    <path d="M0,130 Q75,104 150,130 T300,130 T450,130 T600,130 T750,130 T900,130 T1050,130 T1200,130"/>
  </svg>
</div>
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
        <div class="nav-label" v-if="item.showLabel">{{ item.label }}</div>
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
<div class="toast" id="toast">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#8FD8C9" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
  <span id="toastText">已完成</span>
</div>
</div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { mountShellDecorations } from './decorations'

const props = defineProps({ role: { type: String, default: 'user' } })
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const ICONS = {
  "home": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z\"/></svg>",
  "assess": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z\"/><path d=\"M9.5 9h5M9.5 13h5M9.5 17h3\"/></svg>",
  "lamp": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M9 18h6M10 21h4\"/><path d=\"M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z\"/></svg>",
  "booking": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3.5\" y=\"5\" width=\"17\" height=\"15.5\" rx=\"2.5\"/><path d=\"M8 3v4M16 3v4M3.5 10h17\"/></svg>",
  "records": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5z\"/><path d=\"M4 20.5A2.5 2.5 0 0 1 6.5 18H19v3H6.5\"/></svg>",
  "trend": "<svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 4v15.5a.5.5 0 0 0 .5.5H20\"/><path d=\"M7 15l3.5-4 3 2.5L19 8\"/></svg>"
}

const MENUS = {
  user: [
    { label: '工作台', text: '概览', path: '/workspace/home', icon: ICONS.home },
    { text: '心理测评', path: '/workspace/assess', icon: ICONS.assess },
    { text: '屿灯 · 情绪支持', path: '/workspace/lamp', icon: ICONS.lamp, badge: 'AI' },
    { text: '咨询预约', path: '/workspace/booking', icon: ICONS.booking },
    { label: '我的', text: '我的记录', path: '/workspace/records', icon: ICONS.records },
    { text: '测评趋势', path: '/workspace/trend', icon: ICONS.trend }
  ],
  counselor: [
    { label: '咨询师工作台', text: '概览', path: '/counselor/dashboard', icon: ICONS.home },
    { text: '预约订单', path: '/consultation/counselor/orders', icon: ICONS.booking },
    { text: '咨询会话', path: '/chat', icon: ICONS.lamp },
    { label: '我的', text: '个人中心', path: '/profile', icon: ICONS.records }
  ]
}

// 分组标题只在「该组第一条」渲染一次。
// 之前 我的记录 / 测评趋势 两条都写了 label:'我的'，就会在侧栏出现两个「我的」。
// 这里统一做去重，数据里重复写也不会再重复显示。
const menu = computed(() => {
  let lastLabel = null
  return (MENUS[props.role] || MENUS.user).map((it) => {
    const showLabel = !!it.label && it.label !== lastLabel
    if (it.label) lastLabel = it.label
    return { ...it, showLabel }
  })
})
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

</script>

<style>
.mi-portal .card { padding:0; border:0; border-radius:0; box-shadow:none; background:transparent; transition:none; }
.mi-portal .card:hover { transform:none; box-shadow:none; border-color:transparent; }
.mi-portal .avatar { position:relative; }

  .mi-portal{
    --bg:#F6F5F1;
    --surface:#FFFFFF;
    --surface-2:#FBFAF7;
    --ink:#1B2A2C;
    --ink-2:#56696D;
    --ink-3:#94A4A6;
    --line:#E7E5DE;
    --line-2:#EFEDE6;
    --sea:#2E6E68;
    --sea-deep:#22524E;
    --sea-soft:#E2EFEC;
    --lamp:#D9982F;
    --lamp-soft:#FAEFD7;
    --sand:#F1EBE0;
    --rose:#C4746A;
    --rose-soft:#F7E7E4;
    --shadow-s:0 1px 2px rgba(27,42,44,.05);
    --shadow-m:0 1px 2px rgba(27,42,44,.04), 0 10px 28px -14px rgba(27,42,44,.18);
    --shadow-l:0 2px 6px rgba(27,42,44,.05), 0 24px 56px -24px rgba(27,42,44,.28);
    --ease:cubic-bezier(.2,.8,.2,1);
  }
  .mi-portal *{box-sizing:border-box;margin:0;padding:0}
  
  .mi-portal{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
    background:var(--bg);color:var(--ink);font-size:14px;line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  .mi-portal button{font-family:inherit;cursor:pointer;border:none;background:none;color:inherit;font-size:inherit}
  .mi-portal input{font-family:inherit;font-size:inherit;border:none;outline:none;background:none;color:inherit}
  ::-webkit-scrollbar{width:8px;height:8px}
  ::-webkit-scrollbar-thumb{background:#DDDAD1;border-radius:8px}
  ::-webkit-scrollbar-thumb:hover{background:#C9C5BA}
  ::-webkit-scrollbar-track{background:transparent}

  .mi-portal .app{display:flex;height:100vh;overflow:hidden}

  /* ---------- 侧栏 ---------- */
  .mi-portal .sidebar{
    width:250px;flex:0 0 250px;background:var(--surface);
    border-right:1px solid var(--line);
    display:flex;flex-direction:column;padding:22px 16px 16px;
  }
  .mi-portal .brand{display:flex;align-items:center;gap:11px;padding:2px 8px 24px}
  .mi-portal .brand-mark{
    width:38px;height:38px;border-radius:13px;flex:0 0 38px;
    background:linear-gradient(150deg,#3B837C,#22524E);
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 6px 16px -8px rgba(46,110,104,.9);
  }
  .mi-portal .brand-text b{display:block;font-size:16px;font-weight:650;letter-spacing:2px;line-height:1.3}
  .mi-portal .brand-text span{display:block;font-size:10.5px;color:var(--ink-3);letter-spacing:1.6px;text-transform:uppercase}

  .mi-portal .nav{display:flex;flex-direction:column;gap:2px}
  .mi-portal .nav-label{font-size:11px;color:var(--ink-3);letter-spacing:1.2px;padding:14px 12px 6px}
  .mi-portal .nav-item{
    display:flex;align-items:center;gap:11px;
    padding:10px 12px;border-radius:11px;
    color:var(--ink-2);font-size:13.5px;position:relative;
    transition:background .22s var(--ease),color .22s var(--ease);
    text-align:left;width:100%;
  }
  .mi-portal .nav-item svg{flex:0 0 18px;opacity:.75;transition:opacity .22s}
  .mi-portal .nav-item:hover{background:var(--surface-2);color:var(--ink)}
  .mi-portal .nav-item.active{background:var(--sea-soft);color:var(--sea-deep);font-weight:560}
  .mi-portal .nav-item.active svg{opacity:1}
  .mi-portal .nav-item.active::before{
    content:"";position:absolute;left:-16px;top:50%;transform:translateY(-50%);
    width:3px;height:18px;border-radius:0 3px 3px 0;background:var(--sea);
  }
  .mi-portal .nav-item .badge{
    margin-left:auto;font-size:10.5px;background:var(--lamp);color:#fff;
    padding:1px 6px;border-radius:20px;font-weight:600;letter-spacing:.3px;
  }

  .mi-portal .sidebar-foot{margin-top:auto;padding-top:14px}
  .mi-portal .divider{height:1px;background:var(--line-2);margin:0 8px 14px}
  .mi-portal .user-card{
    display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:13px;
    transition:background .2s var(--ease);cursor:pointer;width:100%;text-align:left;
  }
  .mi-portal .user-card:hover{background:var(--surface-2)}
  .mi-portal .avatar{
    width:34px;height:34px;border-radius:11px;flex:0 0 34px;
    display:flex;align-items:center;justify-content:center;
    font-size:13px;font-weight:600;color:#fff;letter-spacing:.5px;
  }
  .mi-portal .av-a{background:linear-gradient(140deg,#6E9E96,#2E6E68)}
  .mi-portal .av-b{background:linear-gradient(140deg,#C9A277,#9C7448)}
  .mi-portal .av-c{background:linear-gradient(140deg,#8E9BB8,#5B6A8C)}
  .mi-portal .av-d{background:linear-gradient(140deg,#C08E93,#96575F)}
  .mi-portal .user-meta{min-width:0}
  .mi-portal .user-meta b{display:block;font-size:13px;font-weight:560;line-height:1.4}
  .mi-portal .user-meta span{display:block;font-size:11px;color:var(--ink-3)}

  /* ---------- 主区 ---------- */
  .mi-portal .main{flex:1;min-width:0;overflow-y:auto;overflow-x:hidden;position:relative}
  .mi-portal .topbar{
    position:sticky;top:0;z-index:30;
    height:60px;display:flex;align-items:center;gap:16px;padding:0 34px;
    background:rgba(246,245,241,.86);backdrop-filter:blur(14px);
    border-bottom:1px solid transparent;transition:border-color .3s;
  }
  .mi-portal .topbar.scrolled{border-bottom-color:var(--line)}
  .mi-portal .crumb{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ink-3)}
  .mi-portal .crumb b{color:var(--ink);font-weight:560}
  .mi-portal .top-actions{margin-left:auto;display:flex;align-items:center;gap:8px}
  .mi-portal .search{
    display:flex;align-items:center;gap:8px;height:34px;padding:0 12px;
    background:var(--surface);border:1px solid var(--line);border-radius:10px;
    width:210px;transition:border-color .2s,box-shadow .2s;
  }
  .mi-portal .search:focus-within{border-color:#C3D8D4;box-shadow:0 0 0 3px rgba(46,110,104,.08)}
  .mi-portal .search input{width:100%;font-size:12.5px}
  .mi-portal .search input::placeholder{color:var(--ink-3)}
  .mi-portal .icon-btn{
    width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;
    color:var(--ink-2);border:1px solid var(--line);background:var(--surface);position:relative;
    transition:.2s var(--ease);
  }
  .mi-portal .icon-btn:hover{background:var(--surface);color:var(--ink);box-shadow:var(--shadow-s)}
  .mi-portal .icon-btn .pip{position:absolute;top:7px;right:8px;width:6px;height:6px;border-radius:50%;background:var(--lamp);border:1.5px solid #fff}

  .mi-portal .view{display:none;padding:8px 34px 64px;animation:rise .42s var(--ease)}
  .mi-portal .view.active{display:block}
  @keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

  /* ---------- 通用 ---------- */
  .mi-portal .page-head{display:flex;align-items:flex-end;gap:20px;padding:20px 0 26px;flex-wrap:wrap}
  .mi-portal .page-head h1{font-size:27px;font-weight:640;letter-spacing:.2px;line-height:1.35}
  .mi-portal .page-head p{color:var(--ink-2);font-size:13.5px;margin-top:5px;max-width:560px}
  .mi-portal .page-head .spacer{margin-left:auto}
  .mi-portal .eyebrow{font-size:11px;letter-spacing:2px;color:var(--sea);text-transform:uppercase;font-weight:600;margin-bottom:8px}

  .mi-portal .btn{
    display:inline-flex;align-items:center;justify-content:center;gap:7px;
    height:38px;padding:0 17px;border-radius:11px;font-size:13.5px;font-weight:540;
    transition:.22s var(--ease);white-space:nowrap;
  }
  .mi-portal .btn-primary{background:linear-gradient(160deg,#357B74,#22524E);color:#fff;box-shadow:0 8px 20px -12px rgba(34,82,78,.9)}
  .mi-portal .btn-primary:hover{transform:translateY(-1px);box-shadow:0 12px 26px -12px rgba(34,82,78,.85)}
  .mi-portal .btn-ghost{background:var(--surface);border:1px solid var(--line);color:var(--ink-2)}
  .mi-portal .btn-ghost:hover{border-color:#CFDCD9;color:var(--ink);box-shadow:var(--shadow-s)}
  .mi-portal .btn-soft{background:var(--sea-soft);color:var(--sea-deep)}
  .mi-portal .btn-soft:hover{background:#D6E8E4}
  .mi-portal .btn-sm{height:32px;padding:0 13px;font-size:12.5px;border-radius:9px}

  .mi-portal .card{background:var(--surface);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow-s)}
  .mi-portal .card-pad{padding:22px}
  .mi-portal .card-head{display:flex;align-items:center;gap:10px;margin-bottom:18px}
  .mi-portal .card-head h3{font-size:14.5px;font-weight:590;letter-spacing:.2px}
  .mi-portal .card-head .more{margin-left:auto;font-size:12px;color:var(--ink-3);display:flex;align-items:center;gap:4px;transition:color .2s}
  .mi-portal .card-head .more:hover{color:var(--sea)}

  .mi-portal .grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  .mi-portal .grid-2{display:grid;grid-template-columns:1.55fr 1fr;gap:16px;margin-top:16px}
  .mi-portal .stack{display:flex;flex-direction:column;gap:16px}

  /* ---------- 数据卡 ---------- */
  .mi-portal .stat{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px 20px 18px;position:relative;overflow:hidden;box-shadow:var(--shadow-s);transition:.28s var(--ease)}
  .mi-portal .stat:hover{box-shadow:var(--shadow-m);transform:translateY(-2px)}
  .mi-portal .stat .k{font-size:12px;color:var(--ink-3);display:flex;align-items:center;gap:6px;letter-spacing:.3px}
  .mi-portal .stat .v{font-size:31px;font-weight:640;letter-spacing:-.5px;margin-top:8px;line-height:1.15}
  .mi-portal .stat .v small{font-size:13px;font-weight:500;color:var(--ink-3);margin-left:3px;letter-spacing:0}
  .mi-portal .stat .d{font-size:11.5px;margin-top:6px;color:var(--ink-3);display:flex;align-items:center;gap:5px}
  .mi-portal .trend-up{color:var(--sea);font-weight:600}
  .mi-portal .trend-flat{color:var(--lamp);font-weight:600}
  .mi-portal .stat .glow{position:absolute;right:-24px;top:-24px;width:96px;height:96px;border-radius:50%;background:radial-gradient(circle,rgba(46,110,104,.10),transparent 70%)}

  /* ---------- 测评卡 ---------- */
  .mi-portal .scales{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:16px}
  .mi-portal .scale{
    background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;
    box-shadow:var(--shadow-s);cursor:pointer;position:relative;overflow:hidden;
    transition:.28s var(--ease);display:flex;flex-direction:column;min-height:186px;
  }
  .mi-portal .scale:hover{transform:translateY(-3px);box-shadow:var(--shadow-m);border-color:#D8E4E1}
  .mi-portal .scale:hover .go-arrow{background:var(--sea);color:#fff;transform:translateX(2px)}
  .mi-portal .tag{display:inline-flex;align-items:center;font-size:11px;padding:2.5px 9px;border-radius:20px;background:var(--sand);color:#8A7A62;letter-spacing:.3px;font-weight:520}
  .mi-portal .tag.sea{background:var(--sea-soft);color:var(--sea-deep)}
  .mi-portal .tag.lamp{background:var(--lamp-soft);color:#8F6316}
  .mi-portal .tag.rose{background:var(--rose-soft);color:#96574E}
  .mi-portal .scale h4{font-size:15.5px;font-weight:600;margin:12px 0 6px;letter-spacing:.2px}
  .mi-portal .scale p{font-size:12.5px;color:var(--ink-2);line-height:1.65;flex:1}
  .mi-portal .scale-foot{display:flex;align-items:center;gap:10px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line-2);font-size:11.5px;color:var(--ink-3)}
  .mi-portal .scale-foot .go-arrow{
    margin-left:auto;width:26px;height:26px;border-radius:8px;background:var(--surface-2);
    display:flex;align-items:center;justify-content:center;color:var(--ink-2);transition:.25s var(--ease);
  }

  /* ---------- 潮汐图 ---------- */
  .mi-portal .tide-wrap{padding:6px 4px 0}
  .mi-portal .tide-legend{display:flex;gap:18px;font-size:11.5px;color:var(--ink-3);margin-top:12px;padding-left:4px}
  .mi-portal .tide-legend i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}

  /* ---------- 时间线 ---------- */
  .mi-portal .tl{position:relative;padding-left:26px}
  .mi-portal .tl::before{content:"";position:absolute;left:5px;top:8px;bottom:10px;width:1.5px;background:linear-gradient(180deg,var(--sea-soft),var(--line-2))}
  .mi-portal .tl-item{position:relative;padding-bottom:18px}
  .mi-portal .tl-item:last-child{padding-bottom:0}
  .mi-portal .tl-item::before{
    content:"";position:absolute;left:-25px;top:6px;width:9px;height:9px;border-radius:50%;
    background:#fff;border:2px solid #CFDDD9;
  }
  .mi-portal .tl-item.now::before{border-color:var(--sea);background:var(--sea);box-shadow:0 0 0 4px rgba(46,110,104,.12)}
  .mi-portal .tl-item b{font-size:13px;font-weight:560;display:block}
  .mi-portal .tl-item span{font-size:11.5px;color:var(--ink-3)}

  /* ---------- 答题 ---------- */
  .mi-portal .quiz-shell{max-width:760px;margin:0 auto;padding-top:24px}
  .mi-portal .quiz-top{display:flex;align-items:center;gap:14px;margin-bottom:26px}
  .mi-portal .quiz-progress{flex:1;height:4px;border-radius:4px;background:var(--line-2);overflow:hidden}
  .mi-portal .quiz-progress i{display:block;height:100%;width:0;border-radius:4px;background:linear-gradient(90deg,#4C918A,#22524E);transition:width .45s var(--ease)}
  .mi-portal .quiz-count{font-size:12px;color:var(--ink-3);font-variant-numeric:tabular-nums;letter-spacing:.5px}
  .mi-portal .quiz-card{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:40px 40px 34px;box-shadow:var(--shadow-m)}
  .mi-portal .quiz-q{font-size:12px;color:var(--sea);letter-spacing:1.5px;font-weight:600;margin-bottom:14px}
  .mi-portal .quiz-title{font-size:21px;font-weight:580;line-height:1.55;letter-spacing:.2px;margin-bottom:28px}
  .mi-portal .quiz-opts{display:flex;flex-direction:column;gap:9px}
  .mi-portal .opt{
    display:flex;align-items:center;gap:12px;padding:14px 18px;border-radius:13px;
    border:1px solid var(--line);background:var(--surface-2);text-align:left;width:100%;
    font-size:14px;color:var(--ink-2);transition:.2s var(--ease);
  }
  .mi-portal .opt:hover{border-color:#C6DAD6;background:var(--sea-soft);color:var(--sea-deep);transform:translateX(2px)}
  .mi-portal .opt .radio{width:17px;height:17px;border-radius:50%;border:1.5px solid #CFCEC6;flex:0 0 17px;transition:.2s;position:relative}
  .mi-portal .opt:hover .radio{border-color:var(--sea)}
  .mi-portal .opt.sel{border-color:var(--sea);background:var(--sea-soft);color:var(--sea-deep);font-weight:520}
  .mi-portal .opt.sel .radio{border-color:var(--sea);background:var(--sea)}
  .mi-portal .opt.sel .radio::after{content:"";position:absolute;inset:4px;border-radius:50%;background:#fff}

  /* ---------- 结果 ---------- */
  .mi-portal .result-grid{display:grid;grid-template-columns:300px 1fr;gap:20px;align-items:start}
  .mi-portal .ring-card{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:30px 24px;text-align:center;box-shadow:var(--shadow-m)}
  .mi-portal .ring{position:relative;width:150px;height:150px;margin:0 auto 6px}
  .mi-portal .ring svg{transform:rotate(-90deg)}
  .mi-portal .ring .num{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
  .mi-portal .ring .num b{font-size:34px;font-weight:640;letter-spacing:-1px;line-height:1}
  .mi-portal .ring .num span{font-size:11px;color:var(--ink-3);margin-top:4px;letter-spacing:1px}
  .mi-portal .level-pill{display:inline-flex;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:.5px}

  /* ---------- 屿灯 ---------- */
  .mi-portal .lamp-shell{display:grid;grid-template-columns:230px 1fr;gap:16px;height:calc(100vh - 132px);min-height:520px}
  .mi-portal .sess-list{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:14px 10px;overflow-y:auto}
  .mi-portal .sess-label{font-size:11px;color:var(--ink-3);letter-spacing:1px;padding:8px 10px 6px}
  .mi-portal .sess{
    padding:10px 11px;border-radius:11px;cursor:pointer;transition:.2s var(--ease);margin-bottom:2px;
  }
  .mi-portal .sess:hover{background:var(--surface-2)}
  .mi-portal .sess.active{background:var(--sea-soft)}
  .mi-portal .sess b{display:block;font-size:12.5px;font-weight:530;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .mi-portal .sess span{display:block;font-size:11px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

  .mi-portal .chat{background:var(--surface);border:1px solid var(--line);border-radius:18px;display:flex;flex-direction:column;overflow:hidden}
  .mi-portal .chat-head{display:flex;align-items:center;gap:12px;padding:15px 20px;border-bottom:1px solid var(--line-2)}
  .mi-portal .lamp-ava{
    width:36px;height:36px;border-radius:12px;background:radial-gradient(circle at 50% 38%,#FBE2AC,#E0A44B 62%,#C08A32);
    display:flex;align-items:center;justify-content:center;box-shadow:0 0 18px -4px rgba(224,164,75,.75)
  }
  .mi-portal .chat-head h4{font-size:13.5px;font-weight:570;line-height:1.4}
  .mi-portal .chat-head span{font-size:11px;color:var(--sea);display:flex;align-items:center;gap:4px}
  .mi-portal .chat-head span i{width:5px;height:5px;border-radius:50%;background:var(--sea);display:inline-block}

  .mi-portal .chat-body{flex:1;overflow-y:auto;padding:24px 22px;display:flex;flex-direction:column;gap:16px;background:
    radial-gradient(1200px 300px at 50% -8%,rgba(226,239,236,.5),transparent 70%)}
  .mi-portal .msg{display:flex;gap:10px;max-width:78%;animation:pop .35s var(--ease)}
  @keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
  .mi-portal .msg.me{margin-left:auto;flex-direction:row-reverse}
  .mi-portal .bubble{padding:11px 15px;border-radius:15px;font-size:13.5px;line-height:1.75;white-space:pre-wrap}
  .mi-portal .msg.ai .bubble{background:var(--surface-2);border:1px solid var(--line-2);border-top-left-radius:5px}
  .mi-portal .msg.me .bubble{background:linear-gradient(160deg,#357B74,#2A625D);color:#fff;border-top-right-radius:5px}
  .mi-portal .msg .mini{width:28px;height:28px;border-radius:9px;flex:0 0 28px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#fff}
  .mi-portal .msg.ai .mini{background:radial-gradient(circle at 50% 35%,#FBE2AC,#DEA248)}
  .mi-portal .msg.me .mini{background:linear-gradient(140deg,#6E9E96,#2E6E68)}
  .mi-portal .typing{display:flex;gap:4px;padding:14px 16px}
  .mi-portal .typing i{width:5px;height:5px;border-radius:50%;background:#B9C6C4;animation:blink 1.3s infinite}
  .mi-portal .typing i:nth-child(2){animation-delay:.18s}
  .mi-portal .typing i:nth-child(3){animation-delay:.36s}
  @keyframes blink{0%,60%,100%{opacity:.3;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}

  .mi-portal .chat-foot{padding:14px 18px 16px;border-top:1px solid var(--line-2);background:var(--surface)}
  .mi-portal .chips{display:flex;gap:7px;margin-bottom:11px;flex-wrap:wrap}
  .mi-portal .chip{font-size:11.5px;padding:4.5px 11px;border-radius:20px;border:1px solid var(--line);color:var(--ink-2);background:var(--surface-2);transition:.2s}
  .mi-portal .chip:hover{border-color:#C6DAD6;background:var(--sea-soft);color:var(--sea-deep)}
  .mi-portal .composer{display:flex;align-items:flex-end;gap:10px;background:var(--surface-2);border:1px solid var(--line);border-radius:14px;padding:8px 8px 8px 14px;transition:border-color .2s,box-shadow .2s}
  .mi-portal .composer:focus-within{border-color:#C3D8D4;box-shadow:0 0 0 3px rgba(46,110,104,.07)}
  .mi-portal .composer input{flex:1;padding:6px 0;font-size:13.5px}
  .mi-portal .composer input::placeholder{color:var(--ink-3)}
  .mi-portal .send{width:32px;height:32px;border-radius:10px;background:var(--sea);color:#fff;display:flex;align-items:center;justify-content:center;transition:.2s}
  .mi-portal .send:hover{background:var(--sea-deep)}

  /* ---------- 咨询师 ---------- */
  .mi-portal .docs{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}
  .mi-portal .doc{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:var(--shadow-s);transition:.28s var(--ease)}
  .mi-portal .doc:hover{box-shadow:var(--shadow-m);transform:translateY(-2px)}
  .mi-portal .doc-top{display:flex;gap:13px;align-items:flex-start}
  .mi-portal .doc .avatar{width:48px;height:48px;flex:0 0 48px;border-radius:15px;font-size:16px}
  .mi-portal .doc-top h4{font-size:15px;font-weight:600;display:flex;align-items:center;gap:7px}
  .mi-portal .doc-top .sub{font-size:11.5px;color:var(--ink-3);margin-top:2px}
  .mi-portal .doc-tags{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0 12px}
  .mi-portal .doc-meta{display:flex;align-items:center;gap:12px;padding-top:13px;border-top:1px solid var(--line-2);font-size:11.5px;color:var(--ink-3)}
  .mi-portal .doc-meta .price{margin-left:auto;font-size:14px;font-weight:640;color:var(--ink);letter-spacing:-.2px}
  .mi-portal .doc-meta .price small{font-size:11px;font-weight:400;color:var(--ink-3)}
  .mi-portal .stars{display:flex;align-items:center;gap:3px;color:var(--lamp);font-weight:600}

  .mi-portal .filter-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
  .mi-portal .pill{
    font-size:12.5px;padding:6px 15px;border-radius:20px;border:1px solid var(--line);
    background:var(--surface);color:var(--ink-2);transition:.2s var(--ease);
  }
  .mi-portal .pill:hover{border-color:#C6DAD6}
  .mi-portal .pill.on{background:var(--sea);border-color:var(--sea);color:#fff}

  /* ---------- 弹窗 ---------- */
  .mi-portal .overlay{
    position:fixed;inset:0;background:rgba(20,32,33,.32);backdrop-filter:blur(3px);
    display:none;align-items:center;justify-content:center;z-index:80;padding:24px;
  }
  .mi-portal .overlay.open{display:flex;animation:fade .25s var(--ease)}
  @keyframes fade{from{opacity:0}to{opacity:1}}
  .mi-portal .modal{
    background:var(--surface);border-radius:22px;width:100%;max-width:520px;
    box-shadow:var(--shadow-l);max-height:88vh;overflow-y:auto;animation:modalIn .34s var(--ease);
  }
  @keyframes modalIn{from{opacity:0;transform:translateY(18px) scale(.985)}to{opacity:1;transform:none}}
  .mi-portal .modal-head{display:flex;align-items:center;gap:12px;padding:22px 24px 0}
  .mi-portal .modal-head h3{font-size:16px;font-weight:600}
  .mi-portal .modal-head .close{margin-left:auto;width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;color:var(--ink-3)}
  .mi-portal .modal-head .close:hover{background:var(--surface-2);color:var(--ink)}
  .mi-portal .modal-body{padding:18px 24px 24px}
  .mi-portal .days{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;margin-bottom:18px}
  .mi-portal .day{
    flex:0 0 58px;padding:10px 0;border-radius:12px;border:1px solid var(--line);
    background:var(--surface-2);text-align:center;transition:.2s var(--ease);
  }
  .mi-portal .day:hover{border-color:#C6DAD6}
  .mi-portal .day.on{background:var(--sea);border-color:var(--sea);color:#fff}
  .mi-portal .day i{display:block;font-size:10.5px;font-style:normal;opacity:.7;margin-bottom:2px}
  .mi-portal .day b{font-size:15px;font-weight:600;font-variant-numeric:tabular-nums}
  .mi-portal .slots{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
  .mi-portal .slot{
    padding:9px 0;border-radius:10px;border:1px solid var(--line);background:var(--surface-2);
    font-size:12.5px;color:var(--ink-2);transition:.2s var(--ease);font-variant-numeric:tabular-nums;
  }
  .mi-portal .slot:hover:not(:disabled){border-color:#C6DAD6;background:var(--sea-soft);color:var(--sea-deep)}
  .mi-portal .slot.on{background:var(--sea);border-color:var(--sea);color:#fff}
  .mi-portal .slot:disabled{opacity:.34;cursor:not-allowed;text-decoration:line-through}

  .mi-portal .toast{
    position:fixed;left:50%;bottom:34px;transform:translate(-50%,20px);
    background:#1B2A2C;color:#fff;padding:11px 20px;border-radius:12px;font-size:13px;
    box-shadow:var(--shadow-l);opacity:0;pointer-events:none;transition:.35s var(--ease);z-index:99;
    display:flex;align-items:center;gap:9px;
  }
  .mi-portal .toast.show{opacity:1;transform:translate(-50%,0)}

  .mi-portal .empty{text-align:center;padding:46px 20px;color:var(--ink-3);font-size:13px}

  @media (max-width:1080px){
    .mi-portal .grid-3{grid-template-columns:1fr}
    .mi-portal .grid-2{grid-template-columns:1fr}
    .mi-portal .result-grid{grid-template-columns:1fr}
    .mi-portal .lamp-shell{grid-template-columns:1fr;height:auto}
    .mi-portal .sess-list{display:none}
    .mi-portal .chat{height:calc(100vh - 200px);min-height:480px}
  }
  @media (max-width:820px){
    .mi-portal .sidebar{display:none}
    .mi-portal .view,.mi-portal .topbar{padding-left:18px;padding-right:18px}
    .mi-portal .search{display:none}
    .mi-portal .quiz-card{padding:26px 20px}
    .mi-portal .slots{grid-template-columns:repeat(3,1fr)}
  }

  /* ========== 水波纹背景 ========== */
  .mi-portal .ripple-bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
  .mi-portal .app{position:relative;z-index:1}
  .mi-portal .rb-rings{position:absolute;right:-170px;bottom:-200px;width:640px;height:640px;color:#2E6E68;opacity:.065;animation:rbBreath 16s ease-in-out infinite}
  .mi-portal .rb-rings circle{fill:none;stroke:currentColor;stroke-width:1.1}
  .mi-portal .rb-rings .core{fill:currentColor;stroke:none}
  .mi-portal .rb-rings-2{position:absolute;left:-140px;top:96px;width:340px;height:340px;color:#2E6E68;opacity:.04;animation:rbBreath 21s ease-in-out infinite reverse}
  .mi-portal .rb-rings-2 circle{fill:none;stroke:currentColor;stroke-width:1.1}
  .mi-portal .rb-waves{position:absolute;left:0;bottom:0;width:200%;height:210px;animation:rbDrift 30s linear infinite}
  .mi-portal .rb-waves path{fill:none;stroke:#2E6E68;stroke-width:1.3;opacity:.055}
  .mi-portal .rb-waves path:last-child{stroke:#D9982F;opacity:.04}
  @keyframes rbBreath{0%,100%{transform:scale(1)}50%{transform:scale(1.045)}}
  @keyframes rbDrift{from{transform:translateX(0)}to{transform:translateX(-50%)}}

  /* 点击涟漪 */
  .mi-portal .tap-ripple{position:fixed;z-index:200;pointer-events:none;border-radius:50%;border:1.5px solid rgba(46,110,104,.42);background:rgba(46,110,104,.07);transform:translate(-50%,-50%) scale(0);animation:tapRipple .7s cubic-bezier(.2,.7,.3,1) forwards}
  @keyframes tapRipple{to{transform:translate(-50%,-50%) scale(1);opacity:0}}

  /* 今日心情打卡 */
  .mi-portal .mood-card{display:flex;align-items:center;gap:18px;background:linear-gradient(105deg,#FFFFFF 20%,#F1F8F5);border:1px solid var(--line);border-radius:18px;padding:15px 22px;margin-bottom:16px;box-shadow:var(--shadow-s);position:relative;overflow:hidden}
  .mi-portal .mood-card::before{content:"";position:absolute;right:24%;top:-70px;width:230px;height:230px;border-radius:50%;border:1px solid rgba(46,110,104,.06);box-shadow:0 0 0 26px rgba(46,110,104,.028),0 0 0 54px rgba(46,110,104,.016)}
  .mi-portal .mood-k{font-size:13.5px;font-weight:560;display:block;position:relative}
  .mi-portal .mood-hint{font-size:11.5px;color:var(--ink-3);display:block;margin-top:3px;position:relative}
  .mi-portal .mood-dots{display:flex;gap:6px;margin-left:auto;position:relative}
  .mi-portal .mood-dot{display:flex;flex-direction:column;align-items:center;gap:6px;padding:5px 9px;border-radius:12px;transition:.25s var(--ease)}
  .mi-portal .mood-dot i{display:block;width:19px;height:19px;border-radius:50%;border:1.5px solid;background:transparent;transition:.28s var(--ease)}
  .mi-portal .mood-dot span{font-size:11px;color:var(--ink-3);transition:color .2s}
  .mi-portal .mood-dot:hover{background:var(--sea-soft)}
  .mi-portal .mood-dot:hover i{transform:translateY(-2px) scale(1.12)}
  .mi-portal .mood-dot.on{background:var(--sea-soft)}
  .mi-portal .mood-dot.on i{transform:scale(1.22);box-shadow:0 0 0 5px rgba(46,110,104,.10)}
  .mi-portal .mood-dot.on span{color:var(--sea-deep);font-weight:560}

  /* 潮汐图悬浮 */
  .mi-portal .tide-wrap{position:relative}
  .mi-portal .tide-tip{position:absolute;transform:translate(-50%,-118%);background:#1B2A2C;color:#fff;padding:6px 11px;border-radius:9px;font-size:11.5px;line-height:1.5;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .18s;box-shadow:var(--shadow-m)}
  .mi-portal .tide-tip.show{opacity:1}
  .mi-portal .tide-hit{fill:transparent;cursor:crosshair}
  .mi-portal .tide-mark{transition:opacity .2s}

  /* 答题切换 / 屿灯水面 / 细节 */
  .mi-portal .quiz-card.swap{animation:swapIn .38s var(--ease)}
  @keyframes swapIn{from{opacity:.3;transform:translateY(10px)}to{opacity:1;transform:none}}
  .mi-portal .chat-body{position:relative}
  .mi-portal .chat-body::after{content:"";position:absolute;left:50%;bottom:-96px;transform:translateX(-50%);width:300px;height:200px;border-radius:50%;border:1px solid rgba(46,110,104,.075);box-shadow:0 0 0 30px rgba(46,110,104,.035),0 0 0 62px rgba(46,110,104,.018),0 0 0 96px rgba(46,110,104,.01);pointer-events:none}
  .mi-portal .nav-item:hover{transform:translateX(2px)}
  .mi-portal .eyebrow{display:flex;align-items:center;gap:10px}
  .mi-portal .eyebrow::after{content:"";width:26px;height:1px;background:var(--sea);opacity:.4}
  .mi-portal :focus-visible{outline:2px solid rgba(46,110,104,.5);outline-offset:2px}
  @media (prefers-reduced-motion:reduce){.mi-portal *{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
  @media (max-width:820px){
    .mi-portal .mood-card{flex-direction:column;align-items:flex-start}
    .mi-portal .mood-dots{margin-left:0;width:100%;justify-content:space-between}
    .mi-portal .rb-rings{opacity:.045}
  }
  .mi-portal .avatar{position:relative}
  .mi-portal .mood-pip{position:absolute;right:-2px;bottom:-2px;width:10px;height:10px;border-radius:50%;background:#C9D2D0;border:2px solid #fff;transition:background .4s var(--ease),box-shadow .4s var(--ease)}
  .mi-portal .mood-pip.lit{box-shadow:0 0 0 4px rgba(46,110,104,.10)}

  /* ========== 米色底纹：细密水波平铺 ========== */
  .mi-portal .rb-texture{position:absolute;left:-2%;top:-2%;width:104%;height:104%;opacity:.9;animation:rbFloat 26s ease-in-out infinite}
  @keyframes rbFloat{0%,100%{transform:translate(0,0)}50%{transform:translate(-7px,-9px)}}

  /* ========== 情绪潮汐：曲线下的水面波纹 ========== */
  .mi-portal .tide-ripples path{fill:none;stroke-linecap:round}
  .mi-portal .tr1{stroke:#2E6E68;stroke-width:1.2;opacity:.20;animation:tideShift 14s linear infinite}
  .mi-portal .tr2{stroke:#4E9287;stroke-width:1;opacity:.15;animation:tideShift 21s linear infinite}
  .mi-portal .tr3{stroke:#D9982F;stroke-width:1;opacity:.10;animation:tideShift 29s linear infinite}
  @keyframes tideShift{from{transform:translateX(0)}to{transform:translateX(-160px)}}
  .mi-portal .tide-glint{animation:tideGlint 9s linear infinite}
  @keyframes tideGlint{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}

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

</style>
