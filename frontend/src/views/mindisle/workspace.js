import { ElMessage } from 'element-plus'

export function pickList(res) {
  const d = res && res.data !== undefined ? res.data : res
  if (Array.isArray(d)) return d
  return (d && (d.items || d.list)) || []
}

export function pickData(res) {
  return (res && res.data) || {}
}

export function esc(s) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => map[c])
}

export function fmtDate(s) {
  if (!s) return '—'
  const d = new Date(s)
  if (isNaN(d.getTime())) return String(s)
  return (d.getMonth() + 1) + '月' + d.getDate() + '日'
}

export function setText(root, sel, value) {
  const el = root && root.querySelector(sel)
  if (el && value != null) el.textContent = String(value)
}

export function setHtml(root, sel, html) {
  const el = root && root.querySelector(sel)
  if (el) el.innerHTML = html
}

export function toast(msg) {
  const box = document.getElementById('toast')
  const text = document.getElementById('toastText')
  if (box && text) {
    text.textContent = msg
    box.classList.add('show')
    clearTimeout(toast._timer)
    toast._timer = setTimeout(() => box.classList.remove('show'), 2600)
  } else {
    ElMessage.success(msg)
  }
}

export const STATUS = {
  pending: '待确认', confirmed: '已确认', in_progress: '进行中',
  completed: '已完成', cancelled: '已取消', refunded: '已退款', rejected: '已拒绝'
}

export function statusText(s) {
  return STATUS[s] || s || '—'
}

export function go(view, router) {
  if (!view) return
  // 允许直接传绝对路径（如 /workspace/result/21）
  if (String(view).charAt(0) === '/') {
    router.push(String(view))
    return
  }
  const map = {
    home: '/workspace/home', assess: '/workspace/assess',
    'assess-quiz': '/workspace/assess', 'assess-result': '/workspace/records',
    lamp: '/workspace/lamp', booking: '/workspace/booking', records: '/workspace/records',
    trend: '/workspace/trend'
  }
  router.push(map[view] || '/workspace/home')
}

const ARROW = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg>'

const AI_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>'

export function scaleCard(t) {
  const cat = t.category || '心理测评'
  const tone = /焦虑|压力/.test(cat) ? 'rose' : /情绪|心情/.test(cat) ? 'lamp' : /人格|优势/.test(cat) ? 'sea' : ''
  return '<div class="scale" data-start="' + t.id + '">' +
    '<span class="tag ' + tone + '">' + esc(cat) + '</span>' +
    '<h4>' + esc(t.title) + '</h4>' +
    '<p>' + esc(t.description || t.intro_text || '') + '</p>' +
    '<div class="scale-foot">' + (t.total_questions || 0) + ' 题 · 约 ' + (t.avg_duration || 5) + ' 分钟' +
    '<span class="go-arrow">' + ARROW + '</span></div></div>'
}

export function docCard(c) {
  const price = c.price_video || c.price_voice || c.price_offline || 0
  const tags = String(c.specialties || '').split(/[,，、\s]+/).filter(Boolean).slice(0, 3)
  return '<div class="doc"><div class="doc-top">' +
    '<div class="avatar av-a">' + esc(String(c.name || '咨').slice(0, 1)) + '</div>' +
    '<div><h4>' + esc(c.name) + (c.is_verified ? '<span class="tag sea" style="font-size:10px;padding:1.5px 7px">认证</span>' : '') + '</h4>' +
    '<div class="sub">' + esc(c.title || '心理咨询师') + ' · ' + (c.experience_years || 0) + ' 年经验</div></div>' +
    '<div class="stars" style="margin-left:auto;font-size:11.5px">★ ' + (c.rating || '5.0') + '</div></div>' +
    '<div class="doc-tags">' + tags.map(x => '<span class="tag">' + esc(x) + '</span>').join('') + '</div>' +
    '<p style="font-size:12.5px;color:var(--ink-2);line-height:1.75">' + esc(c.bio || '愿意慢慢听你说。') + '</p>' +
    '<div class="doc-meta"><span>可预约咨询</span><span class="price">¥' + price + ' <small>/ 50 分钟</small></span></div>' +
    '<button class="btn btn-primary btn-sm" style="width:100%;margin-top:14px" data-book="' + c.id + '">选择时段</button></div>'
}

export function testTl(r, i) {
  // data-go 让记录项可点击回看详情（go() 已支持绝对路径）
  return '<div class="tl-item' + (i === 0 ? ' now' : '') + '" data-go="/workspace/result/' + (r.id || '') + '" style="cursor:pointer">' +
    '<b>' + esc(r.test_title || r.test_code || '心理测评') + ' · ' + (r.total_score ?? '—') + ' 分</b>' +
    '<span>' + fmtDate(r.created_at) + ' · ' + esc(r.result_title || r.result_level || '已完成') +
    (r.max_score ? ' · 得分率 ' + Math.round((r.total_score || 0) / r.max_score * 100) + '%' : '') +
    '</span></div>'
}

export function apptTl(a) {
  return '<div class="tl-item"><b>' + esc((a.counselor && a.counselor.name) || '咨询师') + ' · ' + statusText(a.status) + '</b>' +
    '<span>' + fmtDate(a.appointment_date) + ' · ' + esc(a.consultation_type || '') + '</span></div>'
}

export function sessCard(s, activeId) {
  return '<div class="sess' + (String(s.id) === String(activeId) ? ' active' : '') + '" data-sess="' + s.id + '">' +
    '<b>' + esc(s.title || s.last_message || '新对话') + '</b><span>' + fmtDate(s.updated_at || s.created_at) + '</span></div>'
}

export function msgCard(m) {
  const me = m.role === 'user'
  return '<div class="msg ' + (me ? 'me' : 'ai') + '"><div class="mini">' + (me ? '我' : AI_ICON) + '</div>' +
    '<div class="bubble">' + esc(m.content).replace(/\n/g, '<br>') + '</div></div>'
}

export function optCard(o) {
  return '<button class="opt" data-opt="' + esc(o.value) + '"><span class="radio"></span><span>' + esc(o.label) + '</span></button>'
}

export function filterPill(text, on) {
  return '<button class="pill' + (on ? ' on' : '') + '" data-filter="' + esc(text) + '">' + esc(text) + '</button>'
}

export function dimCard(d) {
  const max = Number(d.max_score || 0)
  const pct = max ? Math.min(100, Math.round((Number(d.score || 0) / max) * 100)) : 60
  return '<div><div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:7px">' +
    '<span style="color:var(--ink-2)">' + esc(d.dimension) + '</span>' +
    '<span style="color:var(--ink-3);font-variant-numeric:tabular-nums">' + esc(d.score) +
    (max ? '<span style="opacity:.6"> / ' + max + '</span>' : '') + '</span></div>' +
    '<div style="height:6px;border-radius:6px;background:var(--line-2);overflow:hidden">' +
    '<i style="display:block;height:100%;width:' + pct + '%;border-radius:6px;background:var(--sea)"></i></div></div>'
}

export function dayCard(d, i, on) {
  const W = ['日', '一', '二', '三', '四', '五', '六']
  return '<button class="day' + (on ? ' on' : '') + '" data-day="' + i + '"><i>周' + W[d.getDay()] + '</i><b>' + d.getDate() + '</b></button>'
}

export function slotCard(s, on) {
  return '<button class="slot' + (on ? ' on' : '') + '" data-slot="' + esc(s) + '">' + esc(s) + '</button>'
}
