<template>
<section class="view active" data-view="records" ref="rootEl" @click="onClick">

      <div class="page-head">
        <div>
          <div class="eyebrow">My Journey</div>
          <h1>我的记录</h1>
          <p data-bind="recordsSummary">128 天，12 次测评，6 次咨询。变化是慢慢发生的。</p>
        </div>
      </div>

      <div class="grid-2" style="margin-top:0">
        <div class="card card-pad">
          <div class="card-head"><h3>测评历史</h3></div>
          <div class="tl" data-list="testHistory">
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
            <div class="tl" data-list="appointments">
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestHistory } from '@/api/test'
import { getUserAppointments } from '@/api/counselor'
import { pickList, setHtml, setText, testTl, apptTl, go } from '../workspace'

const rootEl = ref(null)
const router = useRouter()

onMounted(async () => {
  try {
    const [h, a] = await Promise.all([
      getTestHistory({ page: 1, page_size: 20 }),
      getUserAppointments({ page: 1, page_size: 20 })
    ])
    const tests = pickList(h)
    const appts = pickList(a)
    setText(rootEl.value, '[data-bind="recordsSummary"]',
      tests.length + ' 次测评，' + appts.length + ' 次咨询。变化是慢慢发生的。')
    setHtml(rootEl.value, '[data-list="testHistory"]', tests.length
      ? tests.map(testTl).join('')
      : '<div class="tl-item"><b>还没有测评记录</b></div>')
    setHtml(rootEl.value, '[data-list="appointments"]', appts.length
      ? appts.map(apptTl).join('')
      : '<div class="tl-item"><b>还没有咨询记录</b></div>')
  } catch (e) {
    // 接口不可用时保留设计稿静态内容
  }
})

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) go(g.getAttribute('data-go'), router)
}

</script>
