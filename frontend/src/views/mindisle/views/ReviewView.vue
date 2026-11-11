<template>
<section class="view active" data-view="review" ref="rootEl" @click="onClick">

  <div class="page-head">
    <div>
      <div class="eyebrow">Review</div>
      <h1>评价咨询</h1>
      <p>你的真实感受会帮助更多人找到合适的咨询师。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost btn-sm" data-back>返回</button>
  </div>

  <div v-if="loading" class="card card-pad empty-box">
    <h4>正在加载…</h4>
  </div>

  <div v-else-if="loadError" class="card card-pad empty-box">
    <h4>{{ loadError }}</h4>
    <button class="btn btn-ghost btn-sm" style="margin-top:16px" data-back>返回我的预约</button>
  </div>

  <div v-else class="rv-grid">
    <!-- 左栏：评分与评价 -->
    <div class="rv-main">
      <!-- 评分 -->
      <div class="card card-pad">
        <div class="card-head"><h3>总体评分</h3></div>
        <div class="stars-row">
          <button
            v-for="n in 5"
            :key="n"
            class="star"
            :class="{ on: n <= rating }"
            :data-star="n"
            :aria-label="n + ' 星'"
          >
            <svg width="30" height="30" viewBox="0 0 24 24" :fill="n <= rating ? 'currentColor' : 'none'"
                 stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
              <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/>
            </svg>
          </button>
          <span class="rating-text">{{ ratingText }}</span>
        </div>
      </div>

      <!-- 标签 -->
      <div class="card card-pad">
        <div class="card-head"><h3>满意度</h3><span class="more">可多选</span></div>
        <div class="tag-pick">
          <button
            v-for="t in TAG_OPTIONS"
            :key="t"
            class="pill"
          :class="{ on: tags.includes(t) }"
          :data-tag="t"
        >{{ t }}</button>
      </div>
    </div>

    <!-- 文字评价 -->
    <div class="card card-pad rv-grow">
      <div class="card-head"><h3>你的评价</h3><span class="more">{{ content.length }}/500</span></div>
      <textarea
        class="rv-textarea"
        v-model="content"
        rows="6"
        maxlength="500"
        placeholder="分享一下这次咨询的感受，你的经验会帮到其他人（选填）"
      ></textarea>
    </div>
    </div>

    <!-- 右栏：咨询信息 + 匿名 + 操作 -->
    <aside class="rv-side">
      <div class="card card-pad">
        <div class="card-head"><h3>本次咨询</h3><span class="tag sea">待评价</span></div>
        <div class="rv-head">
          <div class="avatar av-a">{{ (counselorName || '咨').slice(0, 1) }}</div>
          <div class="rv-info">
            <h4>{{ counselorName }}</h4>
            <div class="rv-sub">{{ typeText(appt.consultation_type) }} · 50 分钟</div>
          </div>
        </div>
        <div class="rv-meta">
          <div class="rv-row"><span>咨询时间</span><b>{{ fmtDate(appt.appointment_date) }}</b></div>
          <div class="rv-row"><span>咨询方式</span><b>{{ typeText(appt.consultation_type) }}</b></div>
          <div class="rv-row"><span>费用</span><b>公益免费</b></div>
        </div>
      </div>

      <div class="card card-pad">
        <div class="card-head"><h3>隐私设置</h3></div>
        <label class="anon-row" :data-anon="isAnonymous ? '1' : '0'" @click.prevent="toggleAnon">
          <span class="cb" :class="{ on: isAnonymous }">
            <svg v-if="isAnonymous" width="11" height="11" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 12.5l5 5L20 6.5"/>
            </svg>
          </span>
          <span>匿名评价</span>
        </label>
        <p class="rv-hint">开启后，你的昵称不会显示在咨询师主页的评价中。</p>
      </div>

      <div class="card card-pad rv-actions">
        <button class="btn btn-primary" :disabled="submitting" data-submit>
          {{ submitting ? '提交中…' : '提交评价' }}
        </button>
        <button class="btn btn-ghost" data-back>取消</button>
      </div>
    </aside>
  </div>

</section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getAppointmentDetail, submitReview } from '@/api/counselor'
import { toast, consultTypeText } from '../workspace'

const router = useRouter()
const route = useRoute()
const rootEl = ref(null)

const loading = ref(true)
const submitting = ref(false)
const loadError = ref('')
const appt = ref({})

const rating = ref(5)
const tags = ref([])
const content = ref('')
const isAnonymous = ref(false)

const TAG_OPTIONS = ['专业度高', '倾听耐心', '思路清晰', '氛围放松', '收获明显']

const RATING_TEXTS = ['', '非常不满意', '不太满意', '一般', '比较满意', '非常满意']
const ratingText = computed(() => RATING_TEXTS[rating.value] || '')

const counselorName = computed(() => {
  const c = appt.value.counselor
  return (c && c.name) || appt.value.counselor_name || '咨询师'
})

function typeText(t) {
  return consultTypeText(t)
}

function fmtDate(v) {
  if (!v) return ''
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v).replace('T', ' ').slice(0, 16)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    loadError.value = '缺少预约信息'
    loading.value = false
    return
  }
  try {
    const res = await getAppointmentDetail(id)
    appt.value = (res && res.data) || {}
    if (appt.value.status && appt.value.status !== 'completed') {
      loadError.value = '只有已完成的咨询才能评价（当前状态：' + statusText(appt.value.status) + '）'
    }
  } catch (e) {
    loadError.value = (e && e.response && e.response.data && e.response.data.detail) || '预约信息加载失败'
  } finally {
    loading.value = false
  }
})

