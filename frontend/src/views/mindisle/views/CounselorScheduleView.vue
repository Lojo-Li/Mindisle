<template>
<section class="view active" data-view="counselor-schedule">

  <div class="page-head">
    <div>
      <div class="eyebrow">Schedule</div>
      <h1>时段管理</h1>
      <p>发布你可接待的时段，来访者只能预约你发布过的时间。时段以 1 小时为单位。</p>
    </div>
    <div class="spacer"></div>
    <button class="btn btn-primary" @click="openDialog">发布时段</button>
  </div>

  <div class="filter-row">
    <span class="pill on" style="cursor:default">共 {{ slots.length }} 个时段</span>
    <span class="pill" style="cursor:default">可预约 {{ availableCount }}</span>
    <span class="pill" style="cursor:default">已预约 {{ bookedCount }}</span>
  </div>

  <div v-if="loading" class="doc"><p class="doc-bio">正在加载时段…</p></div>

  <div v-else-if="slots.length === 0" class="doc">
    <h4>还没有发布可预约时段</h4>
    <p class="doc-bio" style="margin-top:8px">点右上角「发布时段」，选好日期和起止时间即可。未发布排班时，来访者会看到默认的 09:00–18:00 时段。</p>
  </div>

  <div v-else class="doc">
    <div v-for="group in grouped" :key="group.date" class="day-group">
      <div class="day-title">{{ group.date }} <span>{{ group.weekday }}</span></div>
      <div class="slot-row" v-for="s in group.slots" :key="s.id">
        <span class="slot-time">{{ s.start_time }} – {{ s.end_time }}</span>
        <span class="tag" :class="s.status === 'available' ? 'sea' : ''">{{ statusText(s.status) }}</span>
        <button
          v-if="s.status === 'available'"
          class="btn btn-ghost btn-sm"
          style="margin-left:auto"
          @click="remove(s)"
        >删除</button>
        <span v-else style="margin-left:auto;font-size:11.5px;color:var(--ink-3)">被预约的时段需先取消预约</span>
      </div>
    </div>
  </div>

  <!-- 发布弹窗 -->
  <div class="overlay" :class="{ open: dialogOpen }">
    <div class="modal">
      <div class="modal-head">
        <div>
          <h3>发布可预约时段</h3>
          <p style="font-size:12px;color:var(--ink-3);margin-top:2px">需对齐整点，至少 1 小时；与已发布时段重叠的部分会自动跳过。</p>
        </div>
        <button class="close" @click="dialogOpen = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div v-for="(row, i) in draft" :key="i" class="draft-row">
          <input type="date" v-model="row.date" class="ctrl" />
          <select v-model="row.start" class="ctrl" style="width:96px">
            <option value="">开始</option>
            <option v-for="t in timeOptions" :key="'s'+t" :value="t">{{ t }}</option>
          </select>
          <span class="dash">—</span>
          <select v-model="row.end" class="ctrl" style="width:96px">
            <option value="">结束</option>
            <option v-for="t in timeOptions" :key="'e'+t" :value="t">{{ t }}</option>
          </select>
          <button class="btn btn-ghost btn-sm" :disabled="draft.length === 1" @click="draft.splice(i, 1)">删除</button>
        </div>

        <button class="btn btn-ghost btn-sm" style="margin-top:10px" @click="addRow">再添加一行</button>

        <div style="display:flex;gap:9px;margin-top:22px">
          <button class="btn btn-ghost" style="flex:1" @click="dialogOpen = false">取消</button>
          <button class="btn btn-primary" style="flex:1.4" :disabled="publishing" @click="submit">
            {{ publishing ? '发布中…' : '确认发布' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { publishScheduleSlots, getMyScheduleSlots, removeScheduleSlot } from '@/api/counselor'
import { toast } from '../workspace'

const slots = ref([])
const loading = ref(true)
const dialogOpen = ref(false)
const publishing = ref(false)
const draft = ref([])

const timeOptions = Array.from({ length: 14 }, (_, i) => `${String(i + 8).padStart(2, '0')}:00`)

const STATUS_TEXT = { available: '可预约', booked: '已被预约', disabled: '已停用' }
const statusText = (s) => STATUS_TEXT[s] || s

const availableCount = computed(() => slots.value.filter(s => s.status === 'available').length)
const bookedCount = computed(() => slots.value.filter(s => s.status === 'booked').length)

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const grouped = computed(() => {
  const map = new Map()
  for (const s of slots.value) {
    const key = String(s.slot_date || '').slice(0, 10)
    if (!map.has(key)) {
      const d = new Date(key + 'T00:00:00')
      map.set(key, { date: key, weekday: Number.isNaN(d.getTime()) ? '' : WEEKDAYS[d.getDay()], slots: [] })
    }
    map.get(key).slots.push(s)
  }
  return [...map.values()]
})

async function load() {
  loading.value = true
  try {
    slots.value = (await getMyScheduleSlots()).data || []
  } catch (e) {
    slots.value = []
    toast('时段加载失败')
  } finally {
    loading.value = false
  }
}

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function addRow() {
  draft.value.push({ date: draft.value[0]?.date || todayStr(), start: '', end: '' })
}

function openDialog() {
  draft.value = [{ date: todayStr(), start: '', end: '' }]
  dialogOpen.value = true
}

async function submit() {
  for (const r of draft.value) {
    if (!r.date) { toast('请选择日期'); return }
    if (!r.start || !r.end) { toast('请选择开始与结束时间'); return }
    if (r.end <= r.start) { toast('结束时间必须晚于开始时间'); return }
  }
  publishing.value = true
  try {
    const res = await publishScheduleSlots(draft.value.map(r => ({ date: r.date, start_time: r.start, end_time: r.end })))
    const d = res.data || {}
    if (d.created > 0) toast(`成功发布 ${d.created} 个时段`)
    if (d.conflicts && d.conflicts.length) {
      toast(`${d.skipped} 条被跳过：${d.conflicts[0]}`)
    }
    dialogOpen.value = false
    await load()
  } catch (e) {
    toast('发布失败')
  } finally {
    publishing.value = false
  }
}

async function remove(slot) {
  if (!window.confirm(`确定删除 ${slot.slot_date} ${slot.start_time}-${slot.end_time} 这个时段吗？`)) return
  try {
    await removeScheduleSlot(slot.id)
    toast('时段已删除')
    await load()
  } catch (e) {
    toast('删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.day-group { padding: 4px 0 10px; }
.day-group + .day-group { border-top: 1px solid var(--line-2); margin-top: 6px; padding-top: 14px; }
.day-title { font-size: 13px; font-weight: 600; color: var(--ink); margin-bottom: 8px; }
.day-title span { font-size: 11.5px; font-weight: 400; color: var(--ink-3); margin-left: 6px; }
.slot-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.slot-time { font-size: 12.5px; color: var(--ink-2); font-variant-numeric: tabular-nums; min-width: 118px; }
.draft-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.dash { color: var(--ink-3); }
.ctrl {
  border: 1px solid var(--line);
  background: var(--surface-2);
  border-radius: 10px;
  padding: 7px 10px;
  font-size: 12.5px;
  color: var(--ink);
  font-family: inherit;
  outline: none;
}
.ctrl:focus { border-color: #C6DAD6; background: var(--surface); }
</style>
