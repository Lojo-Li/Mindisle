<template>
  <div v-if="messageId" class="answer-feedback">
    <template v-if="!submitted">
      <span class="ask">这条回答有帮助吗？</span>
      <button type="button" class="fb-btn" @click="vote(1)">有帮助</button>
      <button type="button" class="fb-btn" @click="vote(-1)">没帮助</button>
    </template>
    <span v-else class="thanks">感谢反馈，会用来改进知识库</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitFeedback } from '@/api/aiSupport'

const props = defineProps({
  messageId: { type: [Number, String], default: null }
})

const submitted = ref(false)

const vote = async (rating) => {
  if (!props.messageId) return
  submitted.value = true
  try {
    await submitFeedback({ message_id: Number(props.messageId), rating })
  } catch (e) {
    // 反馈失败不打扰用户，静默处理
    console.warn('反馈提交失败', e)
  }
}
</script>

<style scoped>
.answer-feedback {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 12px;
}

.ask {
  color: #c4b0a4;
}

.fb-btn {
  border: none;
  background: transparent;
  color: #9e8070;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.fb-btn:hover {
  background: #fdf1e9;
  color: #cc6b42;
}

.thanks {
  color: #72b087;
}
</style>
