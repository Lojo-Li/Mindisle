<template>
  <div class="slot-manage-page">
    <div class="container">
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>时段管理</h2>
        <el-button type="primary" :icon="Plus" @click="openDialog">发布时段</el-button>
      </div>

      <el-card v-loading="loading">
        <template #header>
          <div class="filter-bar">
            <span>我的可预约时段</span>
            <el-date-picker
              v-model="filterDate"
              type="date"
              placeholder="按日期筛选"
              value-format="YYYY-MM-DD"
              :clearable="true"
              style="width: 180px"
              @change="loadSlots"
            />
          </div>
        </template>

        <el-empty v-if="slots.length === 0" description="还没有发布可预约时段，点击右上角「发布时段」开始排班" />

        <el-table v-else :data="slots" style="width: 100%">
          <el-table-column prop="slot_date" label="日期" width="140" />
          <el-table-column label="时段" width="160">
            <template #default="{ row }">
              {{ row.start_time }} - {{ row.end_time }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="140">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'available'"
                type="danger"
                link
                @click="confirmRemove(row)"
              >
                删除
              </el-button>
              <el-tooltip v-else content="已被预约占用的时段不可删除，需先取消对应预约" placement="top">
                <el-button type="info" link disabled>删除</el-button>
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 发布时段弹窗 -->
      <el-dialog v-model="dialogVisible" title="发布可预约时段" width="560px">
        <div class="publish-tip">
          时段需对齐整点且至少 1 小时。来访者只能预约你发布过的时段；与已有预约冲突的时段会被自动跳过。
        </div>

        <div v-for="(item, index) in pendingSlots" :key="index" class="publish-row">
          <el-date-picker
            v-model="item.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 170px"
          />
          <el-select v-model="item.start_time" placeholder="开始" style="width: 110px">
            <el-option v-for="t in timeOptions" :key="t" :label="t" :value="t" />
          </el-select>
          <span class="dash">—</span>
          <el-select v-model="item.end_time" placeholder="结束" style="width: 110px">
            <el-option v-for="t in timeOptions" :key="t" :label="t" :value="t" />
          </el-select>
          <el-button
            type="danger"
            :icon="Delete"
            circle
            plain
            :disabled="pendingSlots.length === 1"
            @click="pendingSlots.splice(index, 1)"
          />
        </div>

        <el-button type="primary" link :icon="Plus" @click="addRow">再添加一行</el-button>

        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="publishing" @click="submitPublish">确认发布</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { getMyScheduleSlots, publishScheduleSlots, removeScheduleSlot } from '@/api/counselor'

const router = useRouter()
const loading = ref(true)
const slots = ref([])
const filterDate = ref(null)

const dialogVisible = ref(false)
const publishing = ref(false)
const pendingSlots = ref([])

// 可选时间：08:00 - 22:00 整点
const timeOptions = Array.from({ length: 15 }, (_, i) => `${String(i + 8).padStart(2, '0')}:00`)

const statusText = (status) => ({
  available: '可预约',
  booked: '已被预约',
  disabled: '已停用'
}[status] || status)

const statusTagType = (status) => ({
  available: 'success',
  booked: 'warning',
  disabled: 'info'
}[status] || 'info')

const loadSlots = async () => {
  loading.value = true
  try {
    const res = await getMyScheduleSlots(filterDate.value || undefined)
    slots.value = res.data || []
  } catch (error) {
    console.error('加载时段失败:', error)
    slots.value = []
  } finally {
    loading.value = false
  }
}

const addRow = () => {
  pendingSlots.value.push({ date: filterDate.value || '', start_time: '', end_time: '' })
}

const openDialog = () => {
  pendingSlots.value = [{ date: filterDate.value || '', start_time: '', end_time: '' }]
  dialogVisible.value = true
}

const validateRows = () => {
  for (const item of pendingSlots.value) {
    if (!item.date) return '请为每一行选择日期'
    if (!item.start_time || !item.end_time) return '请为每一行选择开始和结束时间'
    if (item.end_time <= item.start_time) return '结束时间必须晚于开始时间'
  }
  return null
}

const submitPublish = async () => {
  const error = validateRows()
  if (error) {
    ElMessage.warning(error)
    return
  }

  publishing.value = true
  try {
    const res = await publishScheduleSlots(pendingSlots.value.map(item => ({
      date: item.date,
      start_time: item.start_time,
      end_time: item.end_time
    })))
    const { created, skipped, conflicts } = res.data || { created: 0, skipped: 0, conflicts: [] }

    if (created > 0) ElMessage.success(`成功发布 ${created} 个时段`)
    if (conflicts && conflicts.length > 0) {
      ElMessageBox.alert(
        conflicts.map(c => `· ${c}`).join('<br/>'),
        `${skipped} 条时段被跳过（冲突）`,
        { dangerouslyUseHTMLString: true, type: 'warning' }
      )
    }
    dialogVisible.value = false
    await loadSlots()
  } catch (err) {
    if (err?.response?.data?.detail) ElMessage.error(err.response.data.detail)
  } finally {
    publishing.value = false
  }
}

const confirmRemove = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除 ${row.slot_date} ${row.start_time}-${row.end_time} 这个时段吗？`,
      '删除时段',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await removeScheduleSlot(row.id)
    ElMessage.success('时段已删除')
    await loadSlots()
  } catch (err) {
    if (err?.response?.data?.detail) ElMessage.error(err.response.data.detail)
  }
}

const goBack = () => {
  router.push('/counselor/dashboard')
}

onMounted(loadSlots)
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.slot-manage-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.page-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;

  h2 {
    flex: 1;
    margin: 0;
  }
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.publish-tip {
  margin-bottom: $spacing-md;
  padding: $spacing-sm $spacing-md;
  background: rgba($primary-color, 0.06);
  border-radius: $border-radius-md;
  color: $text-secondary;
  font-size: $font-size-small;
  line-height: 1.6;
}

.publish-row {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;

  .dash {
    color: $text-secondary;
  }
}
</style>
