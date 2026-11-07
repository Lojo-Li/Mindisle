<template>
  <div class="home-page">

    <!-- Hero 区域 -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <div class="hero-text">
            <div class="hero-badge">🌸 专业心理健康服务平台</div>
            <h1 class="hero-title">
              守护您的<span class="highlight">内心世界</span>
              <br>从这里开始
            </h1>
            <p class="hero-desc">
              智能 AI 陪伴、专业心理测试、一对一咨询预约，
              全方位守护您的心理健康，让每一次倾诉都有温暖回应。
            </p>
            <div class="hero-actions">
              <el-button type="primary" size="large" class="hero-btn-primary" @click="navigateTo('/chat')">
                立即体验 →
              </el-button>
              <el-button size="large" class="hero-btn-secondary" @click="navigateTo('/test')">
                测试一下我
              </el-button>
            </div>
          </div>
          <div class="hero-visual">
            <div class="hero-card-stack">
              <div class="floating-card card-1">
                <span class="fc-icon">🤖</span>
                <div>
                  <div class="fc-title">AI 智能陪伴</div>
                  <div class="fc-sub">24小时在线</div>
                </div>
              </div>
              <div class="floating-card card-2">
                <span class="fc-icon">💆</span>
                <div>
                  <div class="fc-title">情绪疏导</div>
                  <div class="fc-sub">专业贴心</div>
                </div>
              </div>
              <div class="floating-card card-3">
                <span class="fc-icon">✨</span>
                <div>
                  <div class="fc-title">好评用户</div>
                  <div class="fc-sub">满意度 98%</div>
                </div>
              </div>
              <div class="hero-main-card">
                <div class="hmc-emoji">🌿</div>
                <p>心灵驿站</p>
                <p class="hmc-sub">您的心理健康守护者</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 背景装饰 -->
      <div class="hero-bg-blob blob-1"></div>
      <div class="hero-bg-blob blob-2"></div>
      <div class="hero-bg-blob blob-3"></div>
    </section>

    <!-- Her → Features 装饰分隔 -->
    <div class="section-divider">
      <svg class="wave-svg" viewBox="0 0 1440 80" preserveAspectRatio="none">
        <path d="M0,40 C360,80 720,0 1440,40 L1440,0 L0,0 Z" fill="#fdf6ee"/>
      </svg>
    </div>

    <!-- 功能导航 -->
    <section class="features-section">
      <div class="section-ornament orn-top"></div>
      <div class="section-ornament orn-right"></div>
      <div class="container">
        <div class="section-header">
          <div class="section-badge">核心功能</div>
          <h2>您需要的，都在这里</h2>
          <p>专为您的心理健康设计的一整套温暖服务</p>
        </div>
        <div class="features-grid">
          <div
            v-for="feature in features"
            :key="feature.id"
            class="feature-card"
            :style="{ '--card-color': feature.color, '--card-bg': feature.bg }"
            @click="navigateTo(feature.path)"
          >
            <div class="feature-icon-wrap">
              <span class="feature-emoji">{{ feature.emoji }}</span>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <span class="feature-arrow">→</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门心理知识 -->
    <section class="knowledge-section">
      <div class="section-ornament orn-left"></div>
      <div class="container">
        <div class="section-header">
          <div class="section-badge">知识专区</div>
          <h2>热门心理知识</h2>
          <p>专业心理学文章，帮助您了解自己</p>
        </div>
        <div class="knowledge-grid">
          <el-skeleton v-if="loadingKnowledge" :rows="3" animated style="grid-column: 1 / -1" />
          <div
            v-for="article in hotArticles"
            :key="article.id"
            class="knowledge-card"
            @click="viewArticle(article.id)"
          >
            <div class="article-cover">
              <img :src="article.coverImage" :alt="article.title" loading="lazy" />
              <div class="article-tag">{{ article.category }}</div>
            </div>
            <div class="article-body">
              <h3>{{ article.title }}</h3>
              <div class="article-meta">
                <span class="meta-views">👁 {{ formatNumber(article.views) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="section-more">
          <el-button class="more-btn" @click="navigateTo('/knowledge')">
            查看更多文章 →
          </el-button>
        </div>
      </div>
    </section>

    <!-- 推荐咨询师 -->
    <section class="counselor-section">
      <div class="section-ornament orn-bottom"></div>
      <div class="container">
        <div class="section-header">
          <div class="section-badge">专家团队</div>
          <h2>推荐咨询师</h2>
          <p>经过严格认证的专业心理咨询师</p>
        </div>
        <div class="counselor-grid">
          <el-skeleton v-if="loadingCounselors" :rows="3" animated style="grid-column: 1 / -1" />
          <div
            v-for="counselor in recommendedCounselors"
            :key="counselor.id"
            class="counselor-card"
          >
            <div class="counselor-top">
              <el-avatar :size="72" :src="counselor.avatar">
                <span style="font-size:28px">👤</span>
              </el-avatar>
              <div class="counselor-badge">推荐</div>
            </div>
            <h3>{{ counselor.name }}</h3>
            <div class="counselor-rating">
              <el-rate v-model="counselor.rating" disabled show-score text-color="#e8845a" />
            </div>
            <div class="counselor-tags">
              <span v-for="tag in counselor.specialties" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <div class="counselor-price">
              <span class="price-num">¥{{ counselor.price }}</span>
              <span class="price-unit">/小时</span>
            </div>
            <el-button type="primary" class="book-btn" @click="bookCounselor(counselor.id)">
              立即预约
            </el-button>
          </div>
        </div>
        <div class="section-more">
          <el-button class="more-btn" @click="navigateTo('/counselor')">
            查看全部咨询师 →
          </el-button>
        </div>
      </div>
    </section>

    <!-- 平台统计 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div v-for="stat in platformStats" :key="stat.id" class="stat-item">
            <div class="stat-icon">{{ stat.emoji }}</div>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(stat.value) }}{{ stat.suffix || '' }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="footer-logo">🌸 心灵驿站</div>
            <p>专注心理健康服务，用专业与温暖陪伴每一位用户走过心灵低谷，找到属于自己的光。</p>
          </div>
          <div class="footer-links">
            <h4>快速导航</h4>
            <ul>
              <li><a href="/chat">智能问答</a></li>
              <li><a href="/test">心理测试</a></li>
              <li><a href="/counselor">找咨询师</a></li>
              <li><a href="/knowledge">心理知识</a></li>
            </ul>
          </div>
          <div class="footer-contact">
            <h4>联系我们</h4>
            <p>📧 support@soulstation.com</p>
            <p>📞 400-123-4567</p>
          </div>
        </div>
        <div class="footer-bottom">
          © 2026 心灵驿站 · 守护您的心理健康 · 保持善良，保持温柔 🌸
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loadingKnowledge = ref(true)
const loadingCounselors = ref(true)

const features = ref([
  {
    id: 1,
    title: '智能问答',
    description: '24h AI 心理咨询助手，随时倾听您的心声',
    emoji: '🤖',
    color: '#e8845a',
    bg: 'rgba(232, 132, 90, 0.08)',
    path: '/chat'
  },
  {
    id: 2,
    title: '心理测试',
    description: '9套专业量表，科学评估心理状态',
    emoji: '📝',
    color: '#9b8bb4',
    bg: 'rgba(155, 139, 180, 0.08)',
    path: '/test'
  },
  {
    id: 3,
    title: '预约咨询',
    description: '专业认证咨询师，一对一贴心服务',
    emoji: '👨‍⚕️',
    color: '#72b087',
    bg: 'rgba(114, 176, 135, 0.08)',
    path: '/counselor'
  },
  {
    id: 4,
    title: '心理知识',
    description: '科普文章与案例，丰富您的心理认知',
    emoji: '📚',
    color: '#e8b55a',
    bg: 'rgba(232, 181, 90, 0.08)',
    path: '/knowledge'
  }
])

const hotArticles = ref([
  {
    id: 1,
    title: '如何缓解焦虑情绪 — 实用技巧分享',
    category: '焦虑症',
    views: 1234,
    coverImage: 'https://images.unsplash.com/photo-1499209974431-2761b8c71e43?w=400'
  },
  {
    id: 2,
    title: '抑郁症的早期信号与自我调节方法',
    category: '抑郁症',
    views: 980,
    coverImage: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'
  },
  {
    id: 3,
    title: '职场压力管理技巧',
    category: '职场',
    views: 856,
    coverImage: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400'
  },
  {
    id: 4,
    title: '改善睡眠质量的科学方法',
    category: '健康睡眠',
    views: 723,
    coverImage: 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=400'
  }
])

const recommendedCounselors = ref([
  {
    id: 1,
    name: '张老师',
    avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200',
    rating: 4.9,
    specialties: ['焦虑', '抑郁', '情感'],
    price: 300
  },
  {
    id: 2,
    name: '李老师',
    avatar: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=200',
    rating: 4.8,
    specialties: ['职场', '家庭', '情感'],
    price: 500
  },
  {
    id: 3,
    name: '王老师',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200',
    rating: 4.9,
    specialties: ['情感', '婚姻', '亲子'],
    price: 400
  },
  {
    id: 4,
    name: '赵老师',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200',
    rating: 4.7,
    specialties: ['学业', '职业', '社交'],
    price: 350
  }
])

const platformStats = ref([
  { id: 1, label: '注册用户', value: 12340, emoji: '👥' },
  { id: 2, label: '专业咨询师', value: 89, emoji: '🩺' },
  { id: 3, label: '服务次数', value: 25670, emoji: '💬' },
  { id: 4, label: '好评满意度', value: 98, emoji: '⭐', suffix: '%' }
])

const formatNumber = (num) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const navigateTo = (path) => router.push(path)
const viewArticle = (id) => router.push(`/knowledge/${id}`)
const bookCounselor = (id) => router.push(`/counselor/${id}`)

onMounted(() => {
  setTimeout(() => {
    loadingKnowledge.value = false
    loadingCounselors.value = false
  }, 800)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.home-page {
  min-height: 100vh;
  background: $bg-page;
}

// ===================== Hero =====================
.hero-section {
  position: relative;
  padding: 100px 0 110px;
  overflow: hidden;
  background: linear-gradient(160deg, #fff8f2 0%, #fdf0e8 50%, #f8eefd 100%);
  min-height: 85vh;
  display: flex;
  align-items: center;
}

.hero-bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;

  &.blob-1 {
    width: 600px; height: 600px;
    background: rgba(232, 132, 90, 0.12);
    top: -180px; right: -120px;
  }

  &.blob-2 {
    width: 450px; height: 450px;
    background: rgba(155, 139, 180, 0.1);
    bottom: -120px; left: -100px;
  }

  &.blob-3 {
    width: 200px; height: 200px;
    background: rgba(144, 196, 216, 0.08);
    top: 40%; left: 10%;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 80px;
}

.hero-text {
  flex: 1;
  padding: 20px 0;

  .hero-badge {
    display: inline-block;
    padding: 8px 20px;
    background: rgba(232, 132, 90, 0.1);
    border: 1px solid rgba(232, 132, 90, 0.25);
    border-radius: 999px;
    font-size: 14px;
    font-weight: 600;
    color: $primary-dark;
    margin-bottom: 28px;
    letter-spacing: 0.5px;
  }

  .hero-title {
    font-size: 56px;
    font-weight: 800;
    line-height: 1.2;
    color: $text-primary;
    margin-bottom: 24px;
    letter-spacing: -1px;

    .highlight {
      background: linear-gradient(135deg, #f4a57a, #c96f42);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .hero-desc {
    font-size: 17px;
    line-height: 1.8;
    color: $text-regular;
    max-width: 540px;
    margin-bottom: 40px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;

    .hero-btn-primary {
      height: 54px;
      padding: 0 36px;
      font-size: 17px;
      font-weight: 700;
      border-radius: 14px !important;
      background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%) !important;
      border: none !important;
      box-shadow: 0 8px 24px rgba(232, 132, 90, 0.38) !important;
      letter-spacing: 1px;

      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(232, 132, 90, 0.48) !important;
      }
    }

    .hero-btn-secondary {
      height: 54px;
      padding: 0 32px;
      font-size: 16px;
      font-weight: 600;
      border-radius: 14px !important;
      background: white !important;
      border: 1.5px solid $border-base !important;
      color: $text-regular !important;

      &:hover {
        border-color: $primary-color !important;
        color: $primary-color !important;
      }
    }
  }
}

.hero-visual {
  flex: 0 0 480px;
  position: relative;
  height: 440px;
}

.hero-card-stack {
  position: relative;
  width: 100%;
  height: 100%;
}

.hero-main-card {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 220px;
  height: 220px;
  background: linear-gradient(140deg, #fde8d8 0%, #f4cdd8 100%);
  border-radius: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 56px rgba(107, 82, 68, 0.18);

  .hmc-emoji { font-size: 64px; margin-bottom: 12px; }
  p { font-size: 17px; font-weight: 700; color: #3d2b1f; }
  .hmc-sub { font-size: 12px; color: #9e8070; margin-top: 4px; }
}

.floating-card {
  position: absolute;
  background: white;
  border-radius: 18px;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(107, 82, 68, 0.12);
  border: 1px solid $border-lighter;
  white-space: nowrap;

  .fc-icon { font-size: 28px; }
  .fc-title { font-size: 14px; font-weight: 600; color: $text-primary; }
  .fc-sub { font-size: 12px; color: $text-secondary; }

  &.card-1 { top: 20px; left: 0; animation: float1 4s ease-in-out infinite; }
  &.card-2 { bottom: 50px; left: 20px; animation: float2 5s ease-in-out 1s infinite; }
  &.card-3 { top: 25px; right: 0; animation: float3 4.5s ease-in-out 0.5s infinite; }
}

@keyframes float1 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
@keyframes float2 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes float3 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

// ===================== Stats =====================
.stats-section {
  padding: 0;
  background: linear-gradient(135deg, #fff8f2 0%, #fdf0e8 50%, #f8eefd 100%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 48px 24px;
  border-right: 1px solid rgba(232, 132, 90, 0.12);
  transition: $transition-base;

  &:hover {
    background: rgba(232, 132, 90, 0.04);
  }

  &:last-child { border-right: none; }

  .stat-icon { font-size: 48px; }
  .stat-value { font-size: 36px; font-weight: 800; color: $primary-color; line-height: 1; }
  .stat-label { font-size: 14px; color: $text-secondary; margin-top: 6px; font-weight: 500; }
}

// ===================== Section Divider (Wave) =====================
.section-divider {
  width: 100%;
  height: 80px;
  overflow: hidden;
  line-height: 0;
  background: transparent;

  .wave-svg {
    width: 100%;
    height: 100%;
  }
}

// ===================== Section Ornaments =====================
.section-ornament {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;

  &.orn-top {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(232, 132, 90, 0.06) 0%, transparent 70%);
    top: -100px;
    right: -60px;
  }

  &.orn-right {
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(155, 139, 180, 0.06) 0%, transparent 70%);
    top: 40%;
    right: -50px;
  }

  &.orn-left {
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(144, 196, 216, 0.06) 0%, transparent 70%);
    bottom: -80px;
    left: -60px;
  }

  &.orn-bottom {
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(232, 181, 90, 0.06) 0%, transparent 70%);
    bottom: -80px;
    right: -40px;
  }
}

// ===================== Sections 通用 =====================
.features-section,
.knowledge-section,
.counselor-section {
  position: relative;
  padding: 96px 0;
}

.section-header {
  text-align: center;
  margin-bottom: 52px;

  .section-badge {
    display: inline-block;
    padding: 6px 18px;
    background: rgba(232, 132, 90, 0.1);
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    color: $primary-dark;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  h2 {
    font-size: 36px;
    font-weight: 800;
    color: $text-primary;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
  }

  p {
    font-size: 16px;
    color: $text-secondary;
  }
}

.section-more {
  text-align: center;
  margin-top: 40px;

  .more-btn {
    border-radius: 999px !important;
    padding: 0 32px !important;
    height: 44px !important;
    border: 1.5px solid $border-base !important;
    color: $text-regular !important;
    font-weight: 600;

    &:hover {
      border-color: $primary-color !important;
      color: $primary-color !important;
    }
  }
}

// ===================== Features =====================
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
}

.feature-card {
  background: white;
  border-radius: 24px;
  padding: 40px 28px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid $border-lighter;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--card-color);
    transform: scaleX(0);
    transition: transform 0.3s;
    transform-origin: left;
  }

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 24px 56px rgba(107, 82, 68, 0.14);
    border-color: rgba(232, 132, 90, 0.2);

    &::before { transform: scaleX(1); }
  }

  .feature-icon-wrap {
    width: 72px;
    height: 72px;
    border-radius: 20px;
    background: var(--card-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    transition: $transition-base;

    .feature-emoji { font-size: 36px; }
  }

  h3 {
    font-size: 20px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    line-height: 1.7;
    color: $text-secondary;
    margin-bottom: 24px;
  }

  .feature-arrow {
    font-size: 18px;
    color: var(--card-color);
    font-weight: 700;
    transition: $transition-base;
  }

  &:hover .feature-arrow {
    letter-spacing: 3px;
  }
}

// ===================== Knowledge =====================
.knowledge-section {
  background: $bg-warm;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.knowledge-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: $transition-base;
  border: 1px solid $border-lighter;

  &:hover {
    transform: translateY(-6px);
    box-shadow: $box-shadow-dark;
  }

  .article-cover {
    position: relative;
    width: 100%;
    height: 180px;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }

    .article-tag {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(255, 255, 255, 0.92);
      border-radius: 999px;
      padding: 4px 12px;
      font-size: 12px;
      font-weight: 600;
      color: $primary-dark;
      backdrop-filter: blur(4px);
    }
  }

  &:hover .article-cover img { transform: scale(1.08); }

  .article-body {
    padding: 18px 20px;

    h3 {
      font-size: 15px;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: 10px;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
      line-height: 1.5;
    }

    .article-meta {
      font-size: 13px;
      color: $text-secondary;
    }
  }
}

// ===================== Counselor =====================
.counselor-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.counselor-card {
  background: white;
  border-radius: 24px;
  padding: 32px 24px;
  text-align: center;
  transition: $transition-base;
  border: 1px solid $border-lighter;

  &:hover {
    transform: translateY(-6px);
    box-shadow: $box-shadow-dark;
    border-color: rgba(232, 132, 90, 0.2);
  }

  .counselor-top {
    position: relative;
    display: flex;
    justify-content: center;
    margin-bottom: 16px;

    .counselor-badge {
      position: absolute;
      top: -2px;
      right: calc(50% - 48px);
      background: $primary-color;
      color: white;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 999px;
    }
  }

  h3 {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 10px;
  }

  .counselor-rating {
    margin-bottom: 14px;
    :deep(.el-rate__icon) { font-size: 18px !important; }
  }

  .counselor-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-bottom: 16px;

    .tag {
      background: rgba(232, 132, 90, 0.08);
      color: $primary-dark;
      font-size: 12px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 999px;
      border: 1px solid rgba(232, 132, 90, 0.2);
    }
  }

  .counselor-price {
    margin-bottom: 18px;

    .price-num { font-size: 24px; font-weight: 800; color: $primary-color; }
    .price-unit { font-size: 13px; color: $text-secondary; }
  }

  .book-btn {
    width: 100%;
    border-radius: 12px !important;
    height: 42px !important;
    font-weight: 600;
  }
}