function statusText(s) {
  const map = {
    pending: '待确认', confirmed: '已确认', in_progress: '进行中',
    completed: '已完成', cancelled: '已取消', refunded: '已退款'
  }
  return map[s] || s
}

function toggleAnon() {
  isAnonymous.value = !isAnonymous.value
}

function onClick(e) {
  if (e.target.closest('[data-back]')) {
    router.push('/workspace/appointments')
    return
  }

  const s = e.target.closest('[data-star]')
  if (s) {
    rating.value = Number(s.getAttribute('data-star'))
    return
  }

  const t = e.target.closest('[data-tag]')
  if (t) {
    const v = t.getAttribute('data-tag')
    const i = tags.value.indexOf(v)
    if (i >= 0) tags.value.splice(i, 1)
    else tags.value.push(v)
    return
  }

  if (e.target.closest('[data-submit]')) { doSubmit() }
}

async function doSubmit() {
  if (submitting.value) return
  if (!rating.value || rating.value < 1) {
    toast('请先选择评分')
    return
  }
  submitting.value = true
  try {
    await submitReview(route.params.id, {
      rating: Number(rating.value),
      tags: tags.value.slice(),
      content: content.value.trim() || null,
      is_anonymous: isAnonymous.value
    })
    toast('感谢你的评价')
    router.push('/workspace/appointments')
  } catch (e) {
    const d = e && e.response && e.response.data && e.response.data.detail
    toast(typeof d === 'string' ? d : ((e && e.message) || '提交失败，请稍后重试'))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* 两栏铺满可用宽度，与心屿 grid-2（1.55fr 1fr）保持一致，避免卡片孤零零地缩在左侧 */
.rv-grid { display: grid; grid-template-columns: 1.55fr 1fr; gap: 16px; align-items: stretch; }

/* 左栏与右栏等高：最后一张卡片（文字评价）自动撑满剩余高度，两栏底部严格对齐 */
.rv-main { display: flex; flex-direction: column; gap: 16px; }
.rv-main .rv-grow { flex: 1; display: flex; flex-direction: column; }
.rv-main .rv-grow .rv-textarea { flex: 1; min-height: 140px; }
.rv-side { display: flex; flex-direction: column; gap: 16px; }

/* 空态/加载态：与心屿其他页面的卡片空态保持一致 */
.empty-box { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 48px 24px; text-align: center; }
.empty-box h4 { font-size: 14px; font-weight: 500; color: var(--ink-2); }

/* 右侧咨询信息 */
.rv-head { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.rv-info h4 { font-size: 15px; font-weight: 500; }
.rv-sub { font-size: 12.5px; color: var(--ink-3); margin-top: 4px; }
.rv-head .tag { margin-left: auto; }

/* 咨询信息明细行 */
.rv-meta { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--line-2); display: flex; flex-direction: column; gap: 10px; }
.rv-row { display: flex; align-items: center; justify-content: space-between; font-size: 12.5px; }
.rv-row span { color: var(--ink-3); }
.rv-row b { color: var(--ink); font-weight: 500; font-variant-numeric: tabular-nums; }
.rv-hint { font-size: 11.5px; color: var(--ink-3); line-height: 1.7; margin-top: 10px; }

/* 星级 */
.stars-row { display: flex; align-items: center; gap: 6px; }
.star {
  color: var(--line);
  transition: color .16s var(--ease), transform .16s var(--ease);
  display: inline-flex;
  padding: 2px;
}
.star:hover { transform: scale(1.08); }
.star.on { color: var(--lamp); }
.rating-text {
  margin-left: 10px; font-size: 13px; color: var(--ink-2);
  font-weight: 520;
}

/* 标签多选 */
.tag-pick { display: flex; flex-wrap: wrap; gap: 8px; }

/* 文本框 */
.rv-textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 11px;
  padding: 13px 14px;
  font-family: inherit;
  font-size: 13.5px;
  line-height: 1.75;
  color: var(--ink);
  background: var(--surface-2);
  resize: vertical;
  transition: border-color .18s var(--ease), background .18s var(--ease);
  outline: none;
}
.rv-textarea:focus { border-color: var(--sea); background: var(--surface); }
.rv-textarea::placeholder { color: var(--ink-3); }

/* 匿名勾选 */
.anon-row {
  display: inline-flex; align-items: center; gap: 9px;
  font-size: 13px; color: var(--ink-2);
  cursor: pointer; user-select: none;
}
.cb {
  width: 17px; height: 17px; border-radius: 5px;
  border: 1.5px solid var(--line); background: var(--surface);
  display: inline-flex; align-items: center; justify-content: center;
  color: #fff; transition: all .16s var(--ease);
}
.cb.on { background: var(--sea); border-color: var(--sea); }

/* 右栏操作区：主按钮占满，次按钮在下 */
.rv-actions { display: flex; flex-direction: column; gap: 9px; }
.rv-actions .btn { width: 100%; height: 40px; }

@media (max-width: 1080px) {
  .rv-grid { grid-template-columns: 1fr; }
  .rv-side { position: static; }
}
</style>
