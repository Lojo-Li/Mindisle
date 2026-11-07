<template>
  <div class="knowledge-manage">
    <div class="page-header">
      <h2>知识管理</h2>
      <el-button type="primary" :icon="Plus" @click="createArticle">新建文章</el-button>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题或内容"
          style="width: 250px"
          clearable
        />
        <el-select v-model="filters.category" placeholder="全部分类" style="width: 150px" clearable>
          <el-option label="焦虑抑郁" value="anxiety" />
          <el-option label="人际关系" value="relationship" />
          <el-option label="职业发展" value="career" />
          <el-option label="家庭婚姻" value="family" />
          <el-option label="个人成长" value="growth" />
        </el-select>
        <el-button type="primary" @click="loadArticles">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <!-- 文章列表 -->
      <el-table v-loading="loading" :data="articles" stripe>
        <el-table-column prop="cover" label="封面" width="120">
          <template #default="{ row }">
            <el-image
              :src="row.cover"
              fit="cover"
              style="width: 80px; height: 60px; border-radius: 4px"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryText(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="views" label="浏览量" width="100" />
        <el-table-column prop="likes" label="点赞数" width="100" />
        <el-table-column prop="favorites" label="收藏数" width="100" />
        <el-table-column prop="createdAt" label="发布时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="editArticle(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteArticle(row)">删除</el-button>
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
          @size-change="loadArticles"
          @current-change="loadArticles"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getKnowledgeArticles, deleteKnowledgeArticle } from '@/api/admin'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  keyword: '',
  category: ''
})

const loadArticles = async () => {
  try {
    loading.value = true
    const res = await getKnowledgeArticles({
      keyword: filters.keyword,
      category: filters.category,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    articles.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  currentPage.value = 1
  loadArticles()
}

const getCategoryText = (category) => {
  const map = {
    anxiety: '焦虑抑郁',
    relationship: '人际关系',
    career: '职业发展',
    family: '家庭婚姻',
    growth: '个人成长'
  }
  return map[category] || category
}

const createArticle = () => {
  router.push('/admin/article-editor')
}

const editArticle = (row) => {
  router.push(`/admin/article-editor/${row.id}`)
}

const deleteArticle = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除文章《${row.title}》吗？`, '提示', { type: 'warning' })
    await deleteKnowledgeArticle(row.id)
    ElMessage.success('删除成功')
    loadArticles()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => loadArticles())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.knowledge-manage { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }

.filter-bar { display: flex; gap: $spacing-md; margin-bottom: $spacing-lg; }
.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }
</style>