// ===================== Footer =====================
.page-footer {
  background: #2d1f17;
  color: rgba(255, 255, 255, 0.85);
  padding: 80px 0 32px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 40px;
}

.footer-brand {
  .footer-logo {
    font-size: 22px;
    font-weight: 800;
    color: white;
    margin-bottom: 14px;
    letter-spacing: 1px;
  }

  p {
    font-size: 14px;
    line-height: 1.8;
    color: rgba(255, 255, 255, 0.6);
    max-width: 280px;
  }
}

.footer-links, .footer-contact {
  h4 {
    font-size: 14px;
    font-weight: 700;
    color: white;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  ul {
    list-style: none;

    li {
      margin-bottom: 10px;

      a {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
        text-decoration: none;
        transition: color 0.2s;

        &:hover { color: $primary-light; }
      }
    }
  }

  p {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 8px;
  }
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

// ===================== 响应式 =====================
@media (max-width: 1280px) {
  .hero-text .hero-title { font-size: 46px; }
  .hero-visual { flex: 0 0 400px; }
}

@media (max-width: 1024px) {
  .hero-section { min-height: auto; padding: 72px 0 80px; }
  .features-grid,
  .knowledge-grid,
  .counselor-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .stat-item { padding: 36px 20px; }
  .stat-item:nth-child(2) { border-right: none; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
  .footer-brand { grid-column: 1 / -1; }
  .hero-visual { flex: 0 0 320px; height: 340px; }
  .hero-text .hero-title { font-size: 38px; }
  .hero-content { gap: 48px; }
}

@media (max-width: 768px) {
  .hero-content { flex-direction: column; gap: 48px; }
  .hero-visual { flex: none; width: 100%; height: 300px; }
  .hero-text .hero-title { font-size: 32px; }
  .features-grid,
  .knowledge-grid,
  .counselor-grid { grid-template-columns: 1fr; }
  .features-section,
  .knowledge-section,
  .counselor-section { padding: 64px 0; }
  .section-header h2 { font-size: 28px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .stat-item { padding: 28px 16px; }
  .stat-item .stat-value { font-size: 28px; }
  .footer-grid { grid-template-columns: 1fr; gap: 28px; }
  .page-footer { padding: 48px 0 24px; }
}
</style>
