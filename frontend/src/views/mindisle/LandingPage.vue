<template>
  <div class="mi-landing" data-theme="light" ref="rootEl">
<canvas id="trail" aria-hidden="true"></canvas>

<button class="theme-btn" id="themeBtn" title="切换明暗主题" aria-label="切换明暗主题">
  <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
  <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>
</button>

<div class="page">

  <!-- ==================== 左：品牌 + 文案 ==================== -->
  <section class="left">
    <div class="brand">
      <div class="brand-mark">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none">
          <path d="M3 17.5c2.2 0 2.6-3.5 4.8-3.5s2.4 2.4 4.4 2.4 2.5-4.2 4.8-4.2c1.4 0 2.4.9 3 1.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
          <circle cx="16.6" cy="7" r="2.1" fill="#F6D08A"/>
        </svg>
      </div>
      <div>
        <div class="brand-name" data-copy="W1">心屿</div>
        <div class="brand-en" data-copy="W2">Mindisle</div>
      </div>
      <span class="brand-tag" data-copy="W3">心理健康 · 陪伴平台</span>
    </div>

    <div class="hero">
      <div class="eyebrow" data-reveal style="--d:0" data-copy="W3b">A QUIET PLACE FOR YOUR MIND</div>
      <h1 class="hero-title">
        <span class="line-zh" id="wordZh"></span>
        <span class="line-en" id="wordEn"></span>
      </h1>
      <p class="slogan" data-reveal style="--d:1" data-copy="W6">让每一种情绪，都有处可栖。</p>
      <p class="desc" data-reveal style="--d:2" data-copy="W7">测评是一张地图，屿灯是一盏常亮的灯，咨询是一位愿意同行的人。你不必先整理好自己才来到这里——慢慢来，我们等你。</p>
      <div class="tags" data-reveal style="--d:3">
        <span class="tag" data-copy="W8a">心理测评</span>
        <span class="tag" data-copy="W8b">屿灯 · AI 情绪支持</span>
        <span class="tag" data-copy="W8c">咨询预约</span>
      </div>
      <div class="actions" data-reveal style="--d:4">
        <button class="pill pill-primary" data-act="about"><span data-copy="W10">了解心屿</span>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>
        </button>
        <button class="pill pill-ghost" data-copy="W11" data-act="help">帮助中心</button>
      </div>
      <div class="social" data-reveal style="--d:5">
        <div class="chips" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="c0"><path d="M16 2 A14 14 0 1 1 16 30 A14 14 0 1 1 16 2 Z"/></clipPath></defs><rect width="32" height="32" fill="#C36950" clip-path="url(#c0)"/></svg>
          <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="c1"><path d="M16 3 L27 8.5 L27 23.5 L16 29 L5 23.5 L5 8.5 Z"/></clipPath></defs><rect width="32" height="32" fill="#A57D46" clip-path="url(#c1)"/></svg>
          <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="c2"><path d="M16 3 L29 13 L24 28 L8 28 L3 13 Z"/></clipPath></defs><rect width="32" height="32" fill="#558C96" clip-path="url(#c2)"/></svg>
          <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="c3"><path d="M11 2 L21 2 L30 11 L30 21 L21 30 L11 30 L2 21 L2 11 Z"/></clipPath></defs><rect width="32" height="32" fill="#6E915A" clip-path="url(#c3)"/></svg>
          <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="c4"><path d="M5 5 L27 5 L27 27 L5 27 Z"/></clipPath></defs><rect width="32" height="32" fill="#A56982" clip-path="url(#c4)"/></svg>
        </div>
        <p><span data-copy="W9a">已有 </span><b data-copy="W9b">12,000+</b><span data-copy="W9c"> 人在这里停靠</span></p>
      </div>
    </div>
  </section>

  <!-- ==================== 右：单一登录板块（用户 / 管理员切换） ==================== -->
  <section class="right">
    <div class="right-head">
      <div class="rh-eyebrow" data-copy="W28">Welcome back</div>
      <h2 data-copy="W29">欢迎回来</h2>
    </div>

    <div class="card" id="loginCard" data-mode="user">
      <div class="portal-switch" id="portalSwitch" role="tablist" aria-label="登录身份">
        <button class="portal on" type="button" data-portal="user" role="tab" aria-selected="true">
          <i class="dot"></i><span data-copy="W12">用户登录</span>
        </button>
        <button class="portal" type="button" data-portal="admin" role="tab" aria-selected="false">
          <i class="dot"></i><span data-copy="W33">管理员</span>
        </button>
      </div>

      <div class="card-head">
        <h3 id="portalTitle" data-copy="W12">用户登录</h3>
      </div>

      <form id="loginForm" novalidate>
        <label class="field">
          <span id="accountLabel" data-copy="W30">账号</span>
          <input class="input" id="account" type="text" autocomplete="username" data-copy-ph="W15">
        </label>
        <label class="field">
          <span data-copy="W31">密码</span>
          <div class="pw-wrap">
            <input class="input" id="pwd" type="password" autocomplete="current-password" data-copy-ph="W17">
            <button class="eye" type="button" data-eye="pwd" aria-label="显示密码">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6z"/><circle cx="12" cy="12" r="2.6"/></svg>
            </button>
          </div>
        </label>
        <div class="row" id="userOnly">
          <label class="check"><input type="checkbox" id="remember"><span data-copy="W18a">记住我</span></label>
          <a class="link" href="#" data-act="forgot" data-copy="W18b">忘记密码？</a>
        </div>
        <button class="submit" type="submit" id="submitBtn" data-copy="W19">登 录</button>
        <p class="reg" id="regRow"><span data-copy="W20a">还没有账号？</span><a class="link" href="#" data-act="register" data-copy="W20b">立即注册</a></p>
      </form>
    </div>

    <p class="foot" data-copy="W25">© 2026 心屿 Mindisle</p>
    <p class="crisis" data-copy="W26">如遇心理危机，请立即联系专业机构或拨打心理援助热线</p>
  </section>

  <!-- 平台信息浮层：点击「了解心屿」弹出，停留期间可移入暂停 -->
  <aside class="about" id="aboutCard" role="dialog" aria-modal="false" aria-labelledby="aboutTitle" aria-hidden="true">
    <div class="about-head">
      <div>
        <div class="about-eyebrow" data-copy="W40">ABOUT MINDISLE</div>
        <h3 id="aboutTitle" data-copy="W41">关于心屿</h3>
      </div>
      <button class="about-close" id="aboutClose" type="button" aria-label="关闭平台介绍">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
    </div>
    <p class="about-intro" data-copy="W42">心屿把测评、情绪陪伴与专业咨询串成一条连续的路径——先看清自己，再随时有人可倾诉，需要时有人同行。</p>
    <ul class="about-list">
      <li><i class="about-dot"></i><div><b data-copy="W43a">岛图 · 心理测评</b><span data-copy="W44a">用标准化量表记录情绪变化，看清自己的起伏与需要留意的角落。</span></div></li>
      <li><i class="about-dot"></i><div><b data-copy="W43b">屿灯 · AI 情绪支持</b><span data-copy="W44b">一盏随时亮着的灯。说不清楚也没关系，慢慢说，我们听着。</span></div></li>
      <li><i class="about-dot"></i><div><b data-copy="W43c">靠岸 · 咨询预约</b><span data-copy="W44c">需要更深的陪伴时，预约一位咨询师，有人陪你走一段。</span></div></li>
    </ul>
    <p class="about-note" data-copy="W45">测评结果仅用于自我了解，不构成医学诊断；如遇紧急心理危机，请联系专业机构或心理援助热线。</p>
    <div class="about-timer" aria-hidden="true"><i id="aboutBar"></i></div>
  </aside>
