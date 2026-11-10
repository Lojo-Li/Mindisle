<template>
  <section class="view active" data-view="trend" ref="rootEl">
    <div class="page-head">
      <div>
        <div class="eyebrow">My Journey</div>
        <h1>测评趋势</h1>
        <p>{{ subtitle }}</p>
      </div>
      <div class="spacer"></div>
      <select v-if="options.length > 1" v-model="activeId" @change="load" class="scale-select">
        <option v-for="o in options" :key="o.id" :value="o.id">{{ o.title }}（{{ o.count }} 次）</option>
      </select>
    </div>

    <div v-if="loading" class="card card-pad" style="text-align:center;color:var(--ink-3);font-size:12.5px">正在读取趋势…</div>

    <template v-else-if="points.length">
      <div class="grid-3" style="margin-bottom:16px">
        <div class="stat"><div class="k">测评次数</div><div class="v">{{ points.length }}<small>次</small></div><div class="d">{{ testTitle }}</div></div>
        <div class="stat"><div class="k">最近一次</div><div class="v">{{ latest.score }}<small>/ {{ maxScore || '—' }}</small></div><div class="d">{{ latest.title || latest.level }}</div></div>
        <div class="stat"><div class="k">较上次</div><div class="v" :style="{ color: deltaColor }">{{ deltaText }}</div><div class="d">越低越平稳</div></div>
      </div>

      <div class="card card-pad">
        <div class="card-head">
          <h3>得分率曲线</h3>
          <span style="font-size:11.5px;color:var(--ink-3);margin-left:auto">纵轴为得分率，跨满分可比</span>
        </div>
        <svg :viewBox="'0 0 ' + W + ' ' + H" style="width:100%;height:240px;display:block">
          <defs>
            <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="rgba(46,110,104,.18)" />
              <stop offset="100%" stop-color="rgba(46,110,104,0)" />
            </linearGradient>
          </defs>
          <g>
            <line v-for="(g, i) in grid" :key="'g' + i" :x1="PAD.l" :x2="W - PAD.r" :y1="g.y" :y2="g.y"
                  stroke="#EFEDE6" stroke-width="1" stroke-dasharray="3 5" />
          </g>
          <path :d="areaPath" fill="url(#trendFill)" />
          <path :d="linePath" fill="none" stroke="#2E6E68" stroke-width="2" stroke-linejoin="round" />
          <g v-for="(p, i) in plotted" :key="'p' + i">
            <circle :cx="p.x" :cy="p.y" :r="i === plotted.length - 1 ? 5 : 3.4" fill="#fff" stroke="#2E6E68" stroke-width="2"
                    style="cursor:pointer" @click="openResult(points[i])" />
          </g>
        </svg>
        <div style="display:flex;justify-content:space-between;font-size:10.5px;color:var(--ink-3);padding:0 8px">
          <span v-for="p in points" :key="'x' + p.id">{{ p.date.slice(5) }}</span>
        </div>
      </div>

      <div class="card card-pad" style="margin-top:16px">
        <div class="card-head">
          <h3>逐次记录</h3>
          <span style="font-size:11.5px;color:var(--ink-3);margin-left:auto">点击查看该次结果</span>
        </div>
        <div class="tl" style="max-height:none">
          <div v-for="(p, i) in descPoints" :key="p.id" class="tl-item" style="cursor:pointer" @click="openResult(p)">
            <b>{{ p.date }} · {{ p.score }} 分<i v-if="maxScore" style="font-style:normal;opacity:.6"> / {{ maxScore }}</i></b>
            <span>得分率 {{ p.rate ?? '—' }}% · {{ p.title || p.level }}
              <em v-if="i < descPoints.length - 1" style="font-style:normal;color:var(--ink-3)">
                （较上次 {{ diffOf(p) }}）
              </em>
            </span>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="card card-pad" style="text-align:center;color:var(--ink-3);font-size:12.5px">
      <p style="margin-bottom:14px">这个量表还没有足够的历史数据</p>
      <button class="btn btn-primary btn-sm" @click="$router.push('/workspace/assess')">去做一次测评</button>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTestTrend, getTestHistory } from '@/api/test'
import { toast } from '@/views/mindisle/workspace'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const points = ref([])
const maxScore = ref(null)
const testTitle = ref('')
const options = ref([])
const activeId = ref(route.params.id || '')

