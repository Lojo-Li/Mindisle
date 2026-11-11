<template>
<section class="view active" data-view="home" ref="rootEl" @click="onClick">

      <div class="page-head">
        <div>
          <h1 data-bind="greeting">下午好，林深</h1>
          <p>今天的心海，风平。要不要花三分钟，看看自己？</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost" data-go="booking">预约咨询</button>
        <button class="btn btn-primary" data-go="assess">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          开始一次测评
        </button>
      </div>

      <div class="mood-card">
        <div>
          <span class="mood-k">今天，你的心海是什么样子？</span>
          <span class="mood-hint" id="moodHint">点一下就好，不必准确。这一下只属于你。</span>
        </div>
        <div class="mood-dots" id="moodDots"></div>
      </div>

      <div class="grid-3">
        <div class="stat">
          <div class="glow"></div>
          <div class="k">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round"><path d="M3 17c3 0 4-6 6.5-6S13 17 16 17s3-5 5-5"/></svg>
            本周情绪均值
          </div>
          <div class="v"><span data-bind="moodScore">0</span><small>/ 100</small></div>
          <div class="d"><span class="trend-up">↑ 6</span> 较上周平稳回升</div>
        </div>
        <div class="stat">
          <div class="k">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M9.5 9h5M9.5 13h5"/></svg>
            已完成测评
          </div>
          <div class="v"><span data-bind="testCount">0</span><small>份</small></div>
          <div class="d"><span class="trend-up">本月 +3</span> 最近一次：GAD-7</div>
        </div>
        <div class="stat">
          <div class="k">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/></svg>
            下次咨询
          </div>
          <div class="v" style="font-size:23px" data-bind="nextAppointment">11月12日</div>
          <div class="d" data-bind="nextNote">陈曦 · 第 7 次 · 还剩 5 天</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card card-pad">
          <div class="card-head">
            <h3>情绪潮汐 · 近 7 天</h3>
            <button class="more" data-go="records">全部记录
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg>
            </button>
          </div>
          <div class="tide-wrap">
            <svg viewBox="0 0 600 170" width="100%" height="170" preserveAspectRatio="none">
              <defs>
                <linearGradient id="tideFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#2E6E68" stop-opacity=".16"/>
                  <stop offset="100%" stop-color="#2E6E68" stop-opacity="0"/>
                </linearGradient>
                <clipPath id="tideClip">
                  <path d="M40,66 C82,66 83,56 125,56 C167,56 168,70 210,70 C252,70 253,44 295,44 C337,44 338,51 380,51 C422,51 423,34 465,34 C507,34 508,42 550,42 L550,155 L40,155 Z"/>
                </clipPath>
              </defs>
              <line x1="20" y1="40" x2="580" y2="40" stroke="#EFEDE6" stroke-width="1"/>
              <line x1="20" y1="80" x2="580" y2="80" stroke="#EFEDE6" stroke-width="1"/>
              <line x1="20" y1="120" x2="580" y2="120" stroke="#EFEDE6" stroke-width="1"/>
              <path d="M40,66 C82,66 83,56 125,56 C167,56 168,70 210,70 C252,70 253,44 295,44 C337,44 338,51 380,51 C422,51 423,34 465,34 C507,34 508,42 550,42 L550,150 L40,150 Z" fill="url(#tideFill)"/>
              <path d="M40,66 C82,66 83,56 125,56 C167,56 168,70 210,70 C252,70 253,44 295,44 C337,44 338,51 380,51 C422,51 423,34 465,34 C507,34 508,42 550,42"
                transform="translate(0,4)" fill="none" stroke="#FFFFFF" stroke-width="3" opacity=".5" stroke-linecap="round"/>
              <g class="tide-ripples" clip-path="url(#tideClip)">
                <path class="tr1" d="M-160,96 Q-120,88 -80,96 T0,96 T80,96 T160,96 T240,96 T320,96 T400,96 T480,96 T560,96 T640,96 T720,96 T800,96"/>
                <path class="tr2" d="M-160,118 Q-120,108 -80,118 T0,118 T80,118 T160,118 T240,118 T320,118 T400,118 T480,118 T560,118 T640,118 T720,118 T800,118"/>
                <path class="tr3" d="M-160,140 Q-120,133 -80,140 T0,140 T80,140 T160,140 T240,140 T320,140 T400,140 T480,140 T560,140 T640,140 T720,140 T800,140"/>
              </g>
              <path d="M40,66 C82,66 83,56 125,56 C167,56 168,70 210,70 C252,70 253,44 295,44 C337,44 338,51 380,51 C422,51 423,34 465,34 C507,34 508,42 550,42"
                fill="none" stroke="#2E6E68" stroke-width="2.2" stroke-linecap="round"/>
              <path class="tide-glint" d="M40,66 C82,66 83,56 125,56 C167,56 168,70 210,70 C252,70 253,44 295,44 C337,44 338,51 380,51 C422,51 423,34 465,34 C507,34 508,42 550,42"
                fill="none" stroke="#A7DDD1" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="26 974" pathLength="1000"/>
              <circle cx="40" cy="66" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <circle cx="125" cy="56" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <circle cx="210" cy="70" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <circle cx="295" cy="44" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <circle cx="380" cy="51" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <circle cx="465" cy="34" r="4.5" fill="#2E6E68"/>
              <circle cx="465" cy="34" r="9" fill="#2E6E68" opacity=".14"/>
              <circle cx="550" cy="42" r="3.5" fill="#fff" stroke="#2E6E68" stroke-width="2"/>
              <line id="tideMark" x1="465" y1="18" x2="465" y2="150" stroke="#2E6E68" stroke-width="1" stroke-dasharray="3 4" class="tide-mark" style="opacity:0"/>
              <rect class="tide-hit" x="0" y="0" width="83" height="170" data-d="0" data-v="62"/>
              <rect class="tide-hit" x="83" y="0" width="85" height="170" data-d="1" data-v="70"/>
              <rect class="tide-hit" x="168" y="0" width="85" height="170" data-d="2" data-v="58"/>
              <rect class="tide-hit" x="253" y="0" width="85" height="170" data-d="3" data-v="80"/>
              <rect class="tide-hit" x="338" y="0" width="85" height="170" data-d="4" data-v="74"/>
              <rect class="tide-hit" x="423" y="0" width="85" height="170" data-d="5" data-v="88"/>
              <rect class="tide-hit" x="508" y="0" width="92" height="170" data-d="6" data-v="82"/>
            </svg>
            <div class="tide-tip" id="tideTip"></div>
            <div class="tide-legend">
              <span><i style="background:#2E6E68"></i>情绪能量 · 悬停查看每天</span>
              <span><i style="background:#D9982F"></i>11月3日 低谷 58 分（睡眠不足）</span>
            </div>
          </div>
        </div>

        <div class="card card-pad">
          <div class="card-head">
            <h3>接下来</h3>
            <button class="more" data-go="booking">管理</button>
          </div>
          <div class="tl" data-list="homeTests">
            <div class="tl-item now">
              <b>屿灯 · 晚间情绪回访</b>
              <span>今天 21:30 · 预计 5 分钟</span>
            </div>
            <div class="tl-item">
              <b>第 7 次咨询 · 陈曦</b>
              <span>11月12日 20:00 · 在线咨询</span>
            </div>
            <div class="tl-item">
              <b>GAD-7 复测提醒</b>
              <span>11月15日 · 距上次 14 天</span>
            </div>
          </div>
          <button class="btn btn-soft btn-sm" style="width:100%;margin-top:18px" data-go="lamp">
            现在和屿灯说说话
          </button>
        </div>
      </div>

      <div class="grid-3" style="margin-top:16px;align-items:start">
        <div class="card card-pad" style="grid-column:span 2">
          <div class="card-head">
            <h3>为你推荐</h3>
            <button class="more" data-go="assess">量表库</button>
          </div>
          <div class="scales" style="grid-template-columns:1fr 1fr">
            <div class="scale" data-scale="gad7" style="min-height:auto">
              <span class="tag sea">焦虑 · 7 题</span>
              <h4>GAD-7 焦虑自评</h4>
              <p>过去两周，你是否常感到紧张、难以放松？3 分钟看清焦虑的水位。</p>
              <div class="scale-foot">约 3 分钟 <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span></div>
            </div>
            <div class="scale" data-scale="phq9" style="min-height:auto">
              <span class="tag lamp">情绪 · 9 题</span>
              <h4>PHQ-9 情绪状态</h4>
              <p>兴趣减退、疲惫、低落——给你的情绪做一次温和的体检。</p>
              <div class="scale-foot">约 4 分钟 <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span></div>
            </div>
          </div>
        </div>
        <div class="card card-pad">
          <div class="card-head"><h3>屿灯说</h3></div>
          <p style="font-size:13px;color:var(--ink-2);line-height:1.9">
            「你上周提到，睡前脑子总是转个不停。要不要试试把明天的事写在纸上，交给明天？」
          </p>
          <div style="display:flex;align-items:center;gap:9px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line-2)">
            <div class="lamp-ava" style="width:28px;height:28px;border-radius:9px">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
            </div>
            <span style="font-size:11.5px;color:var(--ink-3)">2 小时前 · 来自昨晚的对话</span>
          </div>
        </div>
      </div>
    
