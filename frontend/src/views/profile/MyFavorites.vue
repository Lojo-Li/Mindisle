<template>
  <div class="favorites-page">
    <div class="container">

      <div class="page-title">
        <h2>我的收藏</h2>
        <p>你收藏的心理知识文章</p>
      </div>

      <div v-loading="loading" class="article-grid" :class="{ empty: !loading && articles.length === 0 }">
        <el-empty v-if="!loading && articles.length === 0" description="暂无收藏内容" :image-size="120" />

        <div
          v-for="item in articles"
          :key="item.id"
          class="article-card"
          @click="goToDetail(item.article_id || item.id)"
        >
          <!-- 封面 -->
          <div class="cover-wrap">
            <img :src="item.cover_image || item.cover || defaultCover" :alt="item.title" />
            <div class="category-badge">{{ item.category || '心理知识' }}</div>
          </div>

          <!-- 内容 -->
          <div class="card-body">
            <h3>{{ item.title }}</h3>
            <p class="summary">{{ item.summary || item.content_text || '暂无摘要' }}</p>
            <div class="meta">
              <span class="meta-item">📅 {{ formatDate(item.favorited_at || item.created_at) }}</span>
              <span class="meta-item">👁 {{ item.view_count || 0 }}</span>
              <el-button
                class="unfav-btn"
                size="small"
                text
                @click.stop="unfavorite(item.article_id || item.id)"
              >
                <el-icon><StarFilled /></el-icon> 取消收藏
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="total > pageSize" class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadFavorites"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StarFilled } from '@element-plus/icons-vue'
import { getUserFavorites, unfavoriteKnowledge } from '@/api/knowledge'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12

const defaultCover = 'https://picsum.photos/seed/psych/400/240'

const loadFavorites = async () => {
  try {
    loading.value = true
    const res = await getUserFavorites({ page: page.value, page_size: pageSize })
    const data = res.data
    articles.value = data.items || data.list || []
    total.value = data.total || articles.value.length
  } catch (e) {
    console.error('加载收藏失败:', e)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const unfavorite = async (id) => {
  try {
    await ElMessageBox.confirm('确定取消收藏该文章？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await unfavoriteKnowledge(id)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const goToDetail = (id) => {
  router.push(`/knowledge/${id}`)
}

const formatDate = (str) => {
  if (!str) return ''
  const d = new Date(str)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => loadFavorites())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.favorites-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

// ── 页头 ──────────────────────────────────────────────
.page-title {
  margin-bottom: 32px;

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 4px;
  }

  p {
    font-size: 13px;
    color: $text-secondary;
    margin: 0;
  }
}

// ── 文章网格 ──────────────────────────────────────────
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  min-height: 200px;

  &.empty {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// ── 文章卡片 ──────────────────────────────────────────
.article-card {
  background: #fff;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(107,82,68,0.13);

    .cover-wrap img { transform: scale(1.06); }
  }
}

.cover-wrap {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.35s;
  }

  .category-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 4px 12px;
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(6px);
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: $primary-dark;
  }
}

.card-body {
  padding: 16px 18px 18px;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 8px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
  }

  .summary {
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    margin-bottom: 12px;
    min-height: 40px;
  }

  .meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    .meta-item {
      font-size: 12px;
      color: $text-placeholder;
    }

    .unfav-btn {
      margin-left: auto;
      font-size: 12px;
      color: $text-secondary;
      padding: 0;

      &:hover { color: #f56c6c; }
    }
  }
}

// ── 分页 ──────────────────────────────────────────────
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

@media (max-width: $breakpoint-md) {
  .article-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
}

@media (max-width: $breakpoint-sm) {
  .article-grid { grid-template-columns: 1fr; }
}
</style>
