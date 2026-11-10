<template>
<section class="view active" data-view="counselor-profile" ref="rootEl" @click="onClick">

  <div class="page-head">
    <div>
      <div class="eyebrow">Profile</div>
      <h1>个人中心</h1>
      <p>这里是你对外展示的咨询师资料，来访者会在咨询师详情页看到这些信息。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-ghost" data-logout>退出登录</button>
  </div>

  <div class="grid-2" style="margin-top:0">
    <div class="doc">
      <div class="doc-top">
        <div class="avatar av-a" style="width:56px;height:56px;flex:0 0 56px;font-size:20px">{{ initial }}</div>
        <div>
          <h4>{{ nickname }}<span class="tag sea" style="font-size:10px;padding:1.5px 7px">咨询师</span></h4>
          <div class="sub">{{ profile.title || '心理咨询师' }}<span v-if="profile.experience_years"> · {{ profile.experience_years }} 年经验</span></div>
        </div>
      </div>

      <div class="doc-tags">
        <span v-for="t in specialties" :key="t" class="tag">{{ t }}</span>
        <span v-if="specialties.length === 0" class="tag">暂未填写擅长领域</span>
      </div>

      <p class="doc-bio" style="-webkit-line-clamp:4;min-height:calc(1.75em * 4)">{{ profile.bio || '还没有填写个人简介，来访者了解你的第一入口就是这里。' }}</p>

      <div class="doc-meta">
        <span>公益免费 · 全部咨询不收费</span>
        <span class="avail" :class="profile.has_available_slot === false ? 'no' : 'ok'">
          {{ profile.has_available_slot === false ? '不可预约' : '可预约' }}
        </span>
      </div>
    </div>

    <div class="stack">
      <div class="doc">
        <div class="card-head"><h3>账号信息</h3></div>
        <div class="kv">
          <div class="kv-row"><span>登录邮箱</span><b>{{ account.email || '未填写' }}</b></div>
          <div class="kv-row"><span>联系方式</span><b>{{ account.phone || '未填写' }}</b></div>
          <div class="kv-row"><span>审核状态</span><b>{{ auditText }}</b></div>
        </div>
      </div>

      <div class="doc">
        <div class="card-head"><h3>咨询设置</h3></div>
        <div class="kv">
          <div class="kv-row"><span>咨询方式</span><b>{{ typeText }}</b></div>
          <div class="kv-row"><span>擅长领域</span><b>{{ specialties.join('、') || '未填写' }}</b></div>
          <div class="kv-row"><span>咨询费用</span><b>公益免费</b></div>
        </div>
        <p style="font-size:12px;color:var(--ink-3);margin-top:14px;line-height:1.8">
          资料更新请联系平台管理员，审核通过后会自动同步到咨询师列表。
        </p>
      </div>
    </div>
  </div>
</section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getApplicationStatus, getCounselorDetail } from '@/api/counselor'

const userStore = useUserStore()
const profile = ref({})
const status = ref({})

const account = computed(() => userStore.userInfo || {})
const nickname = computed(() => account.value.nickname || account.value.username || '咨询师')
const initial = computed(() => nickname.value.slice(0, 1))

const specialties = computed(() => {
  const s = profile.value.specialties || ''
  return String(s).split(/[,，、\s]+/).filter(Boolean)
})

const TYPE_LABEL = { video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }
const typeText = computed(() => {
  const t = String(profile.value.consultation_types || '').split(/[,，、\s]+/).filter(Boolean)
  return t.map(x => TYPE_LABEL[x] || x).join('、') || '未填写'
})

const AUDIT_LABEL = { pending: '审核中', approved: '已通过', rejected: '未通过' }
const auditText = computed(() => AUDIT_LABEL[status.value.application_status] || '未知')

function onClick(e) {
  if (e.target.closest('[data-logout]')) userStore.logout()
}

onMounted(async () => {
  try {
    status.value = (await getApplicationStatus()).data || {}
    if (status.value.counselor_id) {
      profile.value = (await getCounselorDetail(status.value.counselor_id)).data || {}
    }
  } catch (e) {
    // 资料加载失败不阻断页面
  }
})
</script>

<style scoped>
.kv { display: flex; flex-direction: column; gap: 12px; margin-top: 6px; }
.kv-row { display: flex; align-items: baseline; gap: 12px; font-size: 12.5px; }
.kv-row span { color: var(--ink-3); flex: 0 0 72px; }
.kv-row b { color: var(--ink); font-weight: 560; }
</style>
