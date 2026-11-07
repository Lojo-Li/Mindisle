<template>
  <div class="knowledge-detail">
    <div class="container">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>

      <el-card v-loading="loading">
        <h1>{{ article.title }}</h1>

        <div class="meta">
          <el-tag>{{ article.category }}</el-tag>
          <span>👁 {{ formatNumber(article.view_count || 0) }}</span>
          <span>{{ formatDate(article.published_at || article.created_at) }}</span>
        </div>

        <el-divider />

        <div class="content" v-html="article.content"></div>

        <el-divider />

        <!-- 互动按钮区 -->
        <div class="actions">
          <div class="action-buttons">
            <el-button
              :class="{ 'is-liked': article.is_liked }"
              :loading="likeLoading"
              @click="toggleLike"
              class="action-btn"
            >
              <el-icon><CaretTop /></el-icon>
              {{ article.is_liked ? '已赞' : '点赞' }}
              <span v-if="article.like_count > 0" class="count-badge">{{ formatNumber(article.like_count) }}</span>
            </el-button>

            <el-button
              :class="{ 'is-favorited': article.is_favorited }"
              :loading="favLoading"
              @click="toggleFavorite"
              class="action-btn"
            >
              <el-icon><Star /></el-icon>
              {{ article.is_favorited ? '已收藏' : '收藏' }}
              <span v-if="article.favorite_count > 0" class="count-badge">{{ formatNumber(article.favorite_count) }}</span>
            </el-button>
          </div>
        </div>

        <!-- 评论区 -->
        <section class="comments-section">
          <div class="comments-header">
            <h3>评论 ({{ article.comment_count || 0 }})</h3>
          </div>

          <!-- 评论输入框 -->
          <div class="comment-editor">
            <div class="editor-avatar">
              <el-avatar :src="userStore.userInfo?.avatar" :size="36">
                <el-icon><User /></el-icon>
              </el-avatar>
            </div>
            <div class="editor-body">
              <el-input
                v-model="commentContent"
                type="textarea"
                :rows="3"
                :autosize="{ minRows: 3, maxRows: 6 }"
                placeholder="写下你的想法..."
                maxlength="1000"
                show-word-limit
                :disabled="!userStore.isLoggedIn"
              />
              <div class="editor-footer">
                <span v-if="!userStore.isLoggedIn" class="login-hint" @click="router.push('/login')">
                  请先登录后再评论
                </span>
                <span v-else></span>
                <el-button
                  type="primary"
                  :loading="commentSubmitting"
                  :disabled="!commentContent.trim()"
                  @click="handleSubmitComment"
                >
                  发表评论
                </el-button>
              </div>
            </div>
          </div>

          <!-- 评论列表 -->
          <div v-loading="commentsLoading" class="comment-list">
            <EmptyState
              v-if="!commentsLoading && comments.length === 0"
              type="chat"
              title="暂无评论"
              description="来写下第一条评论吧"
            />

            <div v-for="comment in comments" :key="comment.id" class="comment-thread">
              <div class="comment-item">
                <el-avatar :src="comment.user_avatar" :size="32" class="comment-avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div class="comment-body">
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.user_name }}</span>
                    <span class="comment-time">{{ formatRelativeTime(comment.created_at) }}</span>
                  </div>
                  <p class="comment-content">{{ comment.content }}</p>
                  <div class="comment-actions">
                    <span
                      class="comment-like-btn"
                      :class="{ liked: comment.is_liked }"
                      @click="handleCommentLike(comment)"
                    >
                      <el-icon><CaretTop /></el-icon>
                      {{ comment.like_count || '' }}
                    </span>
                    <span class="reply-btn" @click="openReplyInput(comment)">
                      <el-icon><ChatDotSquare /></el-icon> 回复
                    </span>
                    <span
                      v-if="canDeleteComment(comment)"
                      class="delete-btn"
                      @click="handleDeleteComment(comment)"
                    >删除</span>
                  </div>

                  <!-- 回复输入框 (内联) -->
                  <div v-if="replyTarget?.id === comment.id" class="reply-editor">
                    <el-input
                      ref="replyInputRef"
                      v-model="replyContent"
                      type="textarea"
                      :rows="2"
                      :placeholder="`回复 ${comment.user_name}...`"
                      maxlength="500"
                      show-word-limit
                    />
                    <div class="reply-editor-footer">
                      <el-button size="small" @click="cancelReply">取消</el-button>
                      <el-button
                        size="small"
                        type="primary"
                        :loading="replySubmitting"
                        :disabled="!replyContent.trim()"
                        @click="handleSubmitReply(comment)"
                      >回复</el-button>
                    </div>
                  </div>

                  <!-- 子回复列表 -->
                  <div v-if="comment.children && comment.children.length > 0" class="child-replies">
                    <div v-for="reply in comment.children" :key="reply.id" class="comment-item reply-item">
                      <el-avatar :src="reply.user_avatar" :size="28" class="comment-avatar">
                        <el-icon><User /></el-icon>
                      </el-avatar>
                      <div class="comment-body">
                        <div class="comment-header">
                          <span class="comment-author">{{ reply.user_name }}</span>
                          <span class="comment-time">{{ formatRelativeTime(reply.created_at) }}</span>
                        </div>
                        <p class="comment-content">{{ reply.content }}</p>
                        <div class="comment-actions">
                          <span
                            class="comment-like-btn"
                            :class="{ liked: reply.is_liked }"
                            @click="handleCommentLike(reply)"
                          >
                            <el-icon><CaretTop /></el-icon>
                            {{ reply.like_count || '' }}
                          </span>
                          <span
                            v-if="canDeleteComment(reply)"
                            class="delete-btn"
                            @click="handleDeleteComment(reply)"
                          >删除</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 加载更多 -->
          <div v-if="commentTotal > comments.length" class="load-more">
            <el-button :loading="loadingMore" @click="loadMoreComments">加载更多评论</el-button>
          </div>
        </section>

        <el-divider />

        <div class="recommend" v-if="recommendations.length">
          <h3>相关推荐</h3>
          <div class="recommend-list">
            <div v-for="item in recommendations" :key="item.id" @click="goTo(item.id)">
              <img :src="item.cover_image || item.coverImage" />
              <h4>{{ item.title }}</h4>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Star, CaretTop, ChatDotSquare, User } from '@element-plus/icons-vue'
