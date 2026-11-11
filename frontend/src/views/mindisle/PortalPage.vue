<template>
  <div class="mi-portal" ref="rootEl">
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

  <!-- ================= 侧栏 ================= -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M3 17.5c2.2 0 2.6-3.5 4.8-3.5s2.4 2.4 4.4 2.4 2.5-4.2 4.8-4.2c1.4 0 2.4.9 3 1.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
          <circle cx="16.6" cy="7" r="2.1" fill="#F6D08A"/>
        </svg>
      </div>
      <div class="brand-text">
        <b>心屿</b>
        <span>Mindisle</span>
      </div>
    </div>

    <nav class="nav">
      <button class="nav-item active" data-go="home">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z"/></svg>
        概览
      </button>
      <button class="nav-item" data-go="assess">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M9.5 9h5M9.5 13h5M9.5 17h3"/></svg>
        心理测评
      </button>
      <button class="nav-item" data-go="lamp">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
        屿灯 · 情绪支持
        <span class="badge">AI</span>
      </button>
      <button class="nav-item" data-go="booking">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/></svg>
        咨询预约
      </button>

      <div class="nav-label">我的</div>
      <button class="nav-item" data-go="records">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H19v3H6.5"/></svg>
        我的记录
      </button>
    </nav>

    <div class="sidebar-foot">
      <div class="divider"></div>
      <button class="user-card">
        <div class="avatar av-a">林<i class="mood-pip" id="userMoodPip"></i></div>
        <div class="user-meta">
          <b>林深</b>
          <span>已陪伴 128 天</span>
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round" style="margin-left:auto"><path d="M9 6l6 6-6 6"/></svg>
      </button>
    </div>
  </aside>

  <!-- ================= 主区 ================= -->
  <main class="main" id="main">

    <div class="topbar" id="topbar">
      <div class="crumb">心屿<b id="crumbNow">概览</b></div>
      <div class="top-actions">
        <div class="search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/></svg>
          <input placeholder="搜索量表、咨询师…">
        </div>
        <button class="icon-btn" title="消息">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 8-3 8h18s-3-1-3-8"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>
          <span class="pip"></span>
        </button>
        <button class="icon-btn" title="设置">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1A1.6 1.6 0 0 0 9 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1A1.6 1.6 0 0 0 4.6 9a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/></svg>
        </button>
      </div>
    </div>

    <!-- ---------- 概览 ---------- -->
    <section class="view active" data-view="home">
      <div class="page-head">
        <div>
          <h1>下午好，林深</h1>
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
          <div class="v"><span data-count="74">0</span><small>/ 100</small></div>
          <div class="d"><span class="trend-up">↑ 6</span> 较上周平稳回升</div>
        </div>
        <div class="stat">
          <div class="k">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M9.5 9h5M9.5 13h5"/></svg>
            已完成测评
          </div>
          <div class="v"><span data-count="12">0</span><small>份</small></div>
          <div class="d"><span class="trend-up">本月 +3</span> 最近一次：GAD-7</div>
        </div>
        <div class="stat">
          <div class="k">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94A4A6" stroke-width="2" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/></svg>
            下次咨询
          </div>
          <div class="v" style="font-size:23px">11月12日<small>周三 20:00</small></div>
          <div class="d">陈曦 · 第 7 次 · 还剩 5 天</div>
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
          <div class="tl">
            <div class="tl-item now">
              <b>屿灯 · 晚间情绪回访</b>
              <span>今天 21:30 · 预计 5 分钟</span>
            </div>
            <div class="tl-item">
              <b>第 7 次咨询 · 陈曦</b>
              <span>11月12日 20:00 · 视频咨询</span>
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

    <!-- ---------- 心理测评 ---------- -->
    <section class="view" data-view="assess">
      <div class="page-head">
        <div>
          <div class="eyebrow">Assessment</div>
          <h1>心理测评</h1>
          <p>用标准化量表，把你的内在状态变成可以看见的地图。所有结果仅你可见。</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost">测评历史</button>
      </div>

      <div class="filter-row">
        <button class="pill on">全部</button>
        <button class="pill">情绪状态</button>
        <button class="pill">焦虑压力</button>
        <button class="pill">睡眠</button>
        <button class="pill">关系</button>
        <button class="pill">人格与优势</button>
      </div>

      <div class="scales">
        <div class="scale" data-scale="phq9">
          <span class="tag lamp">情绪状态</span>
          <h4>PHQ-9 抑郁自评量表</h4>
          <p>国际通用的情绪状态筛查工具，评估过去两周的兴趣、精力与低落程度。</p>
          <div class="scale-foot">
            9 题 · 约 4 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
        <div class="scale" data-scale="gad7">
          <span class="tag sea">焦虑压力</span>
          <h4>GAD-7 焦虑自评量表</h4>
          <p>7 个问题，看清那些说不清来源的紧绷感到底处在什么水位。</p>
          <div class="scale-foot">
            7 题 · 约 3 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
        <div class="scale" data-scale="sleep">
          <span class="tag">睡眠</span>
          <h4>睡眠质量指数 PSQI</h4>
          <p>从入睡时间、夜醒次数到晨起感受，还原你真实的睡眠结构。</p>
          <div class="scale-foot">
            12 题 · 约 6 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
        <div class="scale" data-scale="pss">
          <span class="tag rose">焦虑压力</span>
          <h4>压力知觉量表 PSS-10</h4>
          <p>不是事件本身，而是你觉得「撑不撑得住」。评估主观压力负荷。</p>
          <div class="scale-foot">
            10 题 · 约 4 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
        <div class="scale" data-scale="map">
          <span class="tag sea">心屿原创</span>
          <h4>内在情绪图谱</h4>
          <p>不止一个分数。用 24 个问题绘出你的情绪地形：潮汐、暗礁与可以停靠的岸。</p>
          <div class="scale-foot">
            24 题 · 约 8 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
        <div class="scale" data-scale="rel">
          <span class="tag">关系</span>
          <h4>亲密关系满意度</h4>
          <p>你在一段关系里，是被滋养，还是一直在消耗？</p>
          <div class="scale-foot">
            16 题 · 约 5 分钟
            <span class="go-arrow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></span>
          </div>
        </div>
      </div>
    </section>

    <!-- ---------- 答题 ---------- -->
    <section class="view" data-view="assess-quiz">
      <div class="quiz-shell">
        <div class="quiz-top">
          <button class="icon-btn" id="quizBack" title="退出">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
          </button>
          <div class="quiz-progress"><i id="quizBar"></i></div>
          <div class="quiz-count"><span id="quizNow">1</span> / <span id="quizTotal">9</span></div>
        </div>
        <div class="quiz-card">
          <div class="quiz-q" id="quizName">PHQ-9 · 情绪状态</div>
          <div class="quiz-title" id="quizTitle">—</div>
          <div class="quiz-opts" id="quizOpts"></div>
        </div>
        <p style="text-align:center;font-size:12px;color:var(--ink-3);margin-top:18px">
          没有对错，选最接近「最近两周」真实感受的那一个就好。
        </p>
      </div>
    </section>

    <!-- ---------- 结果 ---------- -->
    <section class="view" data-view="assess-result">
      <div class="page-head">
        <div>
          <div class="eyebrow">Result</div>
          <h1>你的情绪水位</h1>
          <p>这不是诊断，只是一张此刻的地图。你可以带着它去找人聊聊。</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost" data-go="assess">返回量表库</button>
      </div>

      <div class="result-grid">
        <div class="ring-card">
          <div class="ring">
            <svg width="150" height="150">
              <circle cx="75" cy="75" r="62" fill="none" stroke="#EFEDE6" stroke-width="9"/>
              <circle id="ringStroke" cx="75" cy="75" r="62" fill="none" stroke="#2E6E68" stroke-width="9"
                stroke-linecap="round" stroke-dasharray="389.6" stroke-dashoffset="389.6"
                style="transition:stroke-dashoffset 1.1s cubic-bezier(.2,.8,.2,1)"/>
            </svg>
            <div class="num">
              <b id="resScore">0</b>
              <span>总分 / <span id="resMax">27</span></span>
            </div>
          </div>
          <div class="level-pill" id="resLevel" style="background:var(--lamp-soft);color:#8F6316">轻度</div>
          <p id="resSummary" style="font-size:12.5px;color:var(--ink-2);margin-top:14px;line-height:1.8">
            —
          </p>
        </div>

        <div class="stack">
          <div class="card card-pad">
            <div class="card-head"><h3>四个维度</h3><span style="font-size:11.5px;color:var(--ink-3);margin-left:auto">分数越高越需要注意</span></div>
            <div id="dims" style="display:flex;flex-direction:column;gap:15px"></div>
          </div>

          <div class="card card-pad" style="background:linear-gradient(150deg,#FDF9F0,#FFFFFF);border-color:#EFE4CE">
            <div class="card-head">
              <div class="lamp-ava" style="width:30px;height:30px;border-radius:10px">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
              </div>
              <h3>接下来可以做什么</h3>
            </div>
            <ul style="font-size:13px;color:var(--ink-2);line-height:2;padding-left:2px;list-style:none">
              <li style="display:flex;gap:8px"><span style="color:var(--sea)">·</span>把这份结果和屿灯聊聊，它会帮你拆解成具体的小步骤</li>
              <li style="display:flex;gap:8px"><span style="color:var(--sea)">·</span>如果分数持续偏高，建议预约一次专业咨询</li>
              <li style="display:flex;gap:8px"><span style="color:var(--sea)">·</span>14 天后回来复测一次，看曲线而不是看单点</li>
            </ul>
            <div style="display:flex;gap:9px;margin-top:18px">
              <button class="btn btn-primary btn-sm" style="flex:1" data-go="lamp">和屿灯聊聊</button>
              <button class="btn btn-ghost btn-sm" style="flex:1" data-go="booking">预约咨询师</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ---------- 屿灯 ---------- -->
    <section class="view" data-view="lamp">
      <div class="page-head" style="padding-bottom:18px">
        <div>
          <div class="eyebrow">AI Companion</div>
          <h1>屿灯</h1>
          <p>岛上那盏一直亮着的灯。不评判，不催促，你说多久都可以。</p>
        </div>
      </div>

      <div class="lamp-shell">
        <div class="sess-list">
          <div class="sess-label">今天</div>
          <div class="sess active">
            <b>睡前那些停不下来的念头</b>
            <span>刚刚</span>
          </div>
          <div class="sess">
            <b>工作汇报前的紧绷</b>
            <span>今天 09:12</span>
          </div>
          <div class="sess-label">过去 7 天</div>
          <div class="sess">
            <b>和朋友的那次不愉快</b>
            <span>昨天</span>
          </div>
          <div class="sess">
            <b>我好像很久没有开心过了</b>
            <span>11月3日</span>
          </div>
          <div class="sess">
            <b>关于「我够不够好」</b>
            <span>11月1日</span>
          </div>
        </div>

        <div class="chat">
          <div class="chat-head">
            <div class="lamp-ava">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
            </div>
            <div>
              <h4>屿灯</h4>
              <span><i></i>在线 · 正在听</span>
            </div>
            <button class="icon-btn" style="margin-left:auto" title="更多">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>
            </button>
          </div>

          <div class="chat-body" id="chatBody">
            <div class="msg ai">
              <div class="mini">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>
              </div>
              <div class="bubble">晚上好，林深。今天过得怎么样？
