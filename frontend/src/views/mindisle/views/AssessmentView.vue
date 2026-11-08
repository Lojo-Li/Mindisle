<template>
<section class="view active" data-view="assess" ref="rootEl" @click="onClick">

      <div class="page-head">
        <div>
          <div class="eyebrow">Assessment</div>
          <h1>心理测评</h1>
          <p>用标准化量表，把你的内在状态变成可以看见的地图。所有结果仅你可见。</p>
        </div>
        <div class="spacer"></div>
        <button class="btn btn-ghost">测评历史</button>
      </div>

      <div class="filter-row" data-list="filters">
        <button class="pill on">全部</button>
        <button class="pill">情绪状态</button>
        <button class="pill">焦虑压力</button>
        <button class="pill">睡眠</button>
        <button class="pill">关系</button>
        <button class="pill">人格与优势</button>
      </div>

      <div class="scales" data-list="scales">
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestList } from '@/api/test'
import { pickList, setHtml, scaleCard, filterPill, go, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
let all = []
let current = '全部'

onMounted(async () => {
  try {
    all = pickList(await getTestList({ page: 1, page_size: 50 }))
    const cats = ['全部'].concat(Array.from(new Set(all.map(t => t.category).filter(Boolean))))
    setHtml(rootEl.value, '[data-list="filters"]', cats.map(c => filterPill(c, c === '全部')).join(''))
    render()
  } catch (e) {
    toast('量表列表加载失败')
  }
})

function render() {
  const list = current === '全部' ? all : all.filter(t => t.category === current)
  setHtml(rootEl.value, '[data-list="scales"]', list.length
    ? list.map(scaleCard).join('')
    : '<div class="scale"><h4>暂无量表</h4></div>')
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const p = e.target.closest('[data-filter]')
  if (p) {
    current = p.getAttribute('data-filter')
    rootEl.value.querySelectorAll('[data-filter]').forEach(x => x.classList.toggle('on', x === p))
    render()
    return
  }
  const s = e.target.closest('[data-start]')
  if (s) router.push('/workspace/quiz/' + s.getAttribute('data-start'))
}

</script>
