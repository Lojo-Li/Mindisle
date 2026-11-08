<template>
  <el-dialog
    :model-value="modelValue"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="460px"
    top="12vh"
    custom-class="risk-dialog"
    @update:model-value="(v) => $emit('update:modelValue', v)"
  >
    <div class="rd-body">
      <div class="rd-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>

      <h3 class="rd-title">你的安全最重要</h3>

      <p class="rd-text">
        你刚才说的话让我有点担心你。在继续聊之前，我想先把几个能立刻联系到人的方式放在这里。
      </p>
      <p class="rd-text rd-text-strong">
        这些电话 24 小时有人接，不需要你说明太多，也不用先想好怎么开口。
      </p>

      <div class="rd-hotlines">
        <a
          v-for="h in hotlines"
          :key="h.number"
          class="rd-hotline"
          :href="`tel:${h.number}`"
        >
          <div class="rd-hotline-main">
            <span class="rd-hotline-name">{{ h.name }}</span>
            <span class="rd-hotline-desc">{{ h.description }}</span>
          </div>
          <span class="rd-hotline-number">{{ h.number }}</span>
        </a>
      </div>

      <div class="rd-secondary">
        <button type="button" class="rd-ghost" @click="$emit('appointment')">
          预约一位咨询师
        </button>
      </div>

      <label class="rd-confirm">
        <input v-model="confirmed" type="checkbox" />
        <span>我知道了，可以先看这些求助方式</span>
      </label>

      <button
        type="button"
        class="rd-submit"
        :disabled="!confirmed"
        @click="handleConfirm"
      >
        {{ confirmed ? '继续对话' : '请先确认你已看到上面的信息' }}
      </button>

      <p class="rd-footnote">
        AI 无法替代专业帮助。如果你现在就在危险中，请立即拨打 110 或 120。
      </p>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  risk: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'appointment', 'confirmed'])

const confirmed = ref(false)

const hotlines = computed(() => props.risk?.hotlines || [])

// 每次重新弹出都要求重新确认，避免用户被反复打扰又草率点过
watch(() => props.modelValue, (val) => {
  if (val) confirmed.value = false
})

const handleConfirm = () => {
  if (!confirmed.value) return
  emit('confirmed')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.rd-body {
  padding: 4px 6px 8px;
  text-align: center;
}

.rd-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 10px;
  border-radius: 50%;
  background: #fdeeee;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d9534f;
  font-size: 22px;
}

.rd-title {
  margin: 0 0 10px;
  font-size: 17px;
  font-weight: 500;
  color: #3d2b1f;
}

.rd-text {
  margin: 0 0 6px;
  font-size: 13px;
  line-height: 1.7;
  color: #6b5244;
  text-align: left;
}

.rd-text-strong {
  color: #3d2b1f;
}

.rd-hotlines {
  margin: 14px 0 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rd-hotline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #fdf6f5;
  border: 1px solid #f0d0cd;
  text-decoration: none;
  transition: all 0.2s ease;
}

.rd-hotline:hover {
  border-color: #d9534f;
  background: #fdeeee;
}

.rd-hotline-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: left;
}

.rd-hotline-name {
  font-size: 13px;
  color: #3d2b1f;
}

.rd-hotline-desc {
  font-size: 11px;
  color: #9e8070;
}

.rd-hotline-number {
  font-size: 16px;
  font-weight: 500;
  color: #a13d3d;
  white-space: nowrap;
}

.rd-secondary {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.rd-ghost {
  padding: 6px 14px;
  border: 1px solid #e8d5c5;
  border-radius: 999px;
  background: #fff;
  color: #6b5244;
  font-size: 12px;
  cursor: pointer;
}

.rd-ghost:hover {
  border-color: #e8845a;
  color: #cc6b42;
}

.rd-confirm {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: #6b5244;
  cursor: pointer;
  margin-bottom: 10px;
}

.rd-submit {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: #d9534f;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.rd-submit:disabled {
  background: #e8d5c5;
  color: #a08d80;
  cursor: not-allowed;
}

.rd-footnote {
  margin: 10px 0 0;
  font-size: 11px;
  color: #c4b0a4;
}
</style>