</section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserStatistics } from '@/api/user'
import { getTestHistory } from '@/api/test'
import { getUserAppointments } from '@/api/counselor'
import { useUserStore } from '@/stores/user'
import { pickList, pickData, setText, setHtml, fmtDate, testTl, go, statusText } from '../workspace'
import { mountOverviewDecorations, animateNumber } from '../decorations'

const rootEl = ref(null)
const router = useRouter()
const userStore = useUserStore()
let disposeDecorations = null

function greeting() {
  const h = new Date().getHours()
  return h < 11 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
}

onMounted(async () => {
  const root = rootEl.value
  const info = userStore.userInfo || {}
  setText(root, '[data-bind="greeting"]', greeting() + '，' + (info.nickname || info.username || '朋友'))
  disposeDecorations = mountOverviewDecorations(root)
  try {
    const [s, h, a] = await Promise.all([
      getUserStatistics(),
      getTestHistory({ page: 1, page_size: 5 }),
      getUserAppointments({ page: 1, page_size: 10 })
    ])
    const st = pickData(s)
    const tests = pickList(h)
    animateNumber(root.querySelector('[data-bind="testCount"]'), st.test_count ?? tests.length)

    // 用最近一次测评的真实得分率，替代原先编造的「情绪分」
    const latest = tests[0]
    const rate = latest && latest.max_score
      ? Math.round((latest.total_score || 0) / latest.max_score * 100)
      : 0
    animateNumber(root.querySelector('[data-bind="moodScore"]'), rate)
    setText(root, '[data-bind="moodScoreLabel"]', latest ? '最近一次得分率' : '还没有测评')

    setHtml(root, '[data-list="homeTests"]', tests.length
      ? tests.map(testTl).join('')
      : '<div class="tl-item"><b>还没有测评记录</b></div>')
    const appts = pickList(a)
    const next = appts.find(x => ['pending', 'confirmed', 'in_progress'].includes(x.status))
    setText(root, '[data-bind="nextAppointment"]', next ? fmtDate(next.appointment_date) : '暂无安排')
    setText(root, '[data-bind="nextNote"]', next
      ? ((next.counselor && next.counselor.name) || '咨询师') + ' · ' + statusText(next.status)
      : '去预约一次咨询吧')
  } catch (e) {
    // 接口不可用时保留设计稿静态内容
  }
})

onUnmounted(() => { if (disposeDecorations) disposeDecorations() })

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}

</script>
