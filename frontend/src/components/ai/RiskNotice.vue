<template>
  <div v-if="risk && risk.level >= 1" class="risk-notice" :class="`level-${risk.level}`">
    <!-- L1：轻提示，不打断对话 -->
    <div v-if="risk.level === 1" class="l1-row">
      <el-icon class="l1-icon"><InfoFilled /></el-icon>
      <span>如果这种状态已经持续两周以上，找专业咨询师聊一次会比独自扛着更好。</span>
      <button type="button" class="link-btn" @click="$emit('appointment')">看看咨询师</button>
    </div>

    <!-- L2 / L3：常驻横幅 -->
    <template v-else>
      <div class="risk-head">
        <div class="risk-title">
          <el-icon class="risk-icon"><WarningFilled /></el-icon>
          <strong>{{ risk.level === 3 ? '你的安全最重要' : '我们注意到你现在可能不太好受' }}</strong>
        </div>
        <button
          v-if="risk.level === 3"
          type="button"
          class="primary-action"
          @click="$emit('open-dialog')"
        >
          立即查看求助方式
        </button>
        <button
          v-else
          type="button"
          class="ghost-action"
          @click="collapsed = !collapsed"
        >
          {{ collapsed ? '展开' : '收起' }}
        </button>
      </div>

      <div v-show="!collapsed || risk.level === 3" class="risk-body">
        <p class="risk-text">
          {{ risk.level === 3
            ? '如果你现在有伤害自己的念头，请先停一停。这些电话 24 小时有人接，不需要你解释太多。'
            : '这些热线 24 小时免费，可以直接打。你也可以在这里预约一位咨询师。' }}
        </p>

        <div class="hotline-grid">
          <a
            v-for="h in visibleHotlines"
            :key="h.number"
            class="hotline-card"
            :href="`tel:${h.number}`"
          >
            <span class="hotline-name">{{ h.name }}</span>
            <span class="hotline-number">{{ h.number }}</span>
          </a>
        </div>

        <div class="risk-actions">
          <button type="button" class="ghost-action" @click="$emit('appointment')">
            预约咨询师
          </button>
          <button
            v-if="hotlines.length > 2"
            type="button"
            class="link-btn"
            @click="showAll = !showAll"
          >
            {{ showAll ? '收起' : '查看全部热线' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { WarningFilled, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  risk: { type: Object, default: null }
})

defineEmits(['appointment', 'open-dialog'])

const collapsed = ref(false)
const showAll = ref(false)

const hotlines = computed(() => props.risk?.hotlines || [])

const visibleHotlines = computed(() => {
  if (props.risk?.level === 3 || showAll.value) return hotlines.value
  return hotlines.value.slice(0, 2)
})
</script>

<style scoped>
.risk-notice {
  margin: 12px 16px 0;
  border-radius: 12px;
  font-size: 13px;
}

.level-1 {
  background: #fbf7f2;
  border: 1px solid #f0e0d0;
  padding: 8px 12px;
}

.l1-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #9e8070;
  line-height: 1.6;
}

.l1-icon {
  color: #c4b0a4;
  flex-shrink: 0;
}

.level-2 {
  background: #fdf6e8;
  border: 1px solid #f3d9a4;
  padding: 12px 14px;
}

.level-3 {
  background: #fdeeee;
  border: 1px solid #f0b4b4;
  padding: 14px 16px;
}

.risk-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.risk-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.level-2 .risk-title {
  color: #8a5a1a;
}

.level-3 .risk-title {
  color: #a13d3d;
}

.risk-icon {
  flex-shrink: 0;
}

.risk-body {
  margin-top: 8px;
}

.risk-text {
  margin: 0 0 10px;
  line-height: 1.7;
}

.level-2 .risk-text {
  color: #7a6448;
}

.level-3 .risk-text {
  color: #8a4a4a;
}

.hotline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}

.hotline-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 12px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  text-decoration: none;
  transition: all 0.2s ease;
}

.hotline-card:hover {
  border-color: #e8845a;
  transform: translateY(-1px);
}

.hotline-name {
  font-size: 12px;
  color: #9e8070;
}

.hotline-number {
  font-size: 15px;
  font-weight: 500;
  color: #3d2b1f;
  letter-spacing: 0.5px;
}

.risk-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.primary-action {
  padding: 6px 14px;
  border: none;
  border-radius: 999px;
  background: #d9534f;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s ease;
}

.primary-action:hover {
  background: #c0423e;
}

.ghost-action {
  padding: 5px 12px;
  border: 1px solid #e8d5c5;
  border-radius: 999px;
  background: #fff;
  color: #6b5244;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ghost-action:hover {
  border-color: #e8845a;
  color: #cc6b42;
}

.link-btn {
  border: none;
  background: transparent;
  color: #cc6b42;
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
  padding: 0;
}
</style>
