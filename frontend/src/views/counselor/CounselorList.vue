<template>
  <div class="counselor-list-page">

    <div class="container">

      <!-- 筛选卡片 -->
      <el-card class="filter-card">
        <div class="search-wrap">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索咨询师姓名、擅长领域..."
            prefix-icon="Search"
            clearable
            size="large"
            @keyup.enter="handleFilterChange"
          />
        </div>

        <div class="filter-rows">
          <div class="filter-row">
            <span class="label">擅长领域</span>
            <div class="pills">
              <button
                v-for="s in specialtyOptions"
                :key="s.value"
                class="pill"
                :class="{ active: filters.specialties.includes(s.value) }"
                @click="toggleSpecialty(s.value)"
              >{{ s.label }}</button>
            </div>
          </div>

          <div class="filter-row">
            <span class="label">咨询方式</span>
            <div class="pills">
              <button
                v-for="t in typeOptions"
                :key="t.value"
                class="pill"
                :class="{ active: filters.types.includes(t.value) }"
                @click="toggleType(t.value)"
              >{{ t.label }}</button>
            </div>
          </div>

          <div class="filter-row">
            <span class="label">价格范围</span>
            <div class="pills">
              <button
                v-for="p in priceOptions"
                :key="p.value"
                class="pill"
                :class="{ active: filters.priceRange === p.value }"
                @click="filters.priceRange = p.value; handleFilterChange()"
              >{{ p.label }}</button>
            </div>
            <el-select v-model="filters.sort" @change="handleFilterChange" style="width:120px; margin-left:auto" size="small">
              <el-option label="综合排序" value="default" />
              <el-option label="评分最高" value="rating" />
              <el-option label="销量最高" value="orders" />
              <el-option label="价格最低" value="price-asc" />
            </el-select>
          </div>
        </div>
      </el-card>

      <!-- 咨询师列表 -->
      <div v-loading="loading" class="counselor-grid">
        <el-skeleton v-if="loading && counselors.length === 0" :rows="3" animated />
        <el-empty v-else-if="!loading && counselors.length === 0" description="暂无咨询师" />

        <div
          v-for="counselor in counselors"
          :key="counselor.id"
          class="counselor-card"
        >
          <!-- 左侧头像区 -->
          <div class="card-left">
            <el-avatar :size="80" :src="counselor.avatar" class="avatar">
              <el-icon :size="36"><User /></el-icon>
            </el-avatar>
            <div class="price-tag">
              <span class="num">¥{{ counselor.price }}</span>
              <span class="unit">/时</span>
            </div>
          </div>

          <!-- 右侧信息区 -->
          <div class="card-body">
            <div class="card-top">
              <h3>{{ counselor.name }}</h3>
              <div class="rating-row">
                <el-rate v-model="counselor.rating" disabled show-score text-color="#e8845a" score-template="{value}" />
                <span class="review-count">{{ counselor.reviewCount }}条评价</span>
              </div>
            </div>

            <div class="tags-row">
              <el-tag
                v-for="s in counselor.specialties"
                :key="s"
                size="small"
                class="specialty-tag"
              >{{ specialtyLabel(s) }}</el-tag>
            </div>

            <div class="info-row">
              <span class="info-item">
                <el-icon><VideoCamera /></el-icon>
                {{ counselor.types?.map(t => typeLabel(t)).join(' · ') || '—' }}
              </span>
            </div>

            <div class="card-actions">
              <el-button round @click="viewDetail(counselor.id)">查看详情</el-button>
              <el-button type="primary" round @click="goToAppointment(counselor.id)">立即预约</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[12, 24, 36]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, User, VideoCamera } from '@element-plus/icons-vue'
import { getCounselorList } from '@/api/counselor'
import { getToken } from '@/utils/storage'

const specialtyOptions = [
  { label: '全部', value: '' },
  { label: '焦虑症', value: '焦虑症' },
  { label: '抑郁症', value: '抑郁症' },
  { label: '情感障碍', value: '情感障碍' },
  { label: '人际关系', value: '人际关系' },
  { label: '家庭治疗', value: '家庭治疗' },
  { label: '青少年问题', value: '青少年问题' },
  { label: '职业发展', value: '职业发展' },
  { label: '自我成长', value: '自我成长' },
]
const typeOptions = [
  { label: '视频', value: 'video' },
  { label: '语音', value: 'voice' },
  { label: '线下', value: 'offline' },
]
const priceOptions = [
  { label: '不限', value: '' },
  { label: '¥0-200', value: '0-200' },
  { label: '¥200-500', value: '200-500' },
  { label: '¥500+', value: '500+' },
]
const typeLabelMap = { video: '视频', voice: '语音', offline: '线下' }
const typeLabel = (t) => typeLabelMap[t] || t

const specialtyLabelMap = {
  '焦虑症': '焦虑症',
  '抑郁症': '抑郁症',
  '情感障碍': '情感障碍',
  '人际关系': '人际关系',
  '家庭治疗': '家庭治疗',
  '青少年问题': '青少年问题',
  '职业发展': '职业发展',
  '自我成长': '自我成长',
  '婚姻家庭': '婚姻家庭',
  '情绪管理': '情绪管理',
  '压力管理': '压力管理',
  '个人成长': '个人成长'
}
const specialtyLabel = (s) => specialtyLabelMap[s] || s

