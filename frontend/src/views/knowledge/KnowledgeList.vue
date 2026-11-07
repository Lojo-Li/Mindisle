<template>
  <div class="knowledge-list-page">

    <div class="container">
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="category-pills">
          <button
            v-for="cat in categoryOptions"
            :key="cat.value"
            class="pill"
            :class="{ active: category === cat.value }"
            @click="category = cat.value; loadArticles()"
          >{{ cat.label }}</button>
        </div>
        <div class="search-wrap">
          <el-input
            v-model="keyword"
            placeholder="搜索文章标题、内容、标签..."
            prefix-icon="Search"
            clearable
            size="small"
            style="width: 280px"
            @keyup.enter="handleSearch"
            @clear="handleClear"
            @input="handleSearchInput"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </div>
      </div>

      <!-- 热门搜索 -->
      <div v-if="!keyword" class="hot-keywords">
        <span class="hot-label">🔥 热门搜索：</span>
        <el-button
          v-for="kw in hotKeywords"
          :key="kw"
          size="small"
          round
          @click="keyword = kw; handleSearch()"
        >{{ kw }}</el-button>
      </div>

      <!-- 搜索结果提示 -->
      <div v-if="keyword" class="search-result-info">
        <span class="search-keyword">"{{ keyword }}"</span>
        <span class="search-count">找到 {{ totalCount }} 篇相关文章</span>
        <el-button link type="primary" @click="handleClear">清除搜索</el-button>
      </div>

      <!-- 文章网格 -->
      <div v-loading="loading" class="article-grid">
        <el-skeleton v-if="loading && articles.length === 0" :rows="4" animated style="grid-column: 1/-1" />
        <el-empty v-else-if="!loading && articles.length === 0" :description="keyword ? '没有找到相关文章，试试其他关键词吧' : '暂无文章'" style="grid-column: 1/-1" />

        <div
          v-for="article in articles"
          :key="article.id"
          class="article-card"
          @click="goToDetail(article.id)"
        >
          <div class="cover-wrap">
            <img :src="article.coverImage || article.cover_image || defaultCover" :alt="article.title" loading="lazy" />
            <div class="category-badge">{{ article.category }}</div>
          </div>
          <div class="card-body">
            <h3>{{ article.title }}</h3>
            <p class="summary">{{ article.summary }}</p>
            <div class="meta">
              <span class="meta-item">👁 {{ article.views || 0 }}</span>
              <span class="meta-item">❤️ {{ article.favorites || 0 }}</span>
              <span class="read-more">阅读全文 →</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { getKnowledgeList } from '@/api/knowledge'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const keyword = ref('')
const category = ref('')
const totalCount = ref(0)

const defaultCover = 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&h=400&fit=crop'

const hotKeywords = [
  '焦虑', '抑郁', '压力', '失眠', '情绪', '人际关系', '自我提升', '心理健康'
]

const categoryOptions = [
  { label: '全部', value: '' },
  { label: '焦虑', value: '焦虑症' },
  { label: '抑郁', value: '抑郁症' },
  { label: '压力管理', value: '压力管理' },
  { label: '人际关系', value: '人际关系' },
  { label: '自我成长', value: '自我成长' },
]

const loadArticles = async () => {
  loading.value = true
  try {
    const res = await getKnowledgeList({ keyword: keyword.value, category: category.value })
    articles.value = res.data.list || res.data.items || []
    totalCount.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadArticles()
}

const handleClear = () => {
  keyword.value = ''
  loadArticles()
}

// 添加防抖功能，避免频繁搜索
let searchTimer = null
const handleSearchInput = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  if (keyword.value.trim()) {
    searchTimer = setTimeout(() => {
      handleSearch()
    }, 500) // 500ms 防抖延迟
  }
}

const goToDetail = (id) => router.push(`/knowledge/${id}`)

onMounted(() => loadArticles())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.knowledge-list-page {
  min-height: 100vh;
  background: $bg-page;
}

// ── Banner ────────────────────────────────────────────
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px $spacing-lg;
}

// ── 筛选栏 ────────────────────────────────────────────
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 28px;
  background: $bg-white;
  border: 1px solid $border-lighter;
  border-radius: 16px;
  padding: 14px 20px;
  box-shadow: 0 2px 10px rgba(107,82,68,0.05);

  .category-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .pill {
      padding: 5px 16px;
      border-radius: 999px;
      border: 1px solid $border-base;
      background: transparent;
      color: $text-regular;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;

      &:hover { border-color: $primary-light; color: $primary-color; }
      &.active { background: $primary-color; border-color: $primary-color; color: white; }
    }
  }

  .search-wrap {
    :deep(.el-input__wrapper) { border-radius: 999px !important; }
  }
}

// ── 热门搜索 ────────────────────────────────────────────
.hot-keywords {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: $bg-white;
  border-radius: 12px;
  border: 1px solid $border-lighter;
  flex-wrap: wrap;

  .hot-label {
    font-weight: 600;
    color: $text-primary;
    font-size: 14px;
  }

  .el-button {
    transition: all 0.2s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(232, 132, 90, 0.2);
    }
  }
}

// ── 搜索结果信息 ──────────────────────────────────────
.search-result-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.8), rgba(250, 248, 245, 0.8));
  border-left: 4px solid $primary-color;
  border-radius: 0 12px 12px 0;
  font-size: 14px;
  color: $text-secondary;

  .search-keyword {
    font-weight: 600;
    color: $primary-color;
    background: rgba(232, 132, 90, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
  }

  .search-count {
    color: $text-primary;
    font-weight: 500;
  }
}

// ── 文章网格 ──────────────────────────────────────────
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.article-card {
  background: $bg-white;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(107,82,68,0.14);

    .cover-wrap img { transform: scale(1.05); }
    .read-more { color: $primary-color; }
  }
}

.cover-wrap {
  position: relative;
  width: 100%;
  height: 190px;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.35s ease;
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
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
}

.card-body {
  padding: 18px 20px 20px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 8px;
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
    margin-bottom: 14px;
    min-height: 42px;
  }

  .meta {
    display: flex;
    align-items: center;
    gap: 14px;

    .meta-item {
      font-size: 13px;
      color: $text-secondary;
    }

    .read-more {
      margin-left: auto;
      font-size: 13px;
      font-weight: 600;
      color: $text-secondary;
      transition: color 0.2s;
    }
  }
}

@media (max-width: $breakpoint-md) {
  .article-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
  .filter-bar { flex-direction: column; align-items: stretch; }
}

@media (max-width: $breakpoint-sm) {
  .article-grid { grid-template-columns: 1fr; }
}
</style>

