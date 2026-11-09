<template>
  <div class="risk-manage">
    <div class="page-header">
      <h2>风险工单</h2>
      <p class="sub">AI 识别到的危险信号会在这里排队，需要有人跟进处置。</p>
    </div>

    <!-- 概览 -->
    <div class="stat-row">
      <div class="stat-card">
        <span class="stat-label">累计事件</span>
        <span class="stat-value">{{ stats.total }}</span>
      </div>
      <div class="stat-card warn">
        <span class="stat-label">待处理</span>
        <span class="stat-value">{{ stats.pending }}</span>
      </div>
      <div class="stat-card danger">
        <span class="stat-label">L3 紧急</span>
        <span class="stat-value">{{ stats.by_level?.['3'] || 0 }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">近 7 天</span>
        <span class="stat-value">{{ weekTotal }}</span>
      </div>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="风险等级">
          <el-select v-model="query.level" placeholder="全部" clearable style="width: 140px">
            <el-option label="L3 紧急" :value="3" />
            <el-option label="L2 警示" :value="2" />
            <el-option label="L1 关注" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置状态">
          <el-select v-model="query.handled_status" placeholder="全部" clearable style="width: 140px">
            <el-option label="待处理" value="pending" />
            <el-option label="已联系" value="contacted" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="等级" width="110">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)" size="small" effect="dark">
              {{ row.level_label || `L${row.level}` }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="用户" width="160" />
        <el-table-column prop="keywords" label="命中信号" min-width="180">
          <template #default="{ row }">
            <span class="keywords">{{ row.keywords || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="action_taken" label="已执行动作" min-width="180">
          <template #default="{ row }">
            <span class="actions">{{ prettyActions(row.action_taken) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.handled_status)" size="small">
              {{ statusLabel(row.handled_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="触发时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="openHandle(row)">处置</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !list.length" description="暂无风险事件" :image-size="90" />

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="loadList"
        @current-change="loadList"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" title="处置风险事件" width="480px">
      <div v-if="current" class="handle-body">
        <div class="handle-row">
          <span class="handle-label">等级</span>
          <el-tag :type="levelType(current.level)" size="small" effect="dark">
            {{ current.level_label || `L${current.level}` }}
          </el-tag>
        </div>
        <div class="handle-row">
          <span class="handle-label">命中信号</span>
          <span>{{ current.keywords || '—' }}</span>
        </div>
        <div class="handle-row">
          <span class="handle-label">处置结果</span>
          <el-radio-group v-model="handleForm.handled_status">
            <el-radio value="contacted">已联系</el-radio>
            <el-radio value="closed">已关闭</el-radio>
            <el-radio value="pending">退回待处理</el-radio>
          </el-radio-group>
        </div>
        <div class="handle-row column">
          <span class="handle-label">处置备注</span>
          <el-input
            v-model="handleForm.note"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="例如：已电话联系，用户表示情绪稳定，建议持续跟进"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitHandle">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRiskEvents, getRiskStats, handleRiskEvent } from '@/api/aiSupport'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])
const total = ref(0)
const stats = ref({ total: 0, pending: 0, by_level: {}, last_7_days: [] })

const query = reactive({
  level: null,
  handled_status: null,
  page: 1,
  page_size: 10
})

const dialogVisible = ref(false)
const current = ref(null)
const handleForm = reactive({ handled_status: 'contacted', note: '' })

const weekTotal = computed(() =>
  (stats.value.last_7_days || []).reduce((sum, d) => sum + (d.count || 0), 0)
)

const levelType = (level) => (level >= 3 ? 'danger' : level === 2 ? 'warning' : 'info')
const statusType = (s) => (s === 'pending' ? 'danger' : s === 'contacted' ? 'warning' : 'success')
const statusLabel = (s) => ({ pending: '待处理', contacted: '已联系', closed: '已关闭' }[s] || s)

const ACTION_LABELS = {
  gentle_hint: '轻提示',
  self_help_card: '自助卡',
  banner: '警示横幅',
  hotline_card: '热线卡片',
  appointment_cta: '预约入口',
  notify_counselor: '通知咨询师',
  blocking_dialog: '阻塞弹层',
  hotline_call: '一键拨号',
  human_handover: '转人工',
  force_record: '强制留痕',
  notify_admin: '通知管理员'
}

const prettyActions = (s) => {
  if (!s) return '—'
  return s.split(',').map((a) => ACTION_LABELS[a] || a).join(' · ')
}

const formatDate = (v) => {
  if (!v) return '—'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return v
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await getRiskEvents({
      level: query.level || undefined,
      handled_status: query.handled_status || undefined,
      page: query.page,
      page_size: query.page_size
    })
    list.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('加载风险工单失败', e)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await getRiskStats()
    stats.value = res.data || stats.value
  } catch (e) {
    console.error('加载风险统计失败', e)
  }
}

const handleSearch = () => {
  query.page = 1
  loadList()
}

const handleReset = () => {
  query.level = null
  query.handled_status = null
  query.page = 1
  loadList()
}

const openHandle = (row) => {
  current.value = row
  handleForm.handled_status = row.handled_status === 'pending' ? 'contacted' : row.handled_status
  handleForm.note = row.note || ''
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (!current.value) return
  submitting.value = true
  try {
    await handleRiskEvent(current.value.id, {
      handled_status: handleForm.handled_status,
      note: handleForm.note
    })
    ElMessage.success('已保存处置结果')
    dialogVisible.value = false
    await Promise.all([loadList(), loadStats()])
  } catch (e) {
    console.error('处置失败', e)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadList()
  loadStats()
})
</script>

<style scoped>
.risk-manage {
  padding: 0;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 20px;
  color: #3d2b1f;
}

.page-header .sub {
  margin: 0 0 16px;
  font-size: 13px;
  color: #9e8070;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #f0e0d0;
}

.stat-label {
  font-size: 12px;
  color: #9e8070;
}

.stat-value {
  font-size: 22px;
  font-weight: 500;
  color: #3d2b1f;
}

.stat-card.warn .stat-value {
  color: #ba7517;
}

.stat-card.danger .stat-value {
  color: #d9534f;
}

.search-card,
.table-card {
  margin-bottom: 16px;
}

.keywords {
  color: #a13d3d;
}

.actions {
  color: #9e8070;
  font-size: 12px;
}

.handle-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.handle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #6b5244;
}

.handle-row.column {
  align-items: flex-start;
  flex-direction: column;
  gap: 6px;
}

.handle-label {
  color: #9e8070;
  min-width: 64px;
}
</style>
