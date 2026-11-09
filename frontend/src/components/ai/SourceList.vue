<template>
  <div v-if="list.length" class="source-list">
    <button type="button" class="source-toggle" @click="expanded = !expanded">
      <el-icon class="toggle-icon" :class="{ open: expanded }"><ArrowRight /></el-icon>
      <span>参考 {{ list.length }} 条知识</span>
      <span class="top-score" v-if="list[0].score">相似度 {{ toPercent(list[0].score) }}%</span>
    </button>

    <div v-if="expanded" class="source-body">
      <div v-for="(s, i) in list" :key="i" class="source-item">
        <div class="source-head">
          <span class="source-title">{{ s.title || '心理知识片段' }}</span>
          <span class="source-score">{{ toPercent(s.score) }}%</span>
        </div>
        <p class="source-snippet">{{ s.snippet }}</p>
      </div>
      <p class="source-note">
        以上为检索到的知识条目，AI 已用自己的话转述，可对照原文核对。
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { getMessageSources } from '@/api/aiSupport'

const props = defineProps({
  sources: { type: Array, default: () => [] },
  messageId: { type: [Number, String], default: null }
})

const expanded = ref(false)
const loaded = ref([])
const fetching = ref(false)

// 优先用流式过程中已经拿到的来源；历史消息则按需拉取
const list = computed(() => {
  if (props.sources && props.sources.length) return props.sources
  return loaded.value
})

const toPercent = (score) => {
  if (typeof score !== 'number') return '--'
  return Math.round(score * 100)
}

const loadIfNeeded = async () => {
  if (props.sources?.length || loaded.value.length || fetching.value) return
  if (!props.messageId) return
  fetching.value = true
  try {
    const res = await getMessageSources(props.messageId)
    loaded.value = res?.data?.sources || []
  } catch (e) {
    console.warn('获取引用来源失败', e)
  } finally {
    fetching.value = false
  }
}

watch(expanded, (val) => {
  if (val) loadIfNeeded()
})
</script>

<style scoped>
.source-list {
  margin-top: 8px;
}

.source-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: 1px solid #f0e0d0;
  border-radius: 999px;
  background: #fffaf6;
  color: #9e8070;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.source-toggle:hover {
  border-color: #e8845a;
  color: #cc6b42;
}

.toggle-icon {
  transition: transform 0.2s ease;
  font-size: 12px;
}

.toggle-icon.open {
  transform: rotate(90deg);
}

.top-score {
  color: #72b087;
}

.source-body {
  margin-top: 8px;
  padding: 12px;
  border-radius: 10px;
  background: #fffaf6;
  border: 1px solid #f6ece4;
}

.source-item + .source-item {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #f0e0d0;
}

.source-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.source-title {
  font-size: 12px;
  font-weight: 500;
  color: #6b5244;
}

.source-score {
  font-size: 11px;
  color: #72b087;
  white-space: nowrap;
}

.source-snippet {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: #9e8070;
}

.source-note {
  margin: 10px 0 0;
  font-size: 11px;
  color: #c4b0a4;
}
</style>
