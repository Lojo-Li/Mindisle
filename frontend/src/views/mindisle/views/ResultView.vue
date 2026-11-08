<template>
<section class="view active" data-view="assess-result" ref="rootEl" @click="onClick">

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
            <div id="dims" data-list="dims" style="display:flex;flex-direction:column;gap:15px"></div>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTestResult } from '@/api/test'
import { pickData, setText, setHtml, dimCard, go, toast } from '../workspace'

const rootEl = ref(null)
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  let d = null
  const cached = sessionStorage.getItem('mindisle_result')
  if (cached) {
    try { d = JSON.parse(cached) } catch (e) { d = null }
  }
  if (!d && route.params.id !== 'latest') {
    try { d = pickData(await getTestResult(route.params.id)) } catch (e) { d = null }
  }
  if (!d) {
    toast('暂无结果')
    router.push('/workspace/records')
    return
  }
  const root = rootEl.value
  setText(root, '#resScore', d.total_score ?? 0)
  setText(root, '#resMax', d.max_score || 100)
  setText(root, '#resLevel', d.result_level || d.result_title || '已完成')
  setText(root, '#resSummary', d.result_description || d.ai_suggestion || '')
  const stroke = root.querySelector('#ringStroke')
  if (stroke) {
    const max = Number(d.max_score || 100) || 100
    const ratio = Math.min(1, Number(d.total_score || 0) / max)
    stroke.style.strokeDashoffset = String(389.6 * (1 - ratio))
  }
  setHtml(root, '[data-list="dims"]', (d.dimension_scores || []).length
    ? d.dimension_scores.map(dimCard).join('')
    : '<div style="font-size:12px;color:var(--ink-3)">暂无维度数据</div>')
})

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}

</script>