const W = 720
const H = 220
const PAD = { l: 34, r: 14, t: 16, b: 18 }

const subtitle = computed(() =>
  testTitle.value ? testTitle.value + ' · 多次测评的变化' : '多次测评的变化，用来观察而不是评判'
)

const latest = computed(() => points.value[points.value.length - 1] || {})
const descPoints = computed(() => points.value.slice().reverse())

const deltaText = computed(() => {
  const n = points.value.length
  if (n < 2) return '首次记录'
  const d = points.value[n - 1].score - points.value[n - 2].score
  return d === 0 ? '持平' : (d > 0 ? '↑ ' : '↓ ') + Math.abs(d) + ' 分'
})
const deltaColor = computed(() => {
  const n = points.value.length
  if (n < 2) return 'var(--ink)'
  const d = points.value[n - 1].score - points.value[n - 2].score
  return d > 0 ? '#C4746A' : d < 0 ? '#4F8F6F' : 'var(--ink)'
})

const grid = computed(() => [0, 1, 2, 3, 4].map(i => ({ y: PAD.t + (H - PAD.t - PAD.b) * i / 4 })))

const plotted = computed(() => {
  const n = points.value.length
  const innerW = W - PAD.l - PAD.r
  const innerH = H - PAD.t - PAD.b
  return points.value.map((p, i) => {
    const x = n === 1 ? PAD.l + innerW / 2 : PAD.l + innerW * i / (n - 1)
    const ratio = Math.min(1, Math.max(0, (p.rate == null ? 0 : p.rate) / 100))
    return { x, y: PAD.t + innerH * (1 - ratio) }
  })
})

const linePath = computed(() => {
  const pts = plotted.value
  if (!pts.length) return ''
  if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`
  let d = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i]
    const p1 = pts[i]
    const p2 = pts[i + 1]
    const p3 = pts[i + 2] || p2
    const c1x = p1.x + (p2.x - p0.x) / 6
    const c1y = p1.y + (p2.y - p0.y) / 6
    const c2x = p2.x - (p3.x - p1.x) / 6
    const c2y = p2.y - (p3.y - p1.y) / 6
    d += ` C ${c1x} ${c1y}, ${c2x} ${c2y}, ${p2.x} ${p2.y}`
  }
  return d
})

const areaPath = computed(() => {
  const pts = plotted.value
  if (!pts.length) return ''
  const base = H - PAD.b
  return `${linePath.value} L ${pts[pts.length - 1].x} ${base} L ${pts[0].x} ${base} Z`
})

function diffOf(p) {
  const idx = points.value.findIndex(x => x.id === p.id)
  if (idx <= 0) return '首次'
  const d = p.score - points.value[idx - 1].score
  return d === 0 ? '持平' : (d > 0 ? '↑' : '↓') + Math.abs(d)
}

function openResult(p) {
  if (p && p.id) router.push('/workspace/result/' + p.id)
}

async function load() {
  loading.value = true
  try {
    let id = activeId.value || route.params.id

    // 没有指定量表时，用最近有记录的那个量表作为默认
    if (!id) {
      const h0 = await getTestHistory({ page: 1, page_size: 100 })
      const hist0 = ((h0 && h0.data) || {}).items || []
      if (!hist0.length) {
        points.value = []
        return
      }
      id = hist0[0].test_id
      activeId.value = id
    }

    const [t, h] = await Promise.all([
      getTestTrend(id),
      getTestHistory({ page: 1, page_size: 100 })
    ])
    const body = (t && t.data) || {}
    testTitle.value = body.test_title || ''
    maxScore.value = body.max_score || null
    points.value = (body.points || []).map(p => ({
      id: p.id,
      date: p.datetime ? p.datetime.slice(0, 10) : p.date,
      score: p.score,
      rate: p.rate,
      level: p.level,
      title: p.title
    }))

    const hist = ((h && h.data) || {}).items || []
    const map = new Map()
    hist.forEach(it => {
      const cur = map.get(it.test_id) || { id: it.test_id, title: it.test_title, count: 0 }
      cur.count += 1
      map.set(it.test_id, cur)
    })
    options.value = Array.from(map.values())
  } catch (e) {
    toast('趋势数据加载失败')
    points.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.scale-select {
  height: 34px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fff;
  font-size: 12.5px;
  color: var(--ink);
  outline: none;
}
</style>