import {
  getKnowledgeDetail, getRecommendedKnowledge,
  favoriteKnowledge, unfavoriteKnowledge,
  likeKnowledge, unlikeKnowledge,
  getComments, submitComment, deleteComment,
  likeComment, unlikeComment
} from '@/api/knowledge'
import { formatDate, formatNumber, formatRelativeTime } from '@/utils/format'
import { useUserStore } from '@/stores/user'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ── 文章 ──
const loading = ref(true)
const article = ref({})
const recommendations = ref([])

const loadArticle = async () => {
  try {
    const res = await getKnowledgeDetail(route.params.id)
    article.value = res.data
  } catch {
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const loadRecommend = async () => {
  try {
    const res = await getRecommendedKnowledge(route.params.id)
    recommendations.value = res.data || []
  } catch { /* 推荐加载失败不影响主流程 */ }
}

// ── 点赞/收藏 ──
const likeLoading = ref(false)
const favLoading = ref(false)

const toggleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  likeLoading.value = true
  const prevLiked = article.value.is_liked
  const prevCount = article.value.like_count || 0
  article.value.is_liked = !prevLiked
  article.value.like_count = prevCount + (article.value.is_liked ? 1 : -1)
  try {
    if (article.value.is_liked) {
      await likeKnowledge(route.params.id)
    } else {
      await unlikeKnowledge(route.params.id)
    }
  } catch {
    article.value.is_liked = prevLiked
    article.value.like_count = prevCount
  } finally {
    likeLoading.value = false
  }
}

const toggleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  favLoading.value = true
  const prevFav = article.value.is_favorited
  const prevCount = article.value.favorite_count || 0
  article.value.is_favorited = !prevFav
  article.value.favorite_count = prevCount + (article.value.is_favorited ? 1 : -1)
  try {
    if (article.value.is_favorited) {
      await favoriteKnowledge(route.params.id)
    } else {
      await unfavoriteKnowledge(route.params.id)
    }
  } catch {
    article.value.is_favorited = prevFav
    article.value.favorite_count = prevCount
  } finally {
    favLoading.value = false
  }
}

