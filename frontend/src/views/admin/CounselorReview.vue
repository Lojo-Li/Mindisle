<template>
  <div class="counselor-review">
    <div class="page-header">
      <h2>咨询师审核</h2>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索咨询师姓名"
        style="width: 300px"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane :label="`待审核 (${counts.pending || 0})`" name="pending" />
        <el-tab-pane :label="`已通过 (${counts.approved || 0})`" name="approved" />
        <el-tab-pane :label="`已拒绝 (${counts.rejected || 0})`" name="rejected" />
      </el-tabs>

      <el-table v-loading="loading" :data="counselors" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '保密' }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="职称" width="150" />
        <el-table-column prop="specialties" label="擅长领域" min-width="180">
          <template #default="{ row }">
            <el-tag
              v-for="tag in (row.specialties || '').split(',').filter(Boolean)"
              :key="tag"
              size="small"
              style="margin: 2px"
            >{{ getSpecialtyText(tag) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="experience_years" label="年限" width="70">
          <template #default="{ row }">{{ row.experience_years }}年</template>
        </el-table-column>
        <el-table-column prop="application_status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.application_status)" size="small">
              {{ statusLabel(row.application_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button link @click="viewDetail(row)">详情</el-button>
            <template v-if="row.application_status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadCounselors"
          @current-change="loadCounselors"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="咨询师申请详情" width="750px" destroy-on-close>
      <div v-if="currentCounselor" class="detail-content">
        <el-alert
          v-if="currentCounselor.application_status === 'rejected'"
          :title="`已拒绝：${currentCounselor.rejection_reason || '无原因'}`"
          type="error"
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-alert
          v-else-if="currentCounselor.application_status === 'approved'"
          title="该申请已通过审核"
          type="success"
          :closable="false"
          style="margin-bottom: 16px"
        />

        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="姓名">{{ currentCounselor.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ currentCounselor.gender === 'male' ? '男' : currentCounselor.gender === 'female' ? '女' : '保密' }}
          </el-descriptions-item>
          <el-descriptions-item label="职称">{{ currentCounselor.title || '—' }}</el-descriptions-item>
          <el-descriptions-item label="从业年限">{{ currentCounselor.experience_years }}年</el-descriptions-item>
          <el-descriptions-item label="学历背景" :span="2">{{ currentCounselor.education || '—' }}</el-descriptions-item>
          <el-descriptions-item label="擅长领域" :span="2">
            <el-tag
              v-for="tag in (currentCounselor.specialties || '').split(',').filter(Boolean)"
              :key="tag"
              size="small"
              style="margin: 2px"
            >{{ getSpecialtyText(tag) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="咨询方式" :span="2">
            <el-tag
              v-for="t in (currentCounselor.consultation_types || '').split(',').filter(Boolean)"
              :key="t"
              type="success"
              size="small"
              style="margin: 2px"
            >{{ consultTypeLabel(t) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-descriptions title="定价信息" :column="3" border style="margin-top: 16px">
          <el-descriptions-item label="视频咨询">
            {{ currentCounselor.price_video != null ? currentCounselor.price_video + ' 元/时' : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="语音咨询">
            {{ currentCounselor.price_voice != null ? currentCounselor.price_voice + ' 元/时' : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="线下咨询">
            {{ currentCounselor.price_offline != null ? currentCounselor.price_offline + ' 元/时' : '—' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" style="margin-top: 16px">
          <h4>个人简介</h4>
          <div class="bio-text">{{ currentCounselor.bio || '—' }}</div>
        </div>

        <div v-if="currentCounselor.approach" class="detail-section">
          <h4>咨询流派 / 方法</h4>
          <div class="bio-text">{{ currentCounselor.approach }}</div>
        </div>

        <div v-if="currentCounselor.achievements" class="detail-section">
          <h4>成就荣誉</h4>
          <div class="bio-text">{{ currentCounselor.achievements }}</div>
        </div>

        <div v-if="currentCounselor.qualifications" class="detail-section">
          <h4>资质证书</h4>
          <div class="cert-images">
            <el-image
              v-for="(img, idx) in (currentCounselor.qualifications || '').split(',').filter(Boolean)"
              :key="idx"
              :src="img"
              fit="cover"
              style="width: 120px; height: 120px; margin: 4px; border-radius: 4px; cursor: pointer"
              :preview-src-list="(currentCounselor.qualifications || '').split(',').filter(Boolean)"
              :initial-index="idx"
              preview-teleported
            />
          </div>
        </div>
      </div>
      <template v-if="currentCounselor?.application_status === 'pending'" #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="danger" @click="handleReject(currentCounselor); detailVisible = false">拒绝</el-button>
        <el-button type="success" @click="handleApprove(currentCounselor); detailVisible = false">通过</el-button>
      </template>
      <template v-else #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 拒绝对话框 -->
    <el-dialog v-model="rejectVisible" title="拒绝申请" width="480px">
      <el-form>
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因，将会通知申请人..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="reviewing" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getPendingCounselors, reviewCounselor } from '@/api/admin'

const loading = ref(false)
const reviewing = ref(false)
const activeTab = ref('pending')
const searchKeyword = ref('')
const counselors = ref([])
const counts = ref({ pending: 0, approved: 0, rejected: 0 })
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const rejectVisible = ref(false)
const currentCounselor = ref(null)
const rejectReason = ref('')

const loadCounselors = async () => {
  try {
    loading.value = true
    const res = await getPendingCounselors({
      status: activeTab.value,
      keyword: searchKeyword.value || undefined,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    counselors.value = res.data.list || []
    counts.value = res.data.counts || {}
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  currentPage.value = 1
  loadCounselors()
}

const handleSearch = () => {
  currentPage.value = 1
  loadCounselors()
}

const viewDetail = (row) => {
  currentCounselor.value = row
  detailVisible.value = true
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定通过 ${row.name} 的申请？通过后将开放咨询师权限。`, '确认通过', {
      type: 'success',
      confirmButtonText: '确定通过',
      cancelButtonText: '取消'
    })
    reviewing.value = true
    await reviewCounselor(row.id, { action: 'approve' })
    ElMessage.success('已通过审核')
    loadCounselors()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  } finally {
    reviewing.value = false
  }
}

const handleReject = (row) => {
  currentCounselor.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  try {
    reviewing.value = true
    await reviewCounselor(currentCounselor.value.id, {
      action: 'reject',
      reason: rejectReason.value.trim()
    })
    ElMessage.success('已拒绝申请')
    rejectVisible.value = false
    loadCounselors()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    reviewing.value = false
  }
}

const statusLabel = (s) => ({ pending: '待审核', approved: '已通过', rejected: '已拒绝' }[s] || s)
const statusTagType = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || '')
const consultTypeLabel = (t) => ({ video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }[t] || t)

// 擅长领域映射（英文 -> 中文）
const specialtyMap = {
  'anxiety': '焦虑症',
  'depression': '抑郁症',
  'relationship': '人际关系',
  'career': '职业发展',
  'family': '家庭关系',
  'marriage': '婚姻咨询',
  'adolescent': '青少年心理',
  'stress': '压力管理',
  'emotion': '情绪调节',
  'sleep': '睡眠障碍',
  'trauma': '创伤疗愈',
  'addiction': '成瘾行为',
  'eating_disorder': '饮食障碍',
  'obsessive_compulsive': '强迫症',
  'phobia': '恐惧症',
  'bipolar': '双相情感障碍',
  'schizophrenia': '精神分裂症',
  'personality_disorder': '人格障碍',
  'gender_identity': '性别认同',
  'sexual_issues': '性心理',
  'grief': '丧失与悲伤',
  'self_esteem': '自尊自信',
  'perfectionism': '完美主义',
  'procrastination': '拖延行为',
  'anger_management': '愤怒管理',
  'divorce': '离婚调适',
  'parenting': '亲子教育',
  'aging': '老年心理',
  'life_transition': '人生转变',
  'loneliness': '孤独感',
  'burnout': '职业倦怠',
  'other': '其他'
}

const getSpecialtyText = (specialty) => {
  return specialtyMap[specialty] || specialty || '未知'
}

const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => loadCounselors())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.counselor-review { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }
.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }

.detail-content { display: flex; flex-direction: column; gap: 12px; max-height: 65vh; overflow-y: auto; padding-right: 4px; }
.detail-section h4 { margin: 0 0 8px; font-size: 14px; color: #606266; font-weight: 600; }
.bio-text { line-height: 1.8; color: #303133; font-size: 14px; white-space: pre-wrap; }
.cert-images { display: flex; flex-wrap: wrap; gap: 6px; }
</style>
