<template>
  <!-- 视频/语音通话全屏覆盖层，所有状态由 Pinia callStore 管理 -->
  <Teleport to="body">
    <div v-if="store.callStage !== 'idle'" class="vc-overlay" @click.self="onOverlayClick">
      <!-- ============================================================ -->
      <!-- 阶段1：发起方预检查（checking）                              -->
      <!-- ============================================================ -->
      <template v-if="store.callStage === 'checking'">
        <div class="vc-status-center">
          <div class="vc-spinner" />
          <h3 class="vc-status-title">正在检查设备...</h3>
          <p class="vc-status-desc">检测网络、摄像头和麦克风权限</p>
        </div>
      </template>

      <!-- ============================================================ -->
      <!-- 阶段2：发起方等待接听（calling）                             -->
      <!-- ============================================================ -->
      <template v-else-if="store.callStage === 'calling'">
        <div class="vc-waiting">
          <!-- 本地视频预览 -->
          <video
            v-if="store.localStream"
            ref="localPreviewEl"
            :srcObject="store.localStream"
            autoplay
            playsinline
            muted
            class="vc-local-preview"
          />
          <!-- 无视频时显示头像占位 -->
          <div v-else class="vc-avatar-placeholder">
            <el-avatar :size="100" :src="store.peerAvatar">
              <el-icon :size="50"><User /></el-icon>
            </el-avatar>
            <p>{{ store.peerName }}</p>
          </div>

          <h3 class="vc-status-text">等待对方接受邀请...</h3>
          <p class="vc-timeout-hint">{{ timeoutLeft > 0 ? `将在 ${timeoutLeft} 秒后自动取消` : '' }}</p>

          <div class="vc-actions">
            <div class="vc-btn hangup" @click="store.cancelCall()">
              <el-icon :size="28"><Phone /></el-icon>
              <span>取消</span>
            </div>
          </div>
        </div>
      </template>

      <!-- ============================================================ -->
      <!-- 阶段3：接收方来电（ringing）                                 -->
      <!-- ============================================================ -->
      <template v-else-if="store.callStage === 'ringing'">
        <div class="vc-incoming">
          <el-avatar :size="96" :src="store.peerAvatar" class="vc-incoming-avatar">
            <el-icon :size="48"><User /></el-icon>
          </el-avatar>
          <h2>{{ store.peerName }}</h2>
          <p class="vc-incoming-label">邀请你{{ store.isVoiceOnly ? '语音' : '视频' }}通话</p>

          <div class="vc-incoming-actions">
            <div class="vc-btn hangup" @click="store.rejectCall()">
              <el-icon :size="28"><Phone /></el-icon>
              <span>拒绝</span>
            </div>
            <div class="vc-btn answer" @click="store.acceptCall()">
              <el-icon :size="28"><Phone /></el-icon>
              <span>接听</span>
            </div>
          </div>
        </div>
      </template>

      <!-- ============================================================ -->
      <!-- 阶段4：通话中（connected）                                   -->
      <!-- ============================================================ -->
      <template v-else-if="store.callStage === 'connected'">
        <!-- 子模式：全屏通话 -->
        <template v-if="store.uiMode === 'fullscreen' || store.uiMode === 'screenshare'">
          <!-- 远程画面（或屏幕共享画面） -->
          <video
            v-if="displayStream"
            ref="remoteVideoEl"
            :srcObject="displayStream"
            autoplay
            playsinline
            class="vc-remote-video"
          />
          <!-- 无远程流时显示头像占位 -->
          <div v-else class="vc-avatar-placeholder">
            <el-avatar :size="100" :src="store.peerAvatar">
              <el-icon :size="50"><User /></el-icon>
            </el-avatar>
            <p>{{ store.peerName }}</p>
          </div>

          <!-- 本地画面 PIP（右下角小窗，点击可交换） -->
          <div
            v-if="!store.isVoiceOnly && store.localStream"
            class="vc-pip"
            :class="{ screenshare: store.uiMode === 'screenshare' }"
            @click="swapWindows"
          >
            <video
              ref="localVideoEl"
              :srcObject="store.localStream"
              autoplay
              playsinline
              muted
              class="vc-pip-video"
            />
          </div>

          <!-- 顶部信息栏 -->
          <div class="vc-top-bar">
            <div class="vc-top-left">
              <span class="vc-peer-name">{{ store.peerName }}</span>
              <span v-if="store.uiMode === 'screenshare'" class="vc-sharing-badge">屏幕共享中</span>
            </div>
            <span class="vc-duration">{{ store.formatDuration(store.callDuration) }}</span>
          </div>

          <!-- 底部控制栏 -->
          <div class="vc-bottom-bar">
            <!-- 静音 -->
            <div class="vc-ctrl" :class="{ off: store.isMuted }" @click="store.toggleMute()">
              <el-icon :size="22"><Microphone /></el-icon>
              <span>静音</span>
            </div>

            <!-- 摄像头开关（仅视频通话） -->
            <div
              v-if="!store.isVoiceOnly"
              class="vc-ctrl"
              :class="{ off: store.isCameraOff }"
              @click="store.toggleCamera()"
            >
              <el-icon :size="22"><VideoCamera /></el-icon>
              <span>摄像头</span>
            </div>

            <!-- 屏幕共享 -->
            <div
              class="vc-ctrl"
              :class="{ off: store.isScreenSharing }"
              @click="store.toggleScreenShare()"
            >
              <el-icon :size="22"><Monitor /></el-icon>
              <span>{{ store.isScreenSharing ? '停止共享' : '共享屏幕' }}</span>
            </div>

            <!-- 最小化到悬浮球 -->
            <div class="vc-ctrl" @click="store.minimize()">
              <el-icon :size="22"><Minus /></el-icon>
              <span>最小化</span>
            </div>

            <!-- 挂断 -->
            <div class="vc-btn hangup small" @click="store.hangUp()">
              <el-icon :size="24"><Phone /></el-icon>
            </div>
          </div>
        </template>
      </template>

      <!-- ============================================================ -->
      <!-- 阶段5：通话结束（ended）                                     -->
      <!-- ============================================================ -->
      <template v-else-if="store.callStage === 'ended'">
        <div class="vc-ended">
          <div class="vc-ended-icon">{{ endIcon }}</div>
          <h2>{{ store.endTitle }}</h2>
          <p v-if="store.callDuration > 0">通话时长 {{ store.formatDuration(store.callDuration) }}</p>
        </div>
      </template>
    </div>
  </Teleport>

  <!-- 悬浮球（独立组件） -->
  <CallFloatBall />