</div>

<div class="toast" id="toast"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.01"/></svg><span id="toastText"></span></div>
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

function mountLanding(rootEl, loginHandler, navigate) {
  const listeners = []
  const timers = []
  let rafId = null
  function winOn(t, f, o) { window.addEventListener(t, f, o); listeners.push(['window', t, f, o]) }
  function docOn(t, f, o) { document.addEventListener(t, f, o); listeners.push(['document', t, f, o]) }
  function trackTimeout(f, ms) { const id = setTimeout(f, ms); timers.push(id); return id }
  function trackInterval(f, ms) { const id = setInterval(f, ms); timers.push(id); return id }

"use strict";

/* ==================================================================
   文案区 · 所有待审核文案集中在此（data-copy / data-copy-ph 引用）
   审核后只需改这里，页面上所有位置会同步更新
   ================================================================== */
const COPY = {
  W1 : '心屿',
  W2 : 'Mindisle',
  W3 : '心理健康 · 陪伴平台',
  W3b: 'A QUIET PLACE FOR YOUR MIND',
  W4 : '心屿',
  W5 : 'Mindisle',
  W6 : '让每一种情绪，都有处可栖。',
  W7 : '测评是一张地图，屿灯是一盏常亮的灯，咨询是一位愿意同行的人。你不必先整理好自己才来到这里——慢慢来，我们等你。',
  W8a: '心理测评',
  W8b: '屿灯 · AI 情绪支持',
  W8c: '咨询预约',
  W9a: '已有 ',
  W9b: '12,000+',
  W9c: ' 人在这里停靠',
  W10: '了解心屿',
  W11: '帮助中心',
  W12: '用户登录',
  W15: '学号 / 工号 / 校园邮箱',
  W17: '请输入密码',
  W18a:'记住我',
  W18b:'忘记密码？',
  W19: '登 录',
  W20a:'还没有账号？',
  W20b:'立即注册',
  W21: '管理员登录',
  W23: '请输入管理员账号',
  W24: '进入管理后台',
  W25: '© 2026 心屿 Mindisle',
  W26: '如遇心理危机，请立即联系专业机构或拨打心理援助热线',
  W28: 'Welcome back',
  W29: '欢迎回来',
  W30: '账号',
  W30b:'管理员账号',
  W31: '密码',
  W32: '请输入管理员密码',
  W33: '管理员',
  /* 「了解心屿」信息浮层文案，集中在此供审核 */
  W40: 'ABOUT MINDISLE',
  W41: '关于心屿',
  W42: '心屿把测评、情绪陪伴与专业咨询串成一条连续的路径——先看清自己，再随时有人可倾诉，需要时有人同行。',
  W43a:'岛图 · 心理测评',
  W43b:'屿灯 · AI 情绪支持',
  W43c:'靠岸 · 咨询预约',
  W44a:'用标准化量表记录情绪变化，看清自己的起伏与需要留意的角落。',
  W44b:'一盏随时亮着的灯。说不清楚也没关系，慢慢说，我们听着。',
  W44c:'需要更深的陪伴时，预约一位咨询师，有人陪你走一段。',
  W45: '测评结果仅用于自我了解，不构成医学诊断；如遇紧急心理危机，请联系专业机构或心理援助热线。'
};

rootEl.querySelectorAll('[data-copy]').forEach(function(el){
  var k = el.getAttribute('data-copy');
  if(COPY[k] != null) el.textContent = COPY[k];
});
rootEl.querySelectorAll('[data-copy-ph]').forEach(function(el){
  var k = el.getAttribute('data-copy-ph');
  if(COPY[k] != null) el.setAttribute('placeholder', COPY[k]);
});

/* 主标题逐字拆分（对应 md 规范的 per-character split + stagger） */
function buildWord(el, text, start){
  el.innerHTML = '';
  var chars = Array.from(text);
  chars.forEach(function(ch, i){
    var s = document.createElement('span');
    s.className = 'ltr';
    s.style.setProperty('--i', start + i);
    s.textContent = ch === ' ' ? '\u00A0' : ch;
    el.appendChild(s);
  });
  return start + chars.length;
}
var next = buildWord(document.getElementById('wordZh'), COPY.W4, 0);
buildWord(document.getElementById('wordEn'), COPY.W5, next + 2);

/* ================= 表单交互 ================= */
var toastEl = document.getElementById('toast');
var toastText = document.getElementById('toastText');
var toastTimer;
function toast(msg){
  toastText.textContent = msg;
  toastEl.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = trackTimeout(function(){ toastEl.classList.remove('show'); }, 2800);
}

/* 单一板块两套身份：user = 学生 + 咨询师共用入口；admin = 管理员 */
var loginCard   = document.getElementById('loginCard');
var loginForm   = document.getElementById('loginForm');
var cardHead    = loginCard.querySelector('.card-head');
var portalTitle = document.getElementById('portalTitle');
var accountLabel= document.getElementById('accountLabel');
var account     = document.getElementById('account');
var pwd         = document.getElementById('pwd');
var submitBtn   = document.getElementById('submitBtn');
var regRow      = document.getElementById('regRow');
var portalMode  = 'user';

var MODES = {
  user: {
    title: COPY.W12,
    label: COPY.W30,  accPh: COPY.W15, pwdPh: COPY.W17,
    submit: COPY.W19,
    label2: '账号',   ok: '界面演示：账号服务尚未接入'
  },
  admin: {
    title: COPY.W21,
    label: COPY.W30b, accPh: COPY.W23, pwdPh: COPY.W32,
    submit: COPY.W24,
    label2: '管理员账号', ok: '界面演示：管理后台尚未接入'
  }
};

function setPortal(mode, animate){
  var m = MODES[mode];
  if(!m) return;
  portalMode = mode;
  loginCard.setAttribute('data-mode', mode);
  rootEl.querySelectorAll('.portal').forEach(function(b){
    var on = b.getAttribute('data-portal') === mode;
    b.classList.toggle('on', on);
    b.setAttribute('aria-selected', on ? 'true' : 'false');
  });
  portalTitle.textContent  = m.title;
  accountLabel.textContent = m.label;
  account.placeholder      = m.accPh;
  pwd.placeholder          = m.pwdPh;
  submitBtn.textContent    = m.submit;
  submitBtn.classList.toggle('alt', mode === 'admin');
  /* 「记住我 / 忘记密码」两种身份都保留，让卡片内容量与留白保持稳定 */
  regRow.hidden = mode !== 'user';
  if(animate){
    pwd.value = '';                       /* 两套账号体系，切换时清空密码 */
    [cardHead, loginForm].forEach(function(el){
      el.classList.remove('card-swap');
      void el.offsetWidth;
      el.classList.add('card-swap');
    });
  }
}
setPortal('user', false);
document.getElementById('portalSwitch').addEventListener('click', function(e){
  var b = e.target.closest('.portal');
  if(b && b.getAttribute('data-portal') !== portalMode) setPortal(b.getAttribute('data-portal'), true);
});

rootEl.querySelectorAll('[data-eye]').forEach(function(b){
  b.addEventListener('click', function(){
    var input = document.getElementById(b.getAttribute('data-eye'));
    input.type = input.type === 'password' ? 'text' : 'password';
    b.style.color = input.type === 'text' ? 'var(--sea)' : '';
  });
});

function validate(account, pwd, label){
  if(!account.value.trim()){ toast('请填写' + label); account.focus(); return false; }
  if(!pwd.value.trim()){ toast('请填写密码'); pwd.focus(); return false; }
  if(pwd.value.length < 6){ toast('密码至少 6 位'); pwd.focus(); return false; }
  return true;
}
loginForm.addEventListener('submit', function(e){
  e.preventDefault();
  var m = MODES[portalMode];
  if(validate(account, pwd, m.label2)){
    if(typeof loginHandler === 'function'){ loginHandler({ account: account.value.trim(), password: pwd.value, portal: portalMode }); }
    else { toast(m.ok); }
  }
});

/* 「了解心屿」平台信息浮层：9 秒停留、移入暂停、可手动关闭 / Esc */
var ABOUT_MS = 9000, ABOUT_STEP = 50;
var aboutCard = document.getElementById('aboutCard');
var aboutBar  = document.getElementById('aboutBar');
var aboutLeft = 0, aboutTimer = null, aboutPaused = false;
function closeAbout(){
  if(aboutTimer){ clearInterval(aboutTimer); aboutTimer = null; }
  aboutCard.classList.remove('show');
  aboutCard.setAttribute('aria-hidden','true');
}
function openAbout(){
  closeAbout();
  aboutLeft = ABOUT_MS; aboutPaused = false;
  aboutBar.style.width = '100%';
  aboutCard.classList.add('show');
  aboutCard.setAttribute('aria-hidden','false');
  aboutTimer = trackInterval(function(){
    if(aboutPaused) return;
    aboutLeft -= ABOUT_STEP;
    if(aboutLeft <= 0){ closeAbout(); return; }
    aboutBar.style.width = (aboutLeft / ABOUT_MS * 100).toFixed(2) + '%';
  }, ABOUT_STEP);
}
aboutCard.addEventListener('mouseenter', function(){ aboutPaused = true; });
aboutCard.addEventListener('mouseleave', function(){ aboutPaused = false; });
document.getElementById('aboutClose').addEventListener('click', function(e){
  e.stopPropagation(); closeAbout();
});
docOn('keydown', function(e){ if(e.key === 'Escape') closeAbout(); });

var ACTS = {
  help:    '帮助中心正在整理中，稍后开放',
  forgot:  '密码找回需接入邮件服务后开放',
  register:'注册入口需接入账号服务后开放'
};
docOn('click', function(e){
  if(e.target.closest('#aboutCard')) return;          /* 浮层内部不触发 toast */
  var t = e.target.closest('[data-act]');
  var isAboutBtn = t && t.getAttribute('data-act') === 'about';
  if(aboutCard.classList.contains('show') && !isAboutBtn) closeAbout();  /* 点其它处收起 */
  if(!t) return;
  e.preventDefault();
  if(isAboutBtn){ openAbout(); return; }
  var act = t.getAttribute('data-act');
  if(typeof navigate === 'function' && navigate(act)) return;
  toast(ACTS[act]);
});

/* ================= 主题 ================= */
var root = rootEl;
var theme = 'light';
var palette;
document.getElementById('themeBtn').addEventListener('click', function(){
  root.setAttribute('data-theme', theme === 'light' ? 'dark' : 'light');
});

/* ==================================================================
   Shape Trail · 按 shape-trail.md 实现的几何画布
   10 种形状 / 48 顶点 / 尾迹生成 / hover 形变 / 点击爆发 / 颜色波
   为登录页可读性做了两处调校：形状不透明度 0.30、右侧表单区渐隐
   另加「静态几何群岛」：中缝 16 个常驻种子，alpha .10-.18，不老化
   ================================================================== */
var LIGHT = [[195,105,80],[165,125,70],[110,145,90],[85,140,150],[165,105,130],[130,120,165],[180,140,85],[105,135,100]];
var DARK  = [[215,145,120],[190,155,115],[170,195,150],[145,185,190],[195,150,170],[175,165,200],[210,175,130],[155,175,145]];
var N = 48, TAU = Math.PI * 2;

function distribute(vs){
  var segs = [], total = 0, i;
  for(i = 0; i < vs.length; i++){
    var a = vs[i], b = vs[(i+1) % vs.length];
    var len = Math.hypot(b[0]-a[0], b[1]-a[1]);
    segs.push({a:a, b:b, len:len, start:total});
    total += len;
  }
  var out = [];
  for(var k = 0; k < N; k++){
    var d = (k / N) * total;
    var s = segs[segs.length - 1];
    for(i = 0; i < segs.length; i++){ if(d <= segs[i].start + segs[i].len){ s = segs[i]; break; } }
    var t = s.len ? (d - s.start) / s.len : 0;
    out.push([s.a[0] + (s.b[0]-s.a[0])*t, s.a[1] + (s.b[1]-s.a[1])*t]);
  }
  return out;
}
function cubic(p0, p1, p2, p3, n){
  var o = [];
  for(var i = 0; i < n; i++){
    var t = i/n, u = 1-t;
    o.push([
      u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
      u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]
    ]);
  }
  return o;
}
function twoArc(a, b, c, d){
  var top = [0,-1], bot = [0,1];
  return cubic(top, a, b, bot, 24).concat(cubic(bot, c, d, top, 24));
}
function polygon(n, r, off){
  return distribute(Array.from({length:n}, function(_, i){
    var a = i/n*TAU + (off === undefined ? -Math.PI/2 : off);
    return [r*Math.cos(a), r*Math.sin(a)];
  }));
}
var SHAPES = [
  twoArc([.9,-.6],[.9,.6],[-.9,.6],[-.9,-.4]),
  distribute([[0,-1.1],[1,.77],[-1,.77]]),
  Array.from({length:N}, function(_, i){ return [Math.cos(i/N*TAU), Math.sin(i/N*TAU)]; }),
  distribute([[0,-1.1],[.9,0],[0,.4],[-.9,0]]),
  distribute(Array.from({length:12}, function(_, i){
    var r = i % 2 ? .45 : 1, a = i/12*TAU - Math.PI/2;
    return [r*Math.cos(a), r*Math.sin(a)];
  })),
  distribute([[-.82,-.82],[.82,-.82],[.82,.82],[-.82,.82]]),
  distribute([[-.165,-1],[.55,-.15],[.055,-.05],[.275,1],[-.44,.1],[-.0275,.05]]),
  twoArc([.6,-.4],[.8,.3],[-.8,.3],[-.6,-.4]),
  polygon(6,1),
  polygon(5,1)
];