如果一时说不清楚，也可以只告诉我一个词。</div>
            </div>
            <div class="msg me">
              <div class="mini">林</div>
              <div class="bubble">有点累，说不上来为什么。事情其实都做完了。</div>
            </div>
            <div class="msg ai">
              <div class="mini">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>
              </div>
              <div class="bubble">"事情都做完了，却还是累"——这种累通常不是身体欠的觉，而是心里一直在待命。

你最近是不是很久没有那种"完全不用负责"的时刻了？</div>
            </div>
            <div class="msg me">
              <div class="mini">林</div>
              <div class="bubble">好像是。周末也总觉得该做点什么。</div>
            </div>
          </div>

          <div class="chat-foot">
            <div class="chips">
              <button class="chip" data-chip="我有点焦虑">我有点焦虑</button>
              <button class="chip" data-chip="我睡不好">我睡不好</button>
              <button class="chip" data-chip="觉得很空">觉得很空</button>
              <button class="chip" data-chip="今天还不错">今天还不错</button>
            </div>
            <div class="composer">
              <input id="chatInput" placeholder="写下此刻的感受，随便多少都行…">
              <button class="send" id="chatSend" title="发送">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12h14M12.5 5.5 19 12l-6.5 6.5"/></svg>
              </button>
            </div>
            <p style="font-size:11px;color:var(--ink-3);margin-top:10px;text-align:center">
              屿灯不是医生。如果你正处于危机中，请立即联系专业机构或拨打心理援助热线。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ---------- 预约 ---------- -->
    <section class="view" data-view="booking">
      <div class="page-head">
        <div>
          <div class="eyebrow">Consultation</div>
          <h1>咨询预约</h1>
          <p>找到那个让你觉得「可以说下去」的人。首次咨询可免费更换一次。</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost">我的预约</button>
      </div>

      <div class="filter-row">
        <button class="pill on">全部</button>
        <button class="pill">焦虑与压力</button>
        <button class="pill">情绪低落</button>
        <button class="pill">睡眠问题</button>
        <button class="pill">亲密关系</button>
        <button class="pill">青少年</button>
      </div>

      <div class="docs">
        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-a">陈</div>
            <div>
              <h4>陈曦
                <span class="tag sea" style="font-size:10px;padding:1.5px 7px">认证</span>
              </h4>
              <div class="sub">临床心理学硕士 · 8 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.9</div>
          </div>
          <div class="doc-tags">
            <span class="tag">焦虑</span><span class="tag">正念</span><span class="tag">情绪调节</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            擅长用认知行为与正念结合的方式，陪你把"停不下来的脑子"慢慢调慢。
          </p>
          <div class="doc-meta">
            <span>本周可约 4 个时段</span>
            <span class="avail ok" style="margin-left:auto">可预约</span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="陈曦">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-b">周</div>
            <div>
              <h4>周予安</h4>
              <div class="sub">国家二级心理咨询师 · 6 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.8</div>
          </div>
          <div class="doc-tags">
            <span class="tag">亲密关系</span><span class="tag">自我认同</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            相信关系里的痛，也要在关系里被修好。风格温和，擅长长程陪伴。
          </p>
          <div class="doc-meta">
            <span>本周可约 6 个时段</span>
            <span class="avail ok" style="margin-left:auto">可预约</span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="周予安">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-c">林</div>
            <div>
              <h4>林知夏
                <span class="tag lamp" style="font-size:10px;padding:1.5px 7px">精神科</span>
              </h4>
              <div class="sub">副主任医师 · 12 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 5.0</div>
          </div>
          <div class="doc-tags">
            <span class="tag">睡眠障碍</span><span class="tag">抑郁</span><span class="tag">药物评估</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            医学背景，适合症状较重或需要药物联合评估的情况。
          </p>
          <div class="doc-meta">
            <span>本周可约 2 个时段</span>
            <span class="avail ok" style="margin-left:auto">可预约</span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="林知夏">选择时段</button>
        </div>

        <div class="doc">
          <div class="doc-top">
            <div class="avatar av-d">苏</div>
            <div>
              <h4>苏漾</h4>
              <div class="sub">心理咨询师 · 4 年经验</div>
            </div>
            <div class="stars" style="margin-left:auto;font-size:11.5px">★ 4.7</div>
          </div>
          <div class="doc-tags">
            <span class="tag">学业压力</span><span class="tag">青少年</span>
          </div>
          <p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">
            和 12–22 岁的年轻人工作，懂那种"被期待推着走"的窒息感。
          </p>
          <div class="doc-meta">
            <span>本周可约 8 个时段</span>
            <span class="avail ok" style="margin-left:auto">可预约</span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="苏漾">选择时段</button>
        </div>
      </div>
    </section>

    <!-- ---------- 记录 ---------- -->
    <section class="view" data-view="records">
      <div class="page-head">
        <div>
          <div class="eyebrow">My Journey</div>
          <h1>我的记录</h1>
          <p>128 天，12 次测评，6 次咨询。变化是慢慢发生的。</p>
        </div>
      </div>

      <div class="grid-2" style="margin-top:0">
        <div class="card card-pad">
          <div class="card-head"><h3>测评历史</h3></div>
          <div class="tl">
            <div class="tl-item now">
              <b>GAD-7 焦虑自评 · 9 分</b>
              <span>11月1日 · 轻度 · 较上次 ↓ 3</span>
            </div>
            <div class="tl-item">
              <b>PHQ-9 情绪状态 · 11 分</b>
              <span>10月18日 · 中度 · 较上次 ↓ 2</span>
            </div>
            <div class="tl-item">
              <b>睡眠质量指数 PSQI · 8 分</b>
              <span>10月5日 · 睡眠质量欠佳</span>
            </div>
            <div class="tl-item">
              <b>内在情绪图谱 · 首次</b>
              <span>9月20日 · 已生成你的情绪地形</span>
            </div>
          </div>
        </div>

        <div class="stack">
          <div class="card card-pad">
            <div class="card-head"><h3>咨询历程</h3></div>
            <div class="tl">
              <div class="tl-item">
                <b>第 7 次 · 陈曦</b>
                <span>11月12日 20:00 · 待进行</span>
              </div>
              <div class="tl-item">
                <b>第 6 次 · 陈曦</b>
                <span>10月29日 · 已完成 · 咨询笔记已归档</span>
              </div>
              <div class="tl-item">
                <b>第 5 次 · 陈曦</b>
                <span>10月15日 · 已完成</span>
              </div>
            </div>
          </div>
          <div class="card card-pad" style="background:linear-gradient(150deg,#EEF6F3,#FFFFFF)">
            <div class="card-head"><h3>关于隐私</h3></div>
            <p style="font-size:12.5px;color:var(--ink-2);line-height:1.9">
              你的测评结果与对话内容加密存储，仅你本人与经你授权的咨询师可见。可随时导出或永久删除。
            </p>
          </div>
        </div>
      </div>
    </section>

  </main>