</template>

<script setup>
/**
 * 视频/语音通话组件
 *
 * 状态全部由 useCallStore 管理，本组件仅负责 UI 渲染。
 *
 * 状态流转：
 *   idle → checking → calling → connected → ended → idle
 *                         ↓          ↓ (最小化)
 *                      (30s超时)  minimized(悬浮球)
 *   idle → ringing → connected → ended → idle
 *               ↓
 *            (拒绝)
 *
 * 功能：
 * - 发起方预检查（网络/摄像头/麦克风）
 * - 30秒超时自动取消
 * - 接收方来电提醒（头像、名称、接听/拒绝）
 * - 通话中：全屏远程画面 + PIP本地画面 + 底部控制栏
 * - 屏幕共享
 * - 最小化为可拖拽悬浮球
 * - 通话结束显示结果
 */
import { ref, computed, watch, onUnmounted, nextTick, shallowRef } from 'vue'
import { Microphone, Phone, VideoCamera, User, Monitor, Minus } from '@element-plus/icons-vue'
import { useCallStore } from '@/stores/call'
import CallFloatBall from './CallFloatBall.vue'

const store = useCallStore()

// ── 视频元素引用 ──
const localPreviewEl = ref(null)   // calling 阶段的本地预览
const localVideoEl = ref(null)     // connected 阶段的 PIP
const remoteVideoEl = ref(null)    // connected 阶段的远程画面

// ── 30秒超时倒计时 ──
const timeoutLeft = ref(0)
let timeoutInterval = null

// 进入 calling 状态时启动倒计时
watch(() => store.callStage, (stage) => {
  if (stage === 'calling') {
    timeoutLeft.value = 30
    timeoutInterval = setInterval(() => {
      if (timeoutLeft.value > 0) timeoutLeft.value--
    }, 1000)
  } else {
    if (timeoutInterval) { clearInterval(timeoutInterval); timeoutInterval = null }
    timeoutLeft.value = 0
  }
})

// 组件卸载时清理
onUnmounted(() => {
  if (timeoutInterval) clearInterval(timeoutInterval)
})

// ── 视频 srcObject 绑定（解决 v-bind:srcObject 在某些情况下的时序问题） ──

// calling 阶段：绑定本地预览
watch(() => store.localStream, async (stream) => {
  await nextTick()
  if (localPreviewEl.value) {
    localPreviewEl.value.srcObject = stream
    localPreviewEl.value.play().catch(() => {})
  }
}, { immediate: true })

// connected 阶段：绑定远程画面
watch(() => store.remoteStream, async (stream) => {
  await nextTick()
  if (remoteVideoEl.value && stream) {
    remoteVideoEl.value.srcObject = stream
    remoteVideoEl.value.play().catch(() => {})
  }
}, { immediate: true })

// connected 阶段：绑定 PIP 本地画面
watch(() => store.localStream, async (stream) => {
  await nextTick()
  if (localVideoEl.value && stream) {
    localVideoEl.value.srcObject = stream
    localVideoEl.value.play().catch(() => {})
  }
}, { immediate: true })