var cvs = document.getElementById('trail');
var ctx = cvs.getContext('2d');
var W = 0, H = 0, DPR = 1;
function resize(){
  DPR = Math.min(2, window.devicePixelRatio || 1);
  W = window.innerWidth; H = window.innerHeight;
  cvs.width = W*DPR; cvs.height = H*DPR;
  cvs.style.width = W+'px'; cvs.style.height = H+'px';
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
resize();
winOn('resize', function(){ resize(); layoutSeeds(); });

var shapes = [], waves = [], seeds = [];
var mx = -999, my = -999, hasMouse = false, distAccum = 0;
var rawSpeed = 0, smoothSpeed = 0;
var lastType = -1, lastColor = -1, hovered = null;
var pulse = 1, pulseTarget = 1, burstCount = 5, clickIntensity = 0, burstTimer = 0;
var lastTime = 0, clock = 0;
var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function applyTheme(){
  var prev = theme;
  theme = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  palette = theme === 'dark' ? DARK : LIGHT;
  /* 常驻群岛跟随主题换色，避免切换后残留上一套色盘 */
  if(prev && prev !== theme){
    for(var i = 0; i < seeds.length; i++){
      var s = seeds[i], c = palette[s.ci];
      s.r = c[0]; s.g = c[1]; s.b = c[2];
      s.prevR = c[0]; s.prevG = c[1]; s.prevB = c[2];
    }
  }
}
applyTheme();
new MutationObserver(applyTheme).observe(root, {attributes:true, attributeFilter:['data-theme']});

function pickColor(idxAvoid){
  var ci, guard = 0;
  do { ci = Math.floor(Math.random()*8); } while(ci === idxAvoid && guard++ < 8);
  lastColor = ci;
  return palette[ci].map(function(v){
    return Math.max(0, Math.min(255, v + Math.floor((Math.random()-.5)*20)));
  });
}
function zoneAlpha(x){
  /* 卡片区只轻微压暗，形状仍透过玻璃浮层隐约可见 */
  var t = Math.min(1, Math.max(0, (x/Math.max(1,W) - .55) / .30));
  return 1 - .48*t;
}

/* ---------- A 方案：静态几何群岛（中缝常驻种子） ----------
   复用 md 的 10 种形状 / 48 顶点；不参与 2s 老化，只做缓慢自转与
   呼吸（alpha .10-.18）；hover 触发形变并释放一小簇短命尾迹。
   位置用确定性伪随机，窗口变化时按归一化坐标重排，不重新洗牌。 */
var rndState = 20261108;
function rnd(){ rndState = (rndState*1664525 + 1013904223) >>> 0; return rndState / 4294967296; }
function layoutSeeds(){
  var count = 16, clusters = [[.44,.27],[.54,.66],[.66,.44]];
  if(!seeds.length){
    for(var i = 0; i < count; i++){
      var c = clusters[i % 3];
      var j = i < 9 ? .075 : .15;          /* 前 9 个聚成三簇小岛，其余为散点 */
      var nx = Math.min(.77, Math.max(.35, c[0] + (rnd()-.5)*j*2));
      var ny = Math.min(.90, Math.max(.10, c[1] + (rnd()-.5)*j*2.6));
      var t = Math.floor(rnd()*10), ci = Math.floor(rnd()*8);
      var col = palette[ci];
      var s = {
        seed:true, nx:nx, ny:ny, nr:(18 + rnd()*25)/1440, ci:ci,
        x:0, y:0, size:0, life:0, maxLife:2,
        type:t, r:col[0], g:col[1], b:col[2],
        prevR:col[0], prevG:col[1], prevB:col[2],
        rotation:rnd()*TAU, rotationSpeed:(rnd()-.5)*.10,
        morphT:1, currentPoints:SHAPES[t], targetPoints:SHAPES[t],
        phase:rnd()*TAU, breath:.45 + rnd()*.55,
        base:.10 + rnd()*.08
      };
      seeds.push(s);
      shapes.push(s);
    }
  }
  for(var k = 0; k < seeds.length; k++){
    var q = seeds[k];
    q.x = q.nx * W;
    q.y = q.ny * H;
    q.size = Math.max(12, q.nr * W);
  }
}
layoutSeeds();
function spawn(x, y, opts){
  var t, guard = 0;
  do { t = Math.floor(Math.random()*10); } while(t === lastType && guard++ < 8);
  lastType = t;
  var df = Math.min(1, Math.max(0, (x/Math.max(1,W) + (1 - y/Math.max(1,H)))/2));
  var size = 21 + df*21, live = 0;
  for(var i = 0; i < shapes.length; i++){
    var s = shapes[i];
    if(s.seed) continue;                /* 常驻群岛不阻挡鼠标尾迹 */
    live++;
    if(Math.hypot(s.x-x, s.y-y) < (s.size + size)*.7) return null;
  }
  if(live >= 140) return null;
  var c = pickColor(lastColor);
  var o = opts || {};
  if(o.intensity){
    var target = theme === 'dark' ? 255 : 0;
    var steps = o.intensity * (o.proximity === undefined ? 1 : o.proximity);
    for(var k = 0; k < steps; k++){
      c[0] += (target-c[0])*.2; c[1] += (target-c[1])*.2; c[2] += (target-c[2])*.2;
    }
  }
  var sh = {
    x:x, y:y, size:size,
    rotation:Math.random()*TAU, rotationSpeed:Math.random()*2-1,
    type:t, r:c[0], g:c[1], b:c[2],
    life:o.life || 0, maxLife:2,
    morphT:1, currentPoints:SHAPES[t], targetPoints:SHAPES[t],
    prevR:c[0], prevG:c[1], prevB:c[2]
  };
  shapes.push(sh);
  return sh;
}
function smoothstep(t){ return t*t*(3-2*t); }
function findAt(x, y){
  for(var i = shapes.length-1; i >= 0; i--){
    if(Math.hypot(shapes[i].x-x, shapes[i].y-y) < shapes[i].size) return shapes[i];
  }
  return null;
}
function morph(s){
  var mt = s.morphT < 1 ? smoothstep(s.morphT) : 1;
  s.currentPoints = s.currentPoints.map(function(p, i){
    return [p[0] + (s.targetPoints[i][0]-p[0])*mt, p[1] + (s.targetPoints[i][1]-p[1])*mt];
  });
  s.prevR = s.r; s.prevG = s.g; s.prevB = s.b;
  s.morphT = 0;
  var t;
  do { t = Math.floor(Math.random()*10); } while(t === s.type);
  s.type = t; s.targetPoints = SHAPES[t];
  var c = pickColor(lastColor);
  s.r = c[0]; s.g = c[1]; s.b = c[2];
  s.life = s.maxLife * .07;
  s.rotationSpeed = Math.random()*2-1;
}

winOn('mousemove', function(e){
  var x = e.clientX, y = e.clientY;
  if(!hasMouse){ mx = x; my = y; hasMouse = true; return; }
  var dx = x-mx, dy = y-my, dist = Math.hypot(dx,dy);
  rawSpeed = Math.max(rawSpeed, dist);
  var hit = findAt(x,y);
  if(hit && hit !== hovered){
    morph(hit);
    /* 掠过群岛时释放一小簇短命尾迹，让静态形状"被唤醒" */
    if(hit.seed && !reduceMotion){
      for(var k = 0; k < 3; k++){
        var a2 = Math.random()*TAU, r2 = hit.size*(.75 + Math.random()*.9);
        spawn(x + Math.cos(a2)*r2, y + Math.sin(a2)*r2, {life:.35});
      }
    }
    hovered = hit; mx = x; my = y; return;
  }
  if(!hit) hovered = null;
  if(hit || reduceMotion){ mx = x; my = y; return; }
  distAccum += dist;
  var step = 14, steps = Math.floor(distAccum/step);
  distAccum -= steps*step;
  for(var i = 1; i <= steps; i++){
    var t = i/Math.max(1,steps);
    spawn(mx+dx*t, my+dy*t);
  }
  mx = x; my = y;
}, {passive:true});

winOn('click', function(e){
  if(e.target.closest('.right, .theme-btn, #aboutCard')) return;
  burstCount = burstTimer > 0 ? burstCount + 5 : 5;
  clickIntensity = burstTimer > 0 ? clickIntensity + 1 : 1;
  burstTimer = 2;
  pulseTarget = Math.min(1.5, pulseTarget + .15);
  waves.push({x:e.clientX, y:e.clientY, r:0});
  var x = e.clientX, y = e.clientY;
  spawn(x, y, {intensity:clickIntensity, proximity:1});
  var rings = Math.min(3, Math.ceil(burstCount/5));
  for(var ring = 1; ring <= rings; ring++){
    var radius = ring * 52;
    var count = Math.max(6, Math.floor(TAU*radius/52));
    for(var i = 0; i < count; i++){
      var a = i/count*TAU;
      spawn(x + Math.cos(a)*radius, y + Math.sin(a)*radius,
        {intensity:clickIntensity, proximity:1 - ring/(rings+1)});
    }
  }
});

function drawShape(s, dt){
  s.morphT = Math.min(1, s.morphT + dt*2.2);
  var mt = s.morphT < 1 ? smoothstep(s.morphT) : 1;
  if(!reduceMotion){
    s.rotation += s.rotationSpeed*dt;
    if(!s.seed) s.rotationSpeed *= .997;
  }
  var scale, sz, a;
  if(s.seed){
    /* 常驻群岛：不老化，只呼吸 + 极缓自转；深底吃色，dark 单独提亮一档 */
    var br = reduceMotion ? 1 : 1 + Math.sin(clock*s.breath + s.phase)*.07;
    sz = s.size * br * (1 + (pulse-1)*.35);
    a = s.base * (theme === 'dark' ? 1.25 : 1) * zoneAlpha(s.x) * (W < 1000 ? .72 : 1);
  } else {
    s.life += dt * (1 + Math.min(1, smoothSpeed/45)*2.5);
    var lf = s.life/s.maxLife;
    if(lf < .06) scale = lf/.06;
    else if(lf < .6) scale = 1;
    else { var t = (lf-.6)/.4; scale = 1 - t*t*t; }
    if(lf >= 1 || scale < .01) return false;
    sz = s.size*scale*pulse;
    a = .30 * zoneAlpha(s.x) * Math.min(1, scale*1.6);
  }
  if(sz >= .5){
    var rr = s.prevR + (s.r-s.prevR)*mt;
    var gg = s.prevG + (s.g-s.prevG)*mt;
    var bb = s.prevB + (s.b-s.prevB)*mt;
    ctx.save();
    ctx.translate(s.x, s.y);
    ctx.rotate(s.rotation);
    ctx.beginPath();
    for(var i = 0; i < N; i++){
      var p = s.currentPoints[i], q = s.targetPoints[i];
      var px = (p[0] + (q[0]-p[0])*mt)*sz;
      var py = (p[1] + (q[1]-p[1])*mt)*sz;
      if(i) ctx.lineTo(px,py); else ctx.moveTo(px,py);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba('+(rr|0)+','+(gg|0)+','+(bb|0)+','+a.toFixed(3)+')';
    ctx.fill();
    ctx.restore();
  }
  return true;
}

function frame(ts){
  var dt = Math.min(.05, (ts - lastTime)/1000 || .016);
  lastTime = ts;
  clock += dt;
  ctx.clearRect(0,0,W,H);
  smoothSpeed += (rawSpeed - smoothSpeed)*.25;
  rawSpeed *= .6;
  if(burstTimer > 0){
    burstTimer -= dt;
    if(burstTimer <= 0){ burstCount = 5; clickIntensity = 0; }
  }
  pulse += (pulseTarget - pulse)*Math.min(1, dt*8);
  pulseTarget += (1 - pulseTarget)*Math.min(1, dt*1.5);

  var target = theme === 'dark' ? 255 : 0;
  for(var w = waves.length-1; w >= 0; w--){
    var wv = waves[w];
    wv.r += 150*dt;
    for(var j = 0; j < shapes.length; j++){
      var s = shapes[j];
      if(s.seed) continue;              /* 颜色波只作用于短命尾迹，避免群岛被永久染色 */
      var fromEdge = wv.r - Math.hypot(s.x-wv.x, s.y-wv.y);
      if(fromEdge > 0 && fromEdge < 150){
        var push = .4*(1 - fromEdge/150)*dt*4;
        s.r += (target-s.r)*push; s.g += (target-s.g)*push; s.b += (target-s.b)*push;
      }
    }
    var maxR = Math.hypot(W,H) + 150;
    var prog = Math.min(1, wv.r/(maxR*.3));
    var alpha = Math.max(0, 1 - prog*prog)*.15;
    if(alpha > .005){
      ctx.beginPath(); ctx.arc(wv.x, wv.y, wv.r, 0, TAU);
      ctx.strokeStyle = theme === 'dark' ? 'rgba(255,255,255,'+alpha+')' : 'rgba(0,0,0,'+alpha+')';
      ctx.lineWidth = Math.max(.5, 2.5*(1-prog)); ctx.stroke();
    }
    if(wv.r > maxR || alpha < .005) waves.splice(w,1);
  }

  for(var i = shapes.length-1; i >= 0; i--){
    if(!drawShape(shapes[i], dt)) shapes.splice(i,1);
  }
  rafId = requestAnimationFrame(frame);
}
rafId = requestAnimationFrame(frame);


  return function destroy() {
    if (rafId != null) cancelAnimationFrame(rafId)
    timers.forEach(id => { clearTimeout(id); clearInterval(id) })
    listeners.forEach(l => {
      const target = l[0] === 'window' ? window : document
      target.removeEventListener(l[1], l[2], l[3])
    })
  }
}

onMounted(() => { cleanup = mountLanding(rootEl.value, props.loginHandler, props.navigate) })
onUnmounted(() => { if (cleanup) { cleanup(); cleanup = null } })
</script>

<style>
.mi-landing .card { padding:0; border:0; border-radius:0; box-shadow:none; background:transparent; transition:none; }
.mi-landing .card:hover { transform:none; box-shadow:none; border-color:transparent; }

  .mi-landing{
    --bg:#F6F5F1; --fg:#1B2A2C; --fg-2:#56696D; --fg-3:#93A3A5;
    --line:#E4E2DA; --line-2:#EEECE5;
    --surface:#FFFFFF; --surface-2:#FBFAF7;
    --sea:#2E6E68; --sea-deep:#22524E; --sea-soft:#E2EFEC;
    --lamp:#D9982F; --panel:rgba(248,247,243,.88);
    --glass:rgba(255,255,255,.74); --glass-line:rgba(255,255,255,.82);
    --shadow-s:0 1px 2px rgba(27,42,44,.04);
    --shadow-m:0 1px 2px rgba(27,42,44,.04),0 20px 48px -30px rgba(27,42,44,.32);
    --font-serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;
    --font-display:"Playfair Display",Georgia,"Times New Roman",serif;
    --font-sans:"Inter","Noto Sans SC","PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    --ease:cubic-bezier(.16,1,.3,1);
  }
  .mi-landing[data-theme="dark"]{
    --bg:#0C1213; --fg:#EAF0EE; --fg-2:#A9B9B8; --fg-3:#6F8282;
    --line:#243033; --line-2:#1C2729;
    --surface:#182223; --surface-2:#141E1F;
    --sea:#5AA79E; --sea-deep:#7BC2B8; --sea-soft:#1B302E;
    --lamp:#E0AE5A; --panel:rgba(12,18,19,.9);
    --glass:rgba(18,26,27,.72); --glass-line:rgba(255,255,255,.12);
    --shadow-m:0 1px 2px rgba(0,0,0,.25),0 20px 48px -30px rgba(0,0,0,.8);
  }
  .mi-landing *{box-sizing:border-box;margin:0;padding:0}
  
  .mi-landing{
    background:var(--bg);color:var(--fg);font-family:var(--font-sans);
    font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;
    transition:background .5s var(--ease),color .5s var(--ease);
  }
  .mi-landing button,.mi-landing input{font-family:inherit;font-size:inherit;color:inherit}
  .mi-landing button{border:none;background:none;cursor:pointer}
  .mi-landing input{border:none;outline:none;background:none}
  .mi-landing a{color:inherit;text-decoration:none}
  ::selection{background:rgba(46,110,104,.18)}
  .mi-landing :focus-visible{outline:2px solid var(--sea);outline-offset:3px;border-radius:6px}

  /* md 规范：整屏一个 Hero 区块，canvas 全视口铺底，内容浮在其上 */
  .mi-landing .page{position:relative;height:100vh;min-height:0;width:100%;overflow:hidden}
  .mi-landing #trail{position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;animation:canvasIn 2s ease-in-out both}
  @keyframes canvasIn{from{opacity:0}to{opacity:1}}

  /* ---------- 左：品牌与文案 ---------- */
  .mi-landing .left{--lift:0px;position:relative;z-index:10;display:flex;flex-direction:column;justify-content:space-between;
    padding:34px clamp(28px,4.4vw,72px) clamp(30px,4vw,56px);height:100vh;min-height:0;pointer-events:none}
  .mi-landing .left > *{pointer-events:auto}

  .mi-landing .brand{display:flex;align-items:center;gap:12px}
  .mi-landing .brand-mark{width:40px;height:40px;border-radius:13px;background:linear-gradient(150deg,#3B837C,#22524E);
    display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px -12px rgba(34,82,78,.9);flex:0 0 40px}
  .mi-landing .brand-name{font-family:var(--font-serif);font-size:19px;font-weight:600;letter-spacing:.16em;line-height:1.2}
  .mi-landing .brand-en{font-family:var(--font-display);font-style:italic;font-size:12px;color:var(--fg-3);letter-spacing:.14em;margin-top:1px}
  .mi-landing .brand-tag{margin-left:14px;font-size:11px;color:var(--fg-3);letter-spacing:.14em;padding-left:14px;border-left:1px solid var(--line)}

  /* 只用 transform 上移，不改字号/行高，也不影响 space-between 的分布 */
  .mi-landing .hero{max-width:700px;transform:translateY(calc(-1 * var(--lift)))}
  .mi-landing .eyebrow{font-size:11px;letter-spacing:.28em;color:var(--sea);font-weight:600;margin-bottom:20px}
  .mi-landing .hero-title{font-family:var(--font-serif);font-weight:500;letter-spacing:-.025em;line-height:1.04;margin-bottom:22px}
  .mi-landing .line-zh{display:block;font-size:clamp(67.2px,8.4vw,124.8px)}
  .mi-landing .line-en{display:block;font-family:var(--font-display);font-style:italic;font-weight:400;
    font-size:clamp(40px,5.2vw,76.8px);letter-spacing:-.01em;opacity:.42;
    transition:opacity .6s var(--ease);margin-top:2px}
  .mi-landing .line-en:hover{opacity:.95}
  .mi-landing .ltr{display:inline-block;opacity:0;animation:letterIn .62s cubic-bezier(.16,1,.3,1) both;
    animation-delay:calc(var(--i) * 30ms + 320ms)}
  @keyframes letterIn{from{opacity:0;transform:translateY(20px);filter:blur(5px)}to{opacity:1;transform:none;filter:blur(0)}}

  .mi-landing .slogan{font-family:var(--font-serif);font-size:clamp(17px,1.5vw,21px);font-weight:500;
    letter-spacing:.1em;color:var(--fg);margin-bottom:12px}
  .mi-landing .desc{font-size:13.5px;line-height:2;color:var(--fg-2);max-width:470px;letter-spacing:.02em}
  .mi-landing .tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}
  .mi-landing .tag{font-size:11.5px;letter-spacing:.06em;padding:5px 13px;border-radius:20px;
    border:1px solid var(--line);color:var(--fg-2);background:rgba(255,255,255,.42);
    backdrop-filter:blur(6px)}
  .mi-landing[data-theme="dark"] .tag{background:rgba(255,255,255,.04)}
  .mi-landing .tag::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;
    background:var(--sea);margin-right:7px;vertical-align:middle;opacity:.75}

  .mi-landing .actions{display:flex;align-items:center;gap:10px;margin-top:30px}
  .mi-landing .pill{height:38px;padding:0 22px;border-radius:99px;font-size:13px;font-weight:500;
    display:inline-flex;align-items:center;gap:8px;transition:all .3s var(--ease)}
  .mi-landing .pill-primary{background:var(--sea);color:#fff}
  .mi-landing[data-theme="dark"] .pill-primary{color:#0C1213}
  .mi-landing .pill-primary:hover{opacity:.9;transform:scale(1.02)}
  .mi-landing .pill-primary:active{transform:scale(.98)}
  .mi-landing .pill-ghost{border:1px solid var(--line);background:var(--surface);color:var(--fg-2)}
  .mi-landing .pill-ghost:hover{border-color:var(--sea);color:var(--fg)}

  .mi-landing .social{display:flex;align-items:center;gap:12px;margin-top:32px}
  .mi-landing .chips{display:flex;padding-left:2px}
  .mi-landing .chips svg{display:block;margin-left:-6px;filter:drop-shadow(0 2px 4px rgba(27,42,44,.12));border:2px solid var(--bg);border-radius:50%}
  .mi-landing .chips svg:first-child{margin-left:0}
  .mi-landing .social p{font-size:11.5px;color:var(--fg-3);letter-spacing:.03em}
  .mi-landing .social b{color:var(--fg-2);font-weight:600}

  .mi-landing [data-reveal]{opacity:0;animation:revealIn .95s var(--ease) both;
    animation-delay:calc(var(--d,0) * 130ms + 880ms)}
  @keyframes revealIn{from{opacity:0;transform:translateY(28px) scale(.97);filter:blur(6px)}
    to{opacity:1;transform:none;filter:blur(0)}}

  /* ---------- 右：登录区 ---------- */
  /* 登录板块 = 浮在全屏画布之上的玻璃卡片，而不是左右分栏 */
  .mi-landing .right{position:absolute;z-index:20;top:50%;right:clamp(28px,5.5vw,92px);
    transform:translateY(-50%);width:clamp(350px,30vw,432px);
    max-height:calc(100vh - 16px);overflow-y:auto;
    display:flex;flex-direction:column;gap:15px}
  .mi-landing .right::-webkit-scrollbar{width:0;height:0}
  .mi-landing .right-head{margin-bottom:2px;text-shadow:0 1px 14px var(--bg)}
  .mi-landing .rh-eyebrow{font-family:var(--font-display);font-style:italic;font-size:12px;
    letter-spacing:.18em;color:var(--sea);margin-bottom:6px}
  .mi-landing .right-head h2{font-family:var(--font-serif);font-size:25px;font-weight:600;letter-spacing:.05em}

  /* 固定最小高度：两种身份切换时卡片尺寸与位置都不跳，比例约 0.94（略竖向） */
  .mi-landing .card{background:var(--glass);border:1px solid var(--glass-line);border-radius:24px;
    min-height:456px;padding:30px 32px;
    box-shadow:0 28px 70px -34px rgba(27,42,44,.42),0 2px 10px rgba(27,42,44,.05);
    backdrop-filter:blur(26px) saturate(1.35);-webkit-backdrop-filter:blur(26px) saturate(1.35);
    transition:border-color .3s,box-shadow .3s,background .5s var(--ease)}
  .mi-landing[data-theme="dark"] .card{box-shadow:0 28px 70px -30px rgba(0,0,0,.85),0 2px 10px rgba(0,0,0,.3)}
  .mi-landing .card:hover{box-shadow:0 34px 80px -32px rgba(27,42,44,.48),0 2px 10px rgba(27,42,44,.06)}
  .mi-landing[data-theme="dark"] .card:hover{box-shadow:0 34px 80px -28px rgba(0,0,0,.9),0 2px 10px rgba(0,0,0,.35)}
  .mi-landing .card-head{margin-bottom:20px}
  .mi-landing .card-head h3{font-family:var(--font-serif);font-size:17px;font-weight:600;letter-spacing:.08em;
    display:flex;align-items:center;gap:9px}
  .mi-landing .card-head h3::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--sea)}

  /* 单卡片内的身份切换：用户登录（学生+咨询师） / 管理员 */
  .mi-landing .portal-switch{display:flex;gap:4px;background:var(--surface-2);border:1px solid var(--line-2);
    border-radius:12px;padding:4px;margin-bottom:20px}
  .mi-landing .portal{flex:1;height:36px;border-radius:9px;font-size:12.5px;letter-spacing:.04em;color:var(--fg-2);
    transition:.3s var(--ease);display:flex;align-items:center;justify-content:center;gap:7px}
  .mi-landing .portal .dot{width:6px;height:6px;border-radius:50%;background:var(--sea);opacity:.45;transition:.3s}
  .mi-landing .portal[data-portal="admin"] .dot{background:var(--lamp)}
  .mi-landing .portal.on{background:var(--surface);color:var(--sea-deep);font-weight:600;box-shadow:var(--shadow-s)}
  .mi-landing .portal.on .dot{opacity:1}
  .mi-landing .portal:hover:not(.on){color:var(--fg)}
  .mi-landing .card[data-mode="admin"]{border-color:rgba(217,152,47,.3)}
  .mi-landing .card[data-mode="admin"] .card-head h3::before{background:var(--lamp)}
  .mi-landing .card-swap{animation:cardSwap .42s var(--ease) both}
  @keyframes cardSwap{from{opacity:.35;transform:translateY(7px)}to{opacity:1;transform:none}}
  .mi-landing [hidden]{display:none !important}

  .mi-landing .field{display:block;margin-bottom:15px}
  .mi-landing .field > span{display:block;font-size:11.5px;color:var(--fg-2);letter-spacing:.06em;margin-bottom:7px}
  .mi-landing .input{width:100%;height:46px;padding:0 14px;border-radius:11px;
    border:1px solid var(--line);background:var(--surface-2);font-size:13.5px;
    transition:border-color .25s,box-shadow .25s,background .25s}
  .mi-landing .input::placeholder{color:var(--fg-3);opacity:.8}
  .mi-landing .input:focus{border-color:var(--sea);background:var(--surface);box-shadow:0 0 0 3px rgba(46,110,104,.1)}
  .mi-landing .pw-wrap{position:relative}
  .mi-landing .pw-wrap .input{padding-right:42px}
  .mi-landing .eye{position:absolute;right:6px;top:50%;transform:translateY(-50%);width:32px;height:32px;
    border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--fg-3)}
  .mi-landing .eye:hover{color:var(--fg);background:var(--surface-2)}

  .mi-landing .row{display:flex;align-items:center;justify-content:space-between;margin:4px 0 16px}
  .mi-landing .check{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--fg-2);cursor:pointer}
  .mi-landing .check input{appearance:none;width:15px;height:15px;border-radius:5px;border:1.5px solid var(--line);
    background:var(--surface-2);cursor:pointer;position:relative;transition:.2s}
  .mi-landing .check input:checked{background:var(--sea);border-color:var(--sea)}
  .mi-landing .check input:checked::after{content:"";position:absolute;left:4px;top:1px;width:4px;height:8px;
    border:solid #fff;border-width:0 2px 2px 0;transform:rotate(42deg)}
  .mi-landing .link{font-size:12px;color:var(--sea);transition:opacity .2s}
  .mi-landing .link:hover{opacity:.7;text-decoration:underline;text-underline-offset:3px}
  .mi-landing .submit{width:100%;height:46px;border-radius:11px;font-size:13.5px;font-weight:600;
    background:linear-gradient(160deg,#357B74,#22524E);color:#fff;letter-spacing:.1em;
    transition:.28s var(--ease);box-shadow:0 10px 24px -14px rgba(34,82,78,.9)}
  .mi-landing[data-theme="dark"] .submit{color:#0C1213}
  .mi-landing .submit:hover{transform:translateY(-1px);box-shadow:0 14px 30px -14px rgba(34,82,78,.85)}
  .mi-landing .submit:active{transform:translateY(0)}
  .mi-landing .submit.alt{background:linear-gradient(160deg,#E0AC57,#BE7C22);color:#fff;
    box-shadow:0 10px 24px -14px rgba(190,124,34,.9);letter-spacing:.05em}
  .mi-landing .submit.alt:hover{box-shadow:0 14px 30px -14px rgba(190,124,34,.85)}
  .mi-landing .reg{text-align:center;font-size:11.5px;color:var(--fg-3);margin-top:16px}

  .mi-landing .foot,.mi-landing .crisis{text-shadow:0 1px 12px var(--bg)}
  .mi-landing .foot{font-size:10.5px;color:var(--fg-3);text-align:center;letter-spacing:.04em;margin-top:6px}
  .mi-landing .crisis{font-size:10.5px;color:var(--fg-3);text-align:center;line-height:1.7;letter-spacing:.02em}

  /* 主题切换 */
  .mi-landing .theme-btn{position:fixed;top:24px;right:26px;z-index:40;width:36px;height:36px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;background:var(--surface);
    border:1px solid var(--line);color:var(--fg-2);box-shadow:var(--shadow-s);
    transition:.28s var(--ease)}
  .mi-landing .theme-btn:hover{color:var(--sea);transform:rotate(18deg)}
  .mi-landing .theme-btn svg{width:16px;height:16px}
  .mi-landing[data-theme="dark"] .icon-sun{display:none}
  .mi-landing[data-theme="light"] .icon-moon{display:none}

  .mi-landing .toast{position:fixed;left:50%;bottom:30px;transform:translate(-50%,18px);z-index:60;
    background:var(--fg);color:var(--bg);padding:10px 20px;border-radius:12px;font-size:12.5px;
    box-shadow:var(--shadow-m);opacity:0;pointer-events:none;transition:.35s var(--ease);
    display:flex;align-items:center;gap:9px;white-space:nowrap}
  .mi-landing .toast.show{opacity:1;transform:translate(-50%,0)}

  /* 「了解心屿」平台信息浮层：玻璃卡片停在中缝，自动收起，移入暂停 */
  .mi-landing .about{position:absolute;z-index:30;left:50%;top:50%;width:min(392px,calc(100% - 40px));
    padding:26px 28px 20px;background:rgba(255,255,255,.93);border:1px solid var(--glass-line);border-radius:24px;
    backdrop-filter:blur(26px);-webkit-backdrop-filter:blur(26px);
    box-shadow:0 30px 76px -34px rgba(27,42,44,.5),0 2px 10px rgba(27,42,44,.05);
    transform:translate(-50%,calc(-50% + 14px));opacity:0;pointer-events:none;
    transition:opacity .42s var(--ease),transform .42s var(--ease)}
  .mi-landing .about.show{opacity:1;transform:translate(-50%,-50%);pointer-events:auto}
  .mi-landing[data-theme="dark"] .about{background:rgba(20,29,30,.94);
    box-shadow:0 30px 76px -34px rgba(0,0,0,.9),0 2px 10px rgba(0,0,0,.3)}
  .mi-landing .about-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px}
  .mi-landing .about-eyebrow{font-family:var(--font-display);font-style:italic;font-size:11px;
    letter-spacing:.2em;color:var(--sea);margin-bottom:5px}
  .mi-landing .about h3{font-family:var(--font-serif);font-size:20px;font-weight:600;letter-spacing:.08em}
  .mi-landing .about-close{width:28px;height:28px;flex:0 0 28px;border-radius:9px;border:1px solid var(--line);
    display:flex;align-items:center;justify-content:center;color:var(--fg-3);transition:.25s var(--ease)}
  .mi-landing .about-close:hover{color:var(--fg);border-color:var(--sea);transform:rotate(90deg)}
  .mi-landing .about-intro{font-size:12.5px;line-height:1.95;color:var(--fg-2);letter-spacing:.02em;margin-bottom:16px}
  .mi-landing .about-list{list-style:none;margin:0 0 16px;padding:0;display:grid;gap:11px}
  .mi-landing .about-list li{display:flex;gap:10px;align-items:flex-start}
  .mi-landing .about-dot{width:7px;height:7px;border-radius:50%;background:var(--sea);flex:0 0 7px;margin-top:6px;opacity:.8}
  .mi-landing .about-list li:nth-child(2) .about-dot{background:var(--lamp)}
  .mi-landing .about-list li:nth-child(3) .about-dot{background:#6E915A}
  .mi-landing .about-list b{display:block;font-size:12.5px;font-weight:600;letter-spacing:.05em;color:var(--fg);margin-bottom:2px}
  .mi-landing .about-list span{display:block;font-size:11.5px;line-height:1.75;color:var(--fg-2)}
  .mi-landing .about-note{font-size:10.5px;line-height:1.8;color:var(--fg-2);letter-spacing:.02em;
    padding-top:12px;border-top:1px solid var(--line)}
  .mi-landing .about-timer{height:2px;border-radius:2px;background:var(--line-2);margin-top:14px;overflow:hidden}
  .mi-landing .about-timer i{display:block;height:100%;width:100%;border-radius:2px;
    background:linear-gradient(90deg,var(--sea),var(--lamp))}

  /* 宽屏时信息卡停在中缝，不遮左侧说明文字也不压登录卡片 */
  @media (min-width:1360px){
    .mi-landing .about{left:clamp(560px,50.8vw,740px);width:clamp(300px,25vw,368px)}
  }
  /* 桌面固定一屏：矮视口只压缩间距，字号一律不变 */
  /* 左侧内容随视口高度自适应上移，中心与右侧登录板块贴合；矮视口自动收敛 */
  @media (min-width:1001px) and (min-height:700px){
    .mi-landing .left{--lift:clamp(0px, calc(50vh - 272px), 220px)}
  }
  @media (min-width:1001px) and (max-height:699px){
    .mi-landing .left{--lift:16px}
  }
  @media (min-width:1001px) and (max-height:820px){
    .mi-landing .left{padding-top:24px;padding-bottom:24px}
    .mi-landing .hero-title{margin-bottom:14px}
    .mi-landing .slogan{margin-bottom:8px}
    .mi-landing .desc{line-height:1.85}
    .mi-landing .tags{margin-top:16px}
    .mi-landing .actions{margin-top:20px}
    .mi-landing .social{margin-top:18px}
    .mi-landing .right{gap:11px}
    .mi-landing .card{padding:22px 26px}
    .mi-landing .card-head{margin-bottom:14px}
    .mi-landing .portal-switch{margin-bottom:14px}
    .mi-landing .field{margin-bottom:11px}
    .mi-landing .row{margin:2px 0 10px}
    .mi-landing .reg{margin-top:12px}
  }
  @media (min-width:1001px) and (max-height:620px){
    .mi-landing .tags,.mi-landing .social{display:none}
    .mi-landing .hero-title{margin-bottom:10px}
    .mi-landing .actions{margin-top:16px}
  }
  /* 窄屏改为上下堆叠，卡片仍浮在画布之上 */
  @media (max-width:1000px){
    .mi-landing .page{height:auto;min-height:100vh;overflow:visible}
    .mi-landing .left{height:auto;min-height:0;padding:30px 28px 44px;gap:70px}
    .mi-landing .about{position:fixed;left:20px;right:20px;width:auto;
      transform:translateY(calc(-50% + 14px))}
    .mi-landing .about.show{transform:translateY(-50%)}
    .mi-landing .right{position:relative;top:auto;right:auto;transform:none;
      width:min(432px,calc(100% - 56px));max-height:none;overflow:visible;
      margin:0 auto 44px}
    .mi-landing .theme-btn{top:20px;right:20px}
  }
  @media (max-width:560px){
    .mi-landing .brand-tag{display:none}
    .mi-landing .actions{flex-wrap:wrap}
    .mi-landing .right{width:calc(100% - 40px)}
    .mi-landing .card{padding:24px 22px}
  }
  @media (prefers-reduced-motion:reduce){
    .mi-landing .ltr,.mi-landing [data-reveal]{animation-duration:.01ms;animation-delay:0s}
    .mi-landing #trail{animation:none}
  }

</style>