</div>

<!-- ================= 预约弹窗 ================= -->
<div class="overlay" id="bookOverlay">
  <div class="modal">
    <div class="modal-head">
      <div>
        <h3 id="bookTitle">预约 · 陈曦</h3>
        <p style="font-size:12px;color:var(--ink-3);margin-top:2px">50 分钟 · 视频咨询</p>
      </div>
      <button class="close" id="bookClose">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
    </div>
    <div class="modal-body">
      <div style="font-size:12px;color:var(--ink-3);margin-bottom:9px">选择日期</div>
      <div class="days" id="days"></div>
      <div style="font-size:12px;color:var(--ink-3);margin-bottom:9px">可约时段</div>
      <div class="slots" id="slots"></div>
      <div style="display:flex;gap:9px;margin-top:22px">
        <button class="btn btn-ghost" style="flex:1" id="bookCancel">取消</button>
        <button class="btn btn-primary" style="flex:1.4" id="bookConfirm">确认预约</button>
      </div>
      <p style="font-size:11px;color:var(--ink-3);margin-top:14px;text-align:center;line-height:1.8">
        需至少提前 15 分钟预约 · 公益免费，可随时取消
      </p>
    </div>
  </div>
</div>

<div class="toast" id="toast">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#8FD8C9" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
  <span id="toastText">已完成</span>