// ── 显示流（远程画面 or 屏幕共享画面） ──
const displayStream = computed(() => {
  if (store.uiMode === 'screenshare' && store.screenStream) {
    return store.screenStream
  }
  return store.remoteStream
})

// ── PIP 窗口与远程窗口交换 ──
const swapWindows = () => {
  if (!store.remoteStream || !store.localStream) return
  const tmp = store.remoteStream
  store.remoteStream = store.localStream
  store.localStream = tmp
  nextTick(() => {
    if (remoteVideoEl.value) remoteVideoEl.value.srcObject = store.remoteStream
    if (localVideoEl.value) localVideoEl.value.srcObject = store.localStream
  })
}

// ── 结束图标 ──
const endIcon = computed(() => {
  const map = {
    cancel: '📞', reject: '🚫', timeout: '⏰',
    remote_hangup: '📞', hangup: '📞', network_lost: '📡'
  }
  return map[store.endReason] || '📞'
})

// ── 点击覆盖层空白区域（不做什么，避免误关闭） ──
const onOverlayClick = () => {
  // 通话中点击空白不做任何操作
}
</script>

<style lang="scss" scoped>
// ==================== 覆盖层 ====================
.vc-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #0d0d0d;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  user-select: none;
}

// ==================== 通用：头像占位 ====================
.vc-avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  p { font-size: 18px; font-weight: 600; margin: 0; }
}

// ==================== 阶段1：预检查 ====================
.vc-status-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.vc-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: #67c23a;
  border-radius: 50%;
  animation: vcSpin 0.8s linear infinite;
}

@keyframes vcSpin {
  to { transform: rotate(360deg); }
}

.vc-status-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.vc-status-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
}

// ==================== 阶段2：等待接听 ====================
.vc-waiting {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.vc-local-preview {
  width: 66vw;
  max-width: 360px;
  max-height: 55vh;
  border-radius: 20px;
  object-fit: cover;
  background: #1a1a2e;
  transform: scaleX(-1); // 镜像（自拍视角）
}

.vc-status-text {
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.vc-timeout-hint {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
  margin: 0;
  font-variant-numeric: tabular-nums;
}

// ==================== 阶段3：来电 ====================
.vc-incoming {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.vc-incoming-avatar {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

.vc-incoming h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
}

.vc-incoming-label {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.vc-actions, .vc-incoming-actions {
  display: flex;
  gap: 40px;
  margin-top: 8px;
}

// ==================== 按钮 ====================
.vc-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  span { font-size: 12px; color: rgba(255, 255, 255, 0.7); }

  &.hangup { background: #e74c3c; &:hover { background: #c0392b; transform: scale(1.08); } }
  &.answer { background: #27ae60; &:hover { background: #219a52; transform: scale(1.08); } }
  &.small { width: 56px; height: 56px; }
}

// ==================== 阶段4：通话中 ====================
.vc-remote-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #000;
}

// 本地画面 PIP
.vc-pip {
  position: absolute;
  bottom: 100px;
  right: 16px;
  width: 130px;
  height: 170px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  z-index: 10;
  transition: transform 0.15s;
  &:hover { border-color: #fff; transform: scale(1.03); }
  &.screenshare { bottom: 120px; }
}

.vc-pip-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #2a2a3e;
  transform: scaleX(-1); // 镜像
}

// 顶部信息栏
.vc-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.5), transparent);
  z-index: 5;
}

.vc-top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vc-peer-name {
  font-size: 16px;
  font-weight: 600;
}

.vc-sharing-badge {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(103, 194, 58, 0.8);
  color: #fff;
  font-weight: 500;
}

.vc-duration {
  font-variant-numeric: tabular-nums;
  font-weight: 400;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

// 底部控制栏
.vc-bottom-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 16px 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent);
  z-index: 5;
}

.vc-ctrl {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
  transition: all 0.2s;
  span { font-size: 11px; color: rgba(255, 255, 255, 0.6); }
  &:hover { background: rgba(255, 255, 255, 0.2); }
  &.off {
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.3);
    span { color: rgba(255, 255, 255, 0.3); }
  }
}

// ==================== 阶段5：结束 ====================
.vc-ended {
  text-align: center;
  animation: vcFadeIn 0.3s ease-out;
}

.vc-ended-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.vc-ended h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px;
}

.vc-ended p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

@keyframes vcFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

// ==================== 响应式 ====================
@media (max-width: 640px) {
  .vc-pip {
    width: 100px;
    height: 140px;
    bottom: 90px;
    right: 8px;
  }

  .vc-bottom-bar {
    gap: 12px;
    padding: 12px 12px 22px;
  }

  .vc-ctrl {
    padding: 8px 10px;
    span { font-size: 10px; }
  }

  .vc-btn.small { width: 48px; height: 48px; }
  .vc-local-preview { max-width: 280px; }
  .vc-incoming h2 { font-size: 18px; }
  .vc-actions, .vc-incoming-actions { gap: 28px; }
}
</style>
