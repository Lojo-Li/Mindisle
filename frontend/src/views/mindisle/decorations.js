import { toast } from './workspace'

const MOODS = [
  { n: '低落', c: '#8A9BA6', t: '低落也是今天的一部分。谢谢你愿意说出来。' },
  { n: '有点沉', c: '#7FA9A4', t: '有点沉也没关系，慢慢来就好。' },
  { n: '平平', c: '#9DB8AE', t: '平平的一天，也值得被记下。' },
  { n: '还行', c: '#4E9287', t: '挺好的。记住这个感觉，下次可以回来找它。' },
  { n: '轻快', c: '#D9982F', t: '轻快！屿灯帮你把今天收好了。' }
]

function on(target, type, fn, cleanups) {
  target.addEventListener(type, fn)
  cleanups.push(() => target.removeEventListener(type, fn))
}

/** 外壳级装饰：点击涟漪（跨所有视图生效） */
export function mountShellDecorations() {
  const cleanups = []
  const onPointerDown = (e) => {
    const t = e.target.closest('.btn,.pill,.chip,.nav-item,.scale,.opt,.slot,.day,.icon-btn,.mood-dot')
    if (!t || !t.offsetWidth) return
    const r = document.createElement('span')
    const s = Math.max(t.offsetWidth, t.offsetHeight) * 1.7
    r.className = 'tap-ripple'
    r.style.width = r.style.height = s + 'px'
    r.style.left = e.clientX + 'px'
    r.style.top = e.clientY + 'px'
    // 挂到 .mi-portal 内，才能命中带作用域前缀的 .tap-ripple 样式
    const host = document.querySelector('.mi-portal') || document.body
    host.appendChild(r)
    setTimeout(() => r.remove(), 720)
  }
  on(document, 'pointerdown', onPointerDown, cleanups)
  return () => cleanups.forEach(fn => fn())
}

/** 概览视图装饰：心情打卡 + 情绪潮汐悬停读数 */
export function mountOverviewDecorations(root) {
  const cleanups = []
  const dots = root.querySelector('#moodDots')
  const hint = root.querySelector('#moodHint')

  if (dots) {
    dots.innerHTML = ''
    MOODS.forEach((m) => {
      const b = document.createElement('button')
      b.className = 'mood-dot'
      b.innerHTML = '<i style="border-color:' + m.c + '"></i><span>' + m.n + '</span>'
      const onClick = () => {
        dots.querySelectorAll('.mood-dot').forEach(x => {
          x.classList.remove('on')
          const i = x.querySelector('i')
          if (i) i.style.background = 'transparent'
        })
        b.classList.add('on')
        const bi = b.querySelector('i')
        if (bi) bi.style.background = m.c
        if (hint) hint.textContent = m.t
        const pip = document.getElementById('userMoodPip')
        if (pip) {
          pip.style.background = m.c
          pip.classList.add('lit')
        }
        toast('已记下今天的心情 · ' + m.n)
      }
      on(b, 'click', onClick, cleanups)
      dots.appendChild(b)
    })
  }

  const tip = root.querySelector('#tideTip')
  const mark = root.querySelector('#tideMark')
  const DAYS = ['11月1日', '11月2日', '11月3日', '11月4日', '11月5日', '11月6日', '11月7日']
  const XS = [40, 125, 210, 295, 380, 465, 550]

  root.querySelectorAll('.tide-hit').forEach((el) => {
    const enter = () => {
      const i = Number(el.getAttribute('data-d'))
      const v = Number(el.getAttribute('data-v'))
      if (tip) {
        tip.innerHTML = DAYS[i] + ' · 情绪能量 <b style="color:#8FD8C9">' + v + '</b>'
        tip.style.left = (XS[i] / 600 * 100) + '%'
        tip.style.top = (140 - v * 1.2) + 'px'
        tip.classList.add('show')
      }
      if (mark) {
        mark.setAttribute('x1', XS[i])
        mark.setAttribute('x2', XS[i])
        mark.style.opacity = '1'
      }
    }
    const leave = () => {
      if (tip) tip.classList.remove('show')
      if (mark) mark.style.opacity = '0'
    }
    on(el, 'mouseenter', enter, cleanups)
    on(el, 'mouseleave', leave, cleanups)
  })

  return () => cleanups.forEach(fn => fn())
}

/** 数字滚动（对应设计稿的 countUp），返回取消函数 */
export function animateNumber(el, target, dur = 1000) {
  if (!el) return () => {}
  const value = Number(target)
  if (!Number.isFinite(value)) {
    el.textContent = String(target)
    return () => {}
  }
  let start = null
  let raf = null
  const step = (ts) => {
    if (start === null) start = ts
    const p = Math.min(1, (ts - start) / dur)
    el.textContent = String(Math.round(value * (1 - Math.pow(1 - p, 3))))
    if (p < 1) raf = requestAnimationFrame(step)
  }
  raf = requestAnimationFrame(step)
  return () => { if (raf) cancelAnimationFrame(raf) }
}
