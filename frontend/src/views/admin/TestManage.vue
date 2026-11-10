<template>
  <div class="test-manage">
    <header class="page-head">
      <div>
        <div class="mi-eyebrow">ASSESSMENT CONFIG</div>
        <h1 class="page-title">量表管理</h1>
        <p class="page-sub">配置量表信息、题目、维度与等级区间。保存后对之后的测评立即生效。</p>
      </div>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        新建量表
      </el-button>
    </header>

    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索名称 / 编码" clearable class="search-input" @clear="reload" @keyup.enter="reload" />
      <span class="count-hint">共 {{ total }} 个量表</span>
    </div>

    <el-table :data="list" v-loading="loading" class="test-table">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="量表" min-width="220">
        <template #default="{ row }">
          <div class="cell-title">{{ row.title }}</div>
          <div class="cell-code">{{ row.test_code }}</div>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="100">
        <template #default="{ row }">{{ catText(row.category) }}</template>
      </el-table-column>
      <el-table-column prop="questionCount" label="题数" width="76" align="center" />
      <el-table-column prop="completedCount" label="完成" width="76" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <span class="mi-pill" :class="row.isActive ? 'is-ok' : ''">{{ row.isActive ? '已上架' : '已下架' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openEdit(row)">配置</el-button>
          <el-button text size="small" :type="row.isActive ? 'warning' : 'success'" @click="toggleStatus(row)">
            {{ row.isActive ? '下架' : '上架' }}
          </el-button>
          <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="reload"
        @current-change="load"
      />
    </div>

    <el-drawer v-model="drawer" :title="form.id ? `配置：${form.title || '未命名'}` : '新建量表'" size="820px" :close-on-click-modal="false">
      <div class="drawer-body">
        <section class="block">
          <h3 class="block-title">基本信息</h3>
          <div class="grid-2">
            <label class="field"><span>名称 *</span><el-input v-model="form.title" /></label>
            <label class="field"><span>编码 *</span><el-input v-model="form.test_code" :disabled="!!form.id" placeholder="如 SAS20" /></label>
            <label class="field">
              <span>分类</span>
              <el-select v-model="form.category">
                <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </label>
            <label class="field">
              <span>选项类型</span>
              <el-select v-model="form.option_type">
                <el-option label="4 选项（1–4 分）" value="4选项" />
                <el-option label="5 选项（1–5 分）" value="5选项" />
              </el-select>
            </label>
            <label class="field"><span>计分方式</span>
              <el-select v-model="form.score_type">
                <el-option label="总分" value="total" />
                <el-option label="维度分" value="dimension" />
              </el-select>
            </label>
            <label class="field"><span>上架状态</span>
              <el-switch v-model="form.is_active" active-text="上架" inactive-text="下架" />
            </label>
          </div>
          <label class="field"><span>简介</span><el-input v-model="form.description" type="textarea" :rows="2" /></label>
          <label class="field"><span>答题说明</span><el-input v-model="form.intro_text" type="textarea" :rows="2" /></label>
        </section>

        <section class="block">
          <div class="block-head">
            <h3 class="block-title">计分规则</h3>
            <span class="hint">维度决定分项呈现；反向题按「满分+1−原始分」折算</span>
          </div>
          <div v-for="(d, i) in form.dimensions" :key="'d' + i" class="row-2">
            <el-input v-model="d.name" placeholder="维度名，如 躯体性焦虑" />
            <el-input v-model="d.questions" placeholder="题号，如 2,4,6,8" />
            <el-button text type="danger" size="small" @click="form.dimensions.splice(i, 1)">删除</el-button>
          </div>
          <el-button text type="primary" size="small" @click="form.dimensions.push({ name: '', questions: '' })">+ 添加维度</el-button>
          <label class="field" style="margin-top:12px"><span>反向题号</span>
            <el-input v-model="form.reverse" placeholder="逗号分隔，如 5,9,13,17,19" />
          </label>
        </section>

        <section class="block">
          <div class="block-head">
            <h3 class="block-title">结果等级</h3>
            <span class="hint">按总分区间判定，区间应连续</span>
          </div>
          <div v-for="(l, i) in form.levels" :key="'l' + i" class="row-level">
            <el-input v-model="l.code" placeholder="code" />
            <el-input v-model="l.title" placeholder="名称" />
            <el-input v-model.number="l.min" type="number" placeholder="下限" />
            <el-input v-model.number="l.max" type="number" placeholder="上限" />
            <el-input v-model="l.desc" placeholder="说明" />
            <el-button text type="danger" size="small" @click="form.levels.splice(i, 1)">×</el-button>
          </div>
          <el-button text type="primary" size="small" @click="addLevel">+ 添加等级</el-button>
        </section>

        <section class="block">
          <div class="block-head">
            <h3 class="block-title">题目（{{ form.questions.length }}）</h3>
            <el-button text type="primary" size="small" @click="addQuestion">+ 添加题目</el-button>
          </div>
          <p class="hint" style="margin-bottom:8px">选项用逗号分隔，按顺序对应 1 分、2 分…</p>
          <div v-for="(q, i) in form.questions" :key="'q' + i" class="q-item">
            <div class="q-head">
              <span class="q-no">{{ String(i + 1).padStart(2, '0') }}</span>
              <el-input v-model="q.question_text" placeholder="题干" />
              <el-button text type="danger" size="small" @click="form.questions.splice(i, 1)">删除</el-button>
            </div>
            <div class="q-meta">
              <el-input v-model="q.dimension" placeholder="维度（可空）" style="width:180px" />
              <label class="q-reverse"><el-switch v-model="q.is_reverse" size="small" /><span>反向题</span></label>
            </div>
            <el-input v-model="q.optionsText" placeholder="如：完全没有,偶尔出现,经常出现,总是出现" />
          </div>
        </section>
      </div>

      <template #footer>
        <div class="drawer-footer">
          <span class="hint">{{ form.id ? '保存后立即生效' : '创建后可在列表继续编辑' }}</span>
          <div>
            <el-button @click="drawer = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="save">保存</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAdminTestList, getAdminTestDetail, createTest, updateTest, deleteTest, toggleTestStatus
} from '@/api/admin'

const loading = ref(false)
const saving = ref(false)
const drawer = ref(false)
const list = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const categories = [
  { label: '焦虑', value: 'anxiety' }, { label: '抑郁', value: 'depression' },
  { label: '人格', value: 'personality' }, { label: '压力', value: 'stress' },
  { label: '情绪', value: 'emotion' }, { label: '睡眠', value: 'sleep' },
  { label: '职业', value: 'career' }, { label: '其他', value: 'other' }
]
const catText = v => (categories.find(c => c.value === v) || {}).label || v || '未分类'

const blank = () => ({
  id: null, test_code: '', title: '', description: '', category: 'anxiety',
  intro_text: '', option_type: '4选项', score_type: 'total', is_active: true,
  dimensions: [{ name: '', questions: '' }], reverse: '', levels: [], questions: []
})
const form = reactive(blank())

const parseNums = s => String(s || '').split(/[,，\s]+/).map(Number).filter(n => Number.isInteger(n) && n > 0)
const splitOptions = s => String(s || '').split(/[,，]/).map(x => x.trim()).filter(Boolean)

const load = async () => {
  loading.value = true
  try {
    const res = await getAdminTestList({ keyword: keyword.value, page: page.value, page_size: pageSize.value })
    const d = (res && res.data) || {}
    list.value = d.list || []
    total.value = d.total || 0
  } catch (e) {
    ElMessage.error('量表列表加载失败')
  } finally {
    loading.value = false
  }
}
const reload = () => { page.value = 1; load() }

const openCreate = () => {
  Object.assign(form, blank())
  form.levels = [
    { code: 'none', title: '', min: 0, max: 0, desc: '' },
    { code: 'mild', title: '', min: 0, max: 0, desc: '' }
  ]
  drawer.value = true
}

const openEdit = async (row) => {
  loading.value = true
  try {
    const res = await getAdminTestDetail(row.id)
    const d = (res && res.data) || {}
    Object.assign(form, blank(), {
      id: d.id,
      test_code: d.testCode || '',
      title: d.title || '',
      description: d.description || '',
      category: d.category || 'other',
      intro_text: d.introText || '',
      option_type: d.optionType || '4选项',
      score_type: d.scoreType || 'total',
      is_active: d.isActive !== false
    })

    const rules = d.scoringRules || {}
    const dims = rules.dimensions || {}
    form.dimensions = Object.keys(dims).length
      ? Object.entries(dims).map(([name, cfg]) => ({ name, questions: (cfg.questions || []).join(',') }))
      : [{ name: '', questions: '' }]
    form.reverse = (rules.reverse_questions || []).join(',')

    const levels = (d.resultRules || {}).levels || {}
    form.levels = Object.entries(levels)
      .map(([code, cfg]) => ({ code, title: cfg.title || '', min: cfg.min ?? 0, max: cfg.max ?? 0, desc: cfg.desc || '' }))
      .sort((a, b) => Number(a.min) - Number(b.min))

    form.questions = (d.questions || []).map(q => ({
      question_text: q.questionText || '',
      dimension: q.dimension || '',
      is_reverse: !!q.isReverse,
      optionsText: (q.options || []).map(o => o.label).join(',')
    }))
    drawer.value = true
  } catch (e) {
    ElMessage.error('详情加载失败')
  } finally {
    loading.value = false
  }
}

const addLevel = () => {
  const last = form.levels[form.levels.length - 1]
  form.levels.push({ code: '', title: '', min: last ? Number(last.max) + 1 : 0, max: last ? Number(last.max) + 15 : 15, desc: '' })
}

const addQuestion = () => {
  const labels = form.option_type === '5选项'
    ? ['完全没有', '很轻', '中等', '偏重', '严重']
    : ['完全没有', '偶尔出现', '经常出现', '总是出现']
  form.questions.push({ question_text: '', dimension: '', is_reverse: false, optionsText: labels.join(',') })
}

const buildPayload = () => {
  const dims = {}
  form.dimensions.forEach(d => { if ((d.name || '').trim()) dims[d.name.trim()] = { questions: parseNums(d.questions) } })

  const levels = {}
  form.levels.forEach(l => {
    if (!(l.code || '').trim()) return
    levels[l.code.trim()] = { min: Number(l.min) || 0, max: Number(l.max) || 0, title: l.title || l.code, desc: l.desc || '' }
  })

  return {
    test_code: form.test_code.trim(),
    title: form.title.trim(),
    description: form.description,
    category: form.category,
    intro_text: form.intro_text,
    option_type: form.option_type,
    score_type: form.score_type,
    is_active: form.is_active,
    scoring_rules: { type: 'sum_with_dimensions', dimensions: dims, reverse_questions: parseNums(form.reverse) },
    result_rules: { levels },
    questions: form.questions.map(q => ({
      question_text: (q.question_text || '').trim(),
      dimension: q.dimension || null,
      is_reverse: !!q.is_reverse,
      options: splitOptions(q.optionsText).map((label, i) => ({ value: i + 1, label }))
    }))
  }
}

const save = async () => {
  if (!form.title.trim()) return ElMessage.warning('请填写量表名称')
  if (!form.id && !form.test_code.trim()) return ElMessage.warning('请填写量表编码')
  const bad = form.questions.findIndex(q => !(q.question_text || '').trim())
  if (bad !== -1) return ElMessage.warning('第 ' + (bad + 1) + ' 题题干为空')

  saving.value = true
  try {
    const payload = buildPayload()
    if (form.id) { await updateTest(form.id, payload); ElMessage.success('已保存') }
    else { await createTest(payload); ElMessage.success('已创建') }
    drawer.value = false
    await load()
  } catch (e) {
    ElMessage.error((e && e.response && e.response.data && e.response.data.detail) || '保存失败')
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (row) => {
  try {
    await toggleTestStatus(row.id, !row.isActive)
    row.isActive = !row.isActive
    ElMessage.success(row.isActive ? '已上架' : '已下架')
  } catch (e) {
    ElMessage.error('状态切换失败')
  }
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm('删除「' + row.title + '」后用户端不再展示，确定吗？', '删除量表', { type: 'warning' })
    await deleteTest(row.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) { /* 取消 */ }
}

onMounted(load)
</script>

<style scoped>
.test-manage { display: flex; flex-direction: column; gap: 14px; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; }
.page-title { margin: 8px 0 6px; font-size: 24px; font-weight: 620; color: var(--ink); }
.page-sub { font-size: 12.5px; color: var(--ink-3); }
.mi-eyebrow { font-size: 10.5px; letter-spacing: 1.6px; text-transform: uppercase; color: var(--ink-3); }

.toolbar { display: flex; align-items: center; gap: 12px; }
.search-input { width: 240px; }
.count-hint { margin-left: auto; font-size: 11.5px; color: var(--ink-3); }

.test-table { border: 1px solid var(--line); border-radius: var(--r-lg); background: var(--surface); overflow: hidden; }
.cell-title { font-size: 13px; font-weight: 560; color: var(--ink); }
.cell-code { font-size: 10.5px; letter-spacing: .6px; color: var(--ink-3); }
.pager { display: flex; justify-content: flex-end; }

.drawer-body { padding-bottom: 12px; }
.block { padding: 16px 0 18px; border-bottom: 1px solid var(--line-2); }
.block:last-child { border-bottom: none; }
.block-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.block-title { font-size: 13.5px; font-weight: 620; color: var(--ink); margin-bottom: 10px; }
.block-head .block-title { margin-bottom: 0; }
.hint { font-size: 10.5px; color: var(--ink-3); }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.field { display: block; margin-bottom: 12px; }
.field > span { display: block; font-size: 11.5px; color: var(--ink-2); margin-bottom: 6px; }

.row-2 { display: grid; grid-template-columns: 1fr 1.2fr 56px; gap: 8px; align-items: center; margin-bottom: 6px; }
.row-level { display: grid; grid-template-columns: 90px 1fr 80px 80px 1.4fr 36px; gap: 6px; align-items: center; margin-bottom: 6px; }

.q-item { padding: 10px 12px; border: 1px solid var(--line-2); border-radius: var(--r-md); background: var(--surface-2); margin-bottom: 8px; }
.q-head { display: flex; align-items: center; gap: 10px; }
.q-no { flex: 0 0 20px; font-size: 10.5px; color: var(--ink-3); }
.q-meta { display: flex; align-items: center; gap: 14px; margin: 8px 0 8px 30px; }
.q-reverse { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; color: var(--ink-3); }

.drawer-footer { display: flex; align-items: center; justify-content: space-between; }
</style>