// ── 评论 ──
const comments = ref([])
const commentsLoading = ref(false)
const commentContent = ref('')
const commentSubmitting = ref(false)
const commentPage = ref(1)
const commentPageSize = 10
const commentTotal = ref(0)
const loadingMore = ref(false)

// 回复
const replyTarget = ref(null)
const replyContent = ref('')
const replySubmitting = ref(false)
const replyInputRef = ref(null)

const loadComments = async (reset = false) => {
  if (reset) {
    commentPage.value = 1
  }
  commentsLoading.value = true
  try {
    const res = await getComments(route.params.id, {
      page: commentPage.value,
      page_size: commentPageSize
    })
    const items = res.data.items || []
    if (reset) {
      comments.value = items
    } else {
      comments.value = [...comments.value, ...items]
    }
    commentTotal.value = res.data.total || 0
  } catch {
    ElMessage.error('加载评论失败')
  } finally {
    commentsLoading.value = false
  }
}

const loadMoreComments = () => {
  commentPage.value++
  loadingMore.value = true
  loadComments(false).finally(() => { loadingMore.value = false })
}

const handleSubmitComment = async () => {
  if (!commentContent.value.trim()) return
  commentSubmitting.value = true
  try {
    const res = await submitComment(route.params.id, { content: commentContent.value.trim() })
    comments.value.unshift(res.data)
    commentTotal.value++
    article.value.comment_count = (article.value.comment_count || 0) + 1
    commentContent.value = ''
    ElMessage.success('评论成功')
  } catch {
    ElMessage.error('评论失败')
  } finally {
    commentSubmitting.value = false
  }
}

const handleSubmitReply = async (parentComment) => {
  if (!replyContent.value.trim()) return
  replySubmitting.value = true
  try {
    const res = await submitComment(route.params.id, {
      content: replyContent.value.trim(),
      parent_id: parentComment.id
    })
    if (!parentComment.children) parentComment.children = []
    parentComment.children.push(res.data)
    parentComment.reply_count = (parentComment.reply_count || 0) + 1
    article.value.comment_count = (article.value.comment_count || 0) + 1
    replyContent.value = ''
    replyTarget.value = null
    ElMessage.success('回复成功')
  } catch {
    ElMessage.error('回复失败')
  } finally {
    replySubmitting.value = false
  }
}

const openReplyInput = (comment) => {
  replyTarget.value = comment
  replyContent.value = ''
  nextTick(() => {
    const ta = document.querySelector('.reply-editor textarea')
    if (ta) ta.focus()
  })
}

const cancelReply = () => {
  replyTarget.value = null
  replyContent.value = ''
}

const handleCommentLike = async (comment) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  const prevLiked = comment.is_liked
  const prevCount = comment.like_count || 0
  comment.is_liked = !prevLiked
  comment.like_count = prevCount + (comment.is_liked ? 1 : -1)
  try {
    if (comment.is_liked) {
      await likeComment(comment.id)
    } else {
      await unlikeComment(comment.id)
    }
  } catch {
    comment.is_liked = prevLiked
    comment.like_count = prevCount
  }
}

