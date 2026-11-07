<template>
  <!-- 通话中最小化时的悬浮球，可拖拽，显示头像和时长 -->
  <Teleport to="body">
    <div
      v-if="store.uiMode === 'minimized' && store.callStage === 'connected'"
      class="cfb-ball"
      :style="ballStyle"
      @mousedown.prevent="startDrag"
      @touchstart.prevent="startDrag"
      @click="onClick"
    >
      <div class="cfb-avatar-wrap">
        <el-avatar :size="44" :src="store.peerAvatar">
          <el-icon :size="22"><User /></el-icon>
        </el-avatar>
        <div class="cfb-pulse" />
      </div>
      <span class="cfb-duration">{{ store.formatDuration(store.callDuration) }}</span>
    </div>
  </Teleport>
</template>

<script setup>
/**
 * 通话悬浮球组件
 * - 在 connected 状态下点击最小化时显示
 * - 支持鼠标/触摸拖拽移动
 * - 显示对方头像和通话时长
 * - 点击恢复全屏通话
 * - 位置范围限制在视口内
 */
import { ref, computed, onUnmounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import { useCallStore } from '@/stores/call'

const store = useCallStore()

// ── 默认位置：右下角 ──
const ballSize = 62 // 悬浮球直径 px
const pos = ref({
  x: store.floatBallPos.x ?? window.innerWidth - ballSize - 16,
  y: store.floatBallPos.y ?? window.innerHeight - ballSize - 100
})

/** 悬浮球行内样式 */
const ballStyle = computed(() => ({
  left: `${pos.value.x}px`,
  top: `${pos.value.y}px`
}))

// ── 拖拽逻辑 ──
let dragging = false
let dragStart = { x: 0, y: 0, left: 0, top: 0 }
let hasMoved = false  // 区分拖拽和点击

/** 开始拖拽 */
const startDrag = (e) => {
  dragging = true
  hasMoved = false
  const point = e.touches ? e.touches[0] : e
  dragStart = {
    x: point.clientX,
    y: point.clientY,
    left: pos.value.x,
    top: pos.value.y
  }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

/** 拖拽中 */
const onDrag = (e) => {
  if (!dragging) return
  const point = e.touches ? e.touches[0] : e
  const dx = point.clientX - dragStart.x
  const dy = point.clientY - dragStart.y
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) hasMoved = true

  // 计算新位置并限制在视口内
  let nx = dragStart.left + dx
  let ny = dragStart.top + dy
  nx = Math.max(0, Math.min(nx, window.innerWidth - ballSize))
  ny = Math.max(0, Math.min(ny, window.innerHeight - ballSize))
  pos.value = { x: nx, y: ny }
}

/** 停止拖拽 */
const stopDrag = () => {
  dragging = false
  store.setFloatBallPos(pos.value.x, pos.value.y)
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
}

/** 点击悬浮球（区分拖拽和点击） */
const onClick = () => {
  if (hasMoved) return  // 拖拽操作不触发恢复
  store.restore()
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})
</script>

<style lang="scss" scoped>
.cfb-ball {
  position: fixed;
  z-index: 10000;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: rgba(30, 30, 40, 0.9);
  backdrop-filter: blur(8px);
  border: 1.5px solid rgba(103, 194, 58, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
  cursor: pointer;
  user-select: none;
  transition: box-shadow 0.2s;
  &:hover { box-shadow: 0 6px 28px rgba(0, 0, 0, 0.5); }
}

.cfb-avatar-wrap {
  position: relative;
  width: 44px;
  height: 44px;
}

.cfb-pulse {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid rgba(103, 194, 58, 0.6);
  animation: cfbPulse 1.5s ease-out infinite;
}

@keyframes cfbPulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.35); opacity: 0; }
}

.cfb-duration {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  font-variant-numeric: tabular-nums;
  margin-top: -2px;
}
</style>