</div>
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

  /* ---------------- 路由 ---------------- */
  var mainEl = document.getElementById('main');
  var topbar = document.getElementById('topbar');
  var crumbNow = document.getElementById('crumbNow');

  var TITLES = {
    home:'概览', assess:'心理测评', 'assess-quiz':'答题中',
    'assess-result':'测评结果', lamp:'屿灯 · 情绪支持',
    booking:'咨询预约', records:'我的记录'
  };
  var NAVOF = { 'assess-quiz':'assess', 'assess-result':'assess' };

  function go(name){
    var views = rootEl.querySelectorAll('.view');
    for(var i=0;i<views.length;i++){
      views[i].classList.toggle('active', views[i].getAttribute('data-view')===name);
    }
    var navKey = NAVOF[name] || name;
    var items = rootEl.querySelectorAll('.nav-item');
    for(var j=0;j<items.length;j++){
      items[j].classList.toggle('active', items[j].getAttribute('data-go')===navKey);
    }
    crumbNow.textContent = TITLES[name] || '';
    mainEl.scrollTop = 0;
  }

  docOn('click', function(e){
    var t = e.target.closest('[data-go]');
    if(t){ go(t.getAttribute('data-go')); }
  });

  mainEl.addEventListener('scroll', function(){
    topbar.classList.toggle('scrolled', mainEl.scrollTop > 4);
  });

  /* ---------------- Toast ---------------- */
  var toastEl = document.getElementById('toast');
  var toastText = document.getElementById('toastText');
  var toastTimer = null;
  function toast(msg){
    toastText.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = trackTimeout(function(){ toastEl.classList.remove('show'); }, 2600);
  }

  /* ---------------- 测评数据 ---------------- */
  var PHQ9 = {
    name:'PHQ-9 · 情绪状态',
    max:27,
    questions:[
      '做事时提不起劲或没有兴趣',
      '感到心情低落、沮丧或绝望',
      '入睡困难、睡不安稳，或睡得太多',
      '感觉疲倦或没有活力',
      '食欲不振，或吃得太多',
      '觉得自己很糟，或觉得自己很失败，或让自己和家人失望',
      '难以集中注意力，比如看东西时总是走神',
      '动作或说话变慢到别人都察觉了；或者相反，变得烦躁、坐立不安',
      '有不如死掉、或用某种方式伤害自己的念头'
    ],
    options:['完全没有','有几天','一半以上的时间','几乎每天']
  };

  var GAD7 = {
    name:'GAD-7 · 焦虑自评',
    max:21,
    questions:[
      '感到紧张、焦虑或急切',
      '无法停止或控制担忧',
      '对各种各样的事情担忧过多',
      '很难放松下来',
      '由于坐立不安而难以静坐',
      '变得容易烦恼或易怒',
      '感到害怕，好像会有可怕的事情发生'
    ],
    options:['完全没有','有几天','一半以上的时间','几乎每天']
  };

  var SCALES = {
    phq9: PHQ9,
    gad7: GAD7,
    sleep:{
      name:'PSQI · 睡眠质量',
      max:21,
      questions:[
        '过去一周，你通常需要多久才能入睡',
        '夜里醒来的次数',
        '早上醒来后，感觉恢复得怎么样',
        '白天是否因为困倦而难以集中注意力',
        '是否因为睡不好而情绪变差',
        '是否依赖手机或其他方式才能入睡',
        '醒来后是否会反复查看时间'
      ],
      options:['没有困扰','偶尔','经常','几乎每天']
    },
    pss:{
      name:'PSS-10 · 压力知觉',
      max:30,
      questions:[
        '最近，你是否因为突发状况而感到心烦',
        '是否觉得事情超出自己的掌控',
        '是否感到紧张和压力大',
        '是否觉得自己无法应付所有必须做的事',
        '是否因为意外发生的事而生气'
      ],
      options:['从不','很少','有时','经常']
    },
    map:{
      name:'内在情绪图谱',
      max:30,
      questions:[
        '我能清楚说出自己此刻的情绪是什么',
        '难过的时候，我知道自己需要什么',
        '我允许自己有不好的状态',
        '我能感觉到身体在传递信号（紧绷、发沉）',
        '独处的时候，我感到安定而不是空'
      ],
      options:['完全不符合','比较不符合','比较符合','完全符合']
    },
    rel:{
      name:'亲密关系满意度',
      max:30,
      questions:[
        '在这段关系里，我可以做真实的自己',
        '我的感受会被认真对待',
        '我们冲突之后能够修复',
        '我不需要反复揣测对方的意思',
        '这段关系让我更有力量，而不是更疲惫'
      ],
      options:['完全不符合','比较不符合','比较符合','完全符合']
    }
  };

  /* ---------------- 答题逻辑 ---------------- */
  var quiz = { data:PHQ9, idx:0, answers:[], key:'phq9' };

  var quizTitle = document.getElementById('quizTitle');
  var quizOpts = document.getElementById('quizOpts');
  var quizNow = document.getElementById('quizNow');
  var quizTotal = document.getElementById('quizTotal');
  var quizBar = document.getElementById('quizBar');
  var quizName = document.getElementById('quizName');

  function startQuiz(key){
    var d = SCALES[key] || PHQ9;
    quiz = { data:d, idx:0, answers:[], key:key };
    quizName.textContent = d.name;
    quizTotal.textContent = d.questions.length;
    quizBar.style.width = '0%';
    renderQuestion();
    go('assess-quiz');
  }

  function renderQuestion(){
    var d = quiz.data, i = quiz.idx;
    quizNow.textContent = i + 1;
    quizTitle.textContent = d.questions[i];
    quizBar.style.width = Math.round((i / d.questions.length) * 100) + '%';

    var qc = document.querySelector('.quiz-card');
    qc.classList.remove('swap');
    void qc.offsetWidth;
    qc.classList.add('swap');

    quizOpts.innerHTML = '';
    d.options.forEach(function(label, score){
      var b = document.createElement('button');
      b.className = 'opt';
      b.innerHTML = '<span class="radio"></span><span>' + label + '</span>';
      if(quiz.answers[i] === score){ b.classList.add('sel'); }
      b.addEventListener('click', function(){
        quiz.answers[i] = score;
        var all = quizOpts.querySelectorAll('.opt');
        for(var k=0;k<all.length;k++){ all[k].classList.remove('sel'); }
        b.classList.add('sel');
        trackTimeout(function(){
          if(quiz.idx < d.questions.length - 1){
            quiz.idx++;
            renderQuestion();
          }else{
            showResult();
          }
        }, 260);
      });
      quizOpts.appendChild(b);
    });
  }

  document.getElementById('quizBack').addEventListener('click', function(){
    go('assess');
  });

  /* ---------------- 结果 ---------------- */
  var RING_C = 2 * Math.PI * 62;

  function showResult(){
    var d = quiz.data;
    var total = 0;
    for(var i=0;i<d.questions.length;i++){ total += (quiz.answers[i] || 0); }

    var maxPossible = (d.options.length - 1) * d.questions.length;
    var pct = total / maxPossible;
    var shownScore = Math.round(pct * d.max);

    countUp(document.getElementById('resScore'), shownScore, 1000);
    document.getElementById('resMax').textContent = d.max;

    var ring = document.getElementById('ringStroke');
    ring.style.strokeDasharray = RING_C;
    ring.style.strokeDashoffset = RING_C;
    trackTimeout(function(){
      ring.style.strokeDashoffset = RING_C * (1 - Math.max(pct, 0.04));
    }, 60);

    var levelEl = document.getElementById('resLevel');
    var summaryEl = document.getElementById('resSummary');
    var color, bg, label, text;

    if(pct < 0.2){
      color='#2E6E68'; bg='#E2EFEC'; label='平稳';
      text='你此刻的情绪水位是平稳的。继续保持那些让你感觉好的小事，也记得在平静里留意自己的需要。';
    }else if(pct < 0.45){
      color='#8F6316'; bg='#FAEFD7'; label='轻度';
      text='有一些轻微的波动，属于常见范围。它更像是一个提醒：最近可能有些东西被压得太久了。';
    }else if(pct < 0.7){
      color='#A8621F'; bg='#F8E7D6'; label='中度';
      text='情绪水位偏高，已经影响到日常的部分感受。这段时间值得被认真照顾，建议和屿灯聊聊，或预约一次咨询。';
    }else{
      color='#96574E'; bg='#F7E7E4'; label='偏重';
      text='这个分数说明你正在承受不小的重量。请不要独自扛着——尽快联系专业咨询师或医生，这是对自己负责的方式。';
    }
    levelEl.textContent = label;
    levelEl.style.color = color;
    levelEl.style.background = bg;
    summaryEl.textContent = text;
    ring.setAttribute('stroke', color);

    var dims = [
      { n:'情绪低落', v: Math.min(1, pct * (0.85 + Math.random()*0.4)) },
      { n:'兴趣与动力', v: Math.min(1, pct * (0.7 + Math.random()*0.5)) },
      { n:'睡眠与精力', v: Math.min(1, pct * (0.8 + Math.random()*0.45)) },
      { n:'专注与行动', v: Math.min(1, pct * (0.65 + Math.random()*0.55)) }
    ];
    var box = document.getElementById('dims');
    box.innerHTML = '';
    dims.forEach(function(dd){
      var val = Math.round(dd.v * 100);
      var wrap = document.createElement('div');
      wrap.innerHTML =
        '<div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:7px">' +
          '<span style="color:var(--ink-2)">' + dd.n + '</span>' +
          '<span style="color:var(--ink-3);font-variant-numeric:tabular-nums">' + val + '</span>' +
        '</div>' +
        '<div style="height:6px;border-radius:6px;background:var(--line-2);overflow:hidden">' +
          '<i style="display:block;height:100%;width:0;border-radius:6px;background:' + color +
          ';transition:width .9s cubic-bezier(.2,.8,.2,1)"></i>' +
        '</div>';
      box.appendChild(wrap);
      trackTimeout(function(){ wrap.querySelector('i').style.width = val + '%'; }, 80);
    });

    go('assess-result');
  }

  /* 量表卡片入口 */
  docOn('click', function(e){
    var card = e.target.closest('[data-scale]');
    if(card){ startQuiz(card.getAttribute('data-scale')); }
  });

  /* ---------------- 屿灯对话 ---------------- */
  var chatBody = document.getElementById('chatBody');
  var chatInput = document.getElementById('chatInput');
  var chatSend = document.getElementById('chatSend');
  var AI_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>';

  function scrollChat(){ chatBody.scrollTop = chatBody.scrollHeight; }

  function addMsg(who, text){
    var el = document.createElement('div');
    el.className = 'msg ' + who;
    el.innerHTML = who === 'ai'
      ? '<div class="mini">' + AI_ICON + '</div><div class="bubble">' + text + '</div>'
      : '<div class="mini">林</div><div class="bubble">' + text + '</div>';
    chatBody.appendChild(el);
    scrollChat();
  }

  function reply(text){
    var t = text || '';
    var pool;
    if(/睡|失眠|醒/.test(t)){
      pool = ['听起来，夜里那段时间对你不太好过。\n要不要试试：躺下后如果 20 分钟还醒着，就起来到别的地方坐一会儿，等困了再回床上。床只留给睡觉，这是有依据的做法。'];
    }else if(/累|疲|撑不住|耗尽/.test(t)){
      pool = ['你已经撑了很久了。\n累不是软弱，是身体在替你说话。今天能不能允许自己少做一件事？就一件。'];
    }else if(/焦虑|紧|慌|担心|害怕/.test(t)){
      pool = ['那种悬着的感觉，我懂。\n我们先做一件很小的事：说出此刻你能看到的三个东西、能摸到的两个东西。让身体先回到这个房间。'];
    }else if(/空|没意思|麻木|无聊/.test(t)){
      pool = ['"空"是一种很特别的难受，因为它连形状都没有。\n它常常出现在长期的紧绷之后。你最近是不是一直处在一个需要"表现正常"的位置上？'];
    }else if(/谢谢|好的|嗯/.test(t)){
      pool = ['不用谢。灯一直亮着，你随时可以回来。'];
    }else if(/不错|好多了|开心/.test(t)){
      pool = ['这很好。能感觉到"好"，说明你的感受力还在工作。\n愿意多说一点吗？是什么让今天不太一样？'];
    }else{
      pool = ['我在。慢慢说，不着急。',
              '嗯，我在听。\n如果你愿意，可以再说说那时候你身体的感受——是胸口发紧，还是肩膀沉？'];
    }
    var out = pool[Math.floor(Math.random() * pool.length)];

    var typing = document.createElement('div');
    typing.className = 'msg ai';
    typing.innerHTML = '<div class="mini">' + AI_ICON + '</div><div class="bubble typing"><i></i><i></i><i></i></div>';
    chatBody.appendChild(typing);
    scrollChat();

    trackTimeout(function(){
      typing.remove();
      addMsg('ai', out.replace(/\n/g, '<br>'));
    }, 1100);
  }

  function send(){
    var v = chatInput.value.trim();
    if(!v) return;
    addMsg('me', v);
    chatInput.value = '';
    reply(v);
  }

  chatSend.addEventListener('click', send);
  chatInput.addEventListener('keydown', function(e){
    if(e.key === 'Enter'){ e.preventDefault(); send(); }
  });

  var chips = rootEl.querySelectorAll('[data-chip]');
  for(var c=0;c<chips.length;c++){
    chips[c].addEventListener('click', function(){
      var v = this.getAttribute('data-chip');
      addMsg('me', v);
      reply(v);
    });
  }

  /* ---------------- 预约 ---------------- */
  var overlay = document.getElementById('bookOverlay');
  var daysBox = document.getElementById('days');
  var slotsBox = document.getElementById('slots');
  var bookTitle = document.getElementById('bookTitle');
  var booking = { doc:'陈曦', day:0, slot:'' };

  var WEEK = ['日','一','二','三','四','五','六'];
  var now = new Date(2026, 10, 7);
  var ALL_SLOTS = ['10:00','11:00','13:30','14:30','15:30','16:30','19:00','20:00','21:00'];

  function buildDays(){
    daysBox.innerHTML = '';
    for(var i=0;i<7;i++){
      var d = new Date(now.getTime());
      d.setDate(d.getDate() + i);
      var btn = document.createElement('button');
      btn.className = 'day' + (i === booking.day ? ' on' : '');
      btn.innerHTML = '<i>周' + WEEK[d.getDay()] + '</i><b>' + d.getDate() + '</b>';
      (function(idx){
        btn.addEventListener('click', function(){
          booking.day = idx;
          booking.slot = '';
          var all = daysBox.querySelectorAll('.day');
          for(var k=0;k<all.length;k++){ all[k].classList.remove('on'); }
          btn.classList.add('on');
          buildSlots();
        });
      })(i);
      daysBox.appendChild(btn);
    }
  }

  function buildSlots(){
    slotsBox.innerHTML = '';
    var taken = { 3:true, 6:true };
    if(booking.day === 0){ taken[0] = true; taken[1] = true; taken[2] = true; }
    if(booking.day === 5){ taken[4] = true; }

    ALL_SLOTS.forEach(function(s, idx){
      var b = document.createElement('button');
      b.className = 'slot';
      b.textContent = s;
      if(taken[idx]) b.disabled = true;
      if(booking.slot === s) b.classList.add('on');
      b.addEventListener('click', function(){
        booking.slot = s;
        var all = slotsBox.querySelectorAll('.slot');
        for(var k=0;k<all.length;k++){ all[k].classList.remove('on'); }
        b.classList.add('on');
      });
      slotsBox.appendChild(b);
    });
  }

  docOn('click', function(e){
    var b = e.target.closest('[data-book]');
    if(b){
      booking.doc = b.getAttribute('data-book');
      booking.day = 0;
      booking.slot = '';
      bookTitle.textContent = '预约 · ' + booking.doc;
      buildDays();
      buildSlots();
      overlay.classList.add('open');
    }
  });

  function closeBook(){ overlay.classList.remove('open'); }
  document.getElementById('bookClose').addEventListener('click', closeBook);
  document.getElementById('bookCancel').addEventListener('click', closeBook);
  overlay.addEventListener('click', function(e){ if(e.target === overlay) closeBook(); });

  document.getElementById('bookConfirm').addEventListener('click', function(){
    if(!booking.slot){ toast('请先选择一个时段'); return; }
    var d = new Date(now.getTime());
    d.setDate(d.getDate() + booking.day);
    var label = (d.getMonth()+1) + '月' + d.getDate() + '日 ' + booking.slot;
    closeBook();
    toast('已预约 ' + booking.doc + ' · ' + label);
  });

  /* ---------------- 水波与微交互 ---------------- */
  function countUp(el, target, dur){
    var start = null;
    function step(ts){
      if(start === null) start = ts;
      var p = Math.min(1, (ts - start) / dur);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if(p < 1) rafId = requestAnimationFrame(step);
    }
    rafId = requestAnimationFrame(step);
  }

  function initExtras(){

    /* 点击处扩散一圈涟漪 */
    docOn('pointerdown', function(e){
      var t = e.target.closest('.btn,.pill,.chip,.nav-item,.scale,.opt,.slot,.day,.icon-btn,.mood-dot');
      if(!t) return;
      var r = document.createElement('span');
      var s = Math.max(t.offsetWidth, t.offsetHeight) * 1.7;
      r.className = 'tap-ripple';
      r.style.width = r.style.height = s + 'px';
      r.style.left = e.clientX + 'px';
      r.style.top = e.clientY + 'px';
      document.body.appendChild(r);
      trackTimeout(function(){ r.remove(); }, 720);
    });

    /* 今日心情打卡 */
    var MOODS = [
      { n:'低落',   c:'#8A9BA6', t:'低落也是今天的一部分。谢谢你愿意说出来。' },
      { n:'有点沉', c:'#7FA9A4', t:'有点沉也没关系，慢慢来就好。' },
      { n:'平平',   c:'#9DB8AE', t:'平平的一天，也值得被记下。' },
      { n:'还行',   c:'#4E9287', t:'挺好的。记住这个感觉，下次可以回来找它。' },
      { n:'轻快',   c:'#D9982F', t:'轻快！屿灯帮你把今天收好了。' }
    ];
    var dots = document.getElementById('moodDots');
    MOODS.forEach(function(m){
      var b = document.createElement('button');
      b.className = 'mood-dot';
      b.innerHTML = '<i style="border-color:' + m.c + '"></i><span>' + m.n + '</span>';
      b.addEventListener('click', function(){
        var all = dots.querySelectorAll('.mood-dot');
        for(var k=0;k<all.length;k++){
          all[k].classList.remove('on');
          all[k].querySelector('i').style.background = 'transparent';
        }
        b.classList.add('on');
        b.querySelector('i').style.background = m.c;
        document.getElementById('moodHint').textContent = m.t;
        var pip = document.getElementById('userMoodPip');
        pip.style.background = m.c;
        pip.classList.add('lit');
        toast('已记下今天的心情 · ' + m.n);
      });
      dots.appendChild(b);
    });

    /* 概览数字滚动 */
    var counts = rootEl.querySelectorAll('[data-count]');
    for(var q=0;q<counts.length;q++){
      (function(el){ countUp(el, +el.getAttribute('data-count'), 1000); })(counts[q]);
    }

    /* 情绪潮汐：悬停读取当天数值 */
    var tip = document.getElementById('tideTip');
    var mark = document.getElementById('tideMark');
    var DAYS = ['11月1日','11月2日','11月3日','11月4日','11月5日','11月6日','11月7日'];
    var XS = [40,125,210,295,380,465,550];
    var hits = rootEl.querySelectorAll('.tide-hit');
    for(var h=0;h<hits.length;h++){
      (function(el){
        el.addEventListener('mouseenter', function(){
          var i = +el.getAttribute('data-d');
          var v = +el.getAttribute('data-v');
          tip.innerHTML = DAYS[i] + ' · 情绪能量 <b style="color:#8FD8C9">' + v + '</b>';
          tip.style.left = (XS[i] / 600 * 100) + '%';
          tip.style.top = (140 - v * 1.2) + 'px';
          tip.classList.add('show');
          mark.setAttribute('x1', XS[i]);
          mark.setAttribute('x2', XS[i]);
          mark.style.opacity = '1';
        });
        el.addEventListener('mouseleave', function(){
          tip.classList.remove('show');
          mark.style.opacity = '0';
        });
      })(hits[h]);
    }
  }

  /* ---------------- 初始化 ---------------- */
  go('home');
  initExtras();

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
.mi-portal .card { padding:0; border:0; border-radius:0; box-shadow:none; background:transparent; transition:none; }
.mi-portal .card:hover { transform:none; box-shadow:none; border-color:transparent; }

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

</style>