const toggleSpecialty = (val) => {
  if (!val) { filters.specialties = []; handleFilterChange(); return }
  const idx = filters.specialties.indexOf(val)
  if (idx > -1) filters.specialties.splice(idx, 1)
  else filters.specialties.push(val)
  handleFilterChange()
}
const toggleType = (val) => {
  const idx = filters.types.indexOf(val)
  if (idx > -1) filters.types.splice(idx, 1)
  else filters.types.push(val)
  handleFilterChange()
}

const router = useRouter()
const loading = ref(false)
const counselors = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
  specialties: [],
  types: [],
  priceRange: '',
  sort: 'default'
})

const pagination = reactive({
  page: 1,
  pageSize: 12
})

const parsePriceRange = (range) => {
  if (!range) return {}
  if (range === '500+') return { price_min: 500 }

  const [min, max] = range.split('-').map(Number)
  const params = {}
  if (!Number.isNaN(min)) params.price_min = min
  if (!Number.isNaN(max)) params.price_max = max
  return params
}

const normalizeCounselor = (item) => {
  const specialties = typeof item.specialties === 'string'
    ? item.specialties.split(',').map(s => s.trim()).filter(Boolean)
    : (item.specialties || [])

  const types = typeof item.consultation_types === 'string'
    ? item.consultation_types.split(',').map(t => t.trim()).filter(Boolean)
    : (item.types || [])

  const prices = [item.price_video, item.price_voice, item.price_offline]
    .filter(v => v !== null && v !== undefined)

  return {
    ...item,
    specialties,
    types,
    rating: Number(item.rating || 0),
    reviewCount: item.review_count || item.reviewCount || 0,
    price: prices.length ? Math.min(...prices) : 0
  }
}

const loadCounselors = async () => {
  try {
    loading.value = true
    const params = {
      keyword: filters.keyword || undefined,
      specialties: filters.specialties.length > 0 ? filters.specialties.join(',') : undefined,
      consultation_types: filters.types.length > 0 ? filters.types.join(',') : undefined,
      sort: filters.sort,
      page: pagination.page,
      page_size: pagination.pageSize,
      ...parsePriceRange(filters.priceRange)
    }
    const res = await getCounselorList(params)
    const rows = res.data.items || res.data.list || []
    counselors.value = rows.map(normalizeCounselor)
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadCounselors()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadCounselors()
}

const handlePageChange = () => {
  loadCounselors()
}

const viewDetail = (id) => {
  router.push(`/counselor/${id}`)
}

const goToAppointment = (id) => {
  const token = getToken()
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push({ path: '/counselor/appointment', query: { counselorId: id } })
}

onMounted(() => {
  loadCounselors()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-list-page {
  min-height: 100vh;
  background: $bg-page;
}

// ── Banner ────────────────────────────────────────────
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px $spacing-lg;
}

// ── 筛选卡片 ──────────────────────────────────────────
.filter-card {
  margin-bottom: 28px;
  border-radius: 18px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;

  :deep(.el-card__body) { padding: 20px 24px; }
}

.search-wrap {
  margin-bottom: 16px;

  :deep(.el-input__wrapper) {
    border-radius: 12px !important;
  }
}

.filter-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;

  .label {
    font-weight: 600;
    font-size: 13px;
    color: $text-regular;
    min-width: 64px;
    white-space: nowrap;
  }

  .pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .pill {
    padding: 4px 14px;
    border-radius: 999px;
    border: 1px solid $border-base;
    background: transparent;
    color: $text-regular;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover { border-color: $primary-light; color: $primary-color; }
    &.active { background: $primary-color; border-color: $primary-color; color: white; }
  }
}

// ── 咨询师卡片网格 ────────────────────────────────────
.counselor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
  gap: 20px;
  margin-bottom: $spacing-xl;
}

.counselor-card {
  background: $bg-white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);
  display: flex;
  gap: 20px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 28px rgba(107,82,68,0.12);
  }

  .card-left {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;

    .avatar {
      border: 3px solid $primary-lighter;
    }

    .price-tag {
      background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%);
      color: white;
      border-radius: 10px;
      padding: 4px 12px;
      text-align: center;
      white-space: nowrap;

      .num { font-size: 17px; font-weight: 700; }
      .unit { font-size: 11px; opacity: 0.9; }
    }
  }

  .card-body {
    flex: 1;
    min-width: 0;

    .card-top {
      margin-bottom: 10px;

      h3 {
        font-size: 17px;
        font-weight: 700;
        color: $text-primary;
        margin-bottom: 4px;
      }

      .rating-row {
        display: flex;
        align-items: center;
        gap: 8px;

        .review-count {
          font-size: 12px;
          color: $text-secondary;
        }
      }
    }

    .tags-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;

      .specialty-tag {
        border-radius: 999px !important;
      }
    }

    .info-row {
      margin-bottom: 14px;

      .info-item {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: $text-secondary;
      }
    }

    .card-actions {
      display: flex;
      gap: 10px;

      .el-button {
        flex: 1;
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: $spacing-lg;
}

@media (max-width: $breakpoint-md) {
  .counselor-grid { grid-template-columns: 1fr; }
  .filter-row { flex-wrap: wrap; }
}
</style>