const handleDeleteComment = async (comment) => {
  try {
    await ElMessageBox.confirm('确定要删除此评论吗？若有子回复也将一并删除。', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await deleteComment(comment.id)
    const deletedCount = res.data?.deleted_count || 1

    // 从本地列表中移除
    comments.value = comments.value.filter(c => c.id !== comment.id)
    // 同时也从子回复中移除 (如果是回复被删除但它在children中)
    for (const c of comments.value) {
      if (c.children) {
        c.children = c.children.filter(r => r.id !== comment.id)
      }
    }
    commentTotal.value = Math.max(0, commentTotal.value - 1)
    article.value.comment_count = Math.max(0, (article.value.comment_count || 0) - deletedCount)
    ElMessage.success('已删除')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const canDeleteComment = (comment) => {
  return userStore.userInfo?.id === comment.user_id
}

// ── 通用 ──
const goTo = (id) => router.push(`/knowledge/${id}`)
const goBack = () => router.push('/knowledge')

onMounted(() => {
  loadArticle()
  loadRecommend()
  loadComments(true)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.knowledge-detail {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px $spacing-lg;
}

:deep(.el-card) {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  .el-card__body {
    padding: 40px;
  }
}

h1 {
  font-size: 30px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 20px;
  line-height: 1.4;
}

.meta {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  color: $text-secondary;
  font-size: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.content {
  font-size: 16px;
  line-height: 1.9;
  color: $text-regular;
  margin-bottom: $spacing-xl;

  :deep(img) {
    max-width: 100%;
    border-radius: 12px;
  }

  :deep(h2), :deep(h3) {
    color: $text-primary;
    margin: 24px 0 12px;
  }

  :deep(blockquote) {
    border-left: 4px solid $primary-color;
    padding: 12px 16px;
    color: $text-secondary;
    background: rgba(232,132,90,0.05);
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
  }
}

// ── 互动按钮 ──
.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;

  .action-btn {
    border-radius: 24px;
    padding: 8px 20px;
    font-weight: 500;
    border: 1px solid $border-base;
    background: $bg-white;
    transition: all 0.2s;

    &:hover {
      border-color: $primary-light;
    }

    &.is-liked {
      color: $primary-color;
      background: rgba(232, 132, 90, 0.08);
      border-color: $primary-lighter;
    }

    &.is-favorited {
      color: #e8b55a;
      background: rgba(232, 181, 90, 0.08);
      border-color: #fce4b8;
    }

    .count-badge {
      margin-left: 4px;
      font-size: 12px;
      color: $text-secondary;
    }
  }
}

// ── 评论区 ──
.comments-section {
  margin-top: $spacing-xl;
}

.comments-header h3 {
  font-size: $font-size-xl;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20px;
}

// 评论输入
.comment-editor {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;

  .editor-avatar {
    flex-shrink: 0;
  }

  .editor-body {
    flex: 1;
    min-width: 0;
  }

  .editor-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;

    .login-hint {
      color: $primary-color;
      font-size: 13px;
      cursor: pointer;
      &:hover { text-decoration: underline; }
    }
  }
}

// 评论列表
.comment-thread {
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid $border-lighter;

  .comment-avatar {
    flex-shrink: 0;
  }

  .comment-body {
    flex: 1;
    min-width: 0;
  }

  .comment-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;

    .comment-author {
      font-weight: 600;
      font-size: $font-size-base;
      color: $text-primary;
    }

    .comment-time {
      font-size: $font-size-extra-small;
      color: $text-placeholder;
    }
  }

  .comment-content {
    font-size: $font-size-base;
    color: $text-regular;
    line-height: 1.7;
    margin-bottom: 8px;
    word-break: break-word;
  }

  .comment-actions {
    display: flex;
    gap: 16px;
    font-size: $font-size-extra-small;
    color: $text-secondary;

    span {
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 2px;
      transition: color 0.2s;

      &:hover { color: $primary-color; }
    }

    .comment-like-btn.liked {
      color: $primary-color;
      font-weight: 600;
    }

    .delete-btn {
      margin-left: auto;
      &:hover { color: $danger-color !important; }
    }
  }
}

// 回复输入 (内联)
.reply-editor {
  margin-top: 12px;
  .reply-editor-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 8px;
  }
}

// 子回复
.child-replies {
  margin-top: 8px;
  margin-left: 44px;
  padding-left: 16px;
  border-left: 2px solid $border-light;
  border-radius: 0;

  .reply-item {
    border-bottom: none;
    padding: 10px 0;

    &:last-child { padding-bottom: 0; }
  }
}

// 加载更多
.load-more {
  text-align: center;
  margin-top: 20px;
}

// 推荐
.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;

  > div {
    cursor: pointer;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid $border-lighter;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(107,82,68,0.12);
    }
  }

  img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    display: block;
  }

  h4 {
    margin: 10px 12px;
    font-size: 14px;
    color: $text-primary;
    font-weight: 600;
  }
}

@media (max-width: $breakpoint-md) {
  .child-replies { margin-left: 20px; }
}
</style>
