<template>
  <div class="voice-recorder">
    <div class="microphone-wrapper">
      <!-- 麦克风设备选择器 -->
      <div class="device-selector" v-if="audioDevices.length > 1">
        <el-select
          v-model="selectedDeviceId"
          placeholder="选择麦克风"
          size="small"
          :popper-class="'device-select-popper'"
          @change="onDeviceChanged"
        >
          <el-option
            v-for="device in audioDevices"
            :key="device.deviceId"
            :label="device.label || `麦克风 ${device.deviceId.slice(0, 6)}`"
            :value="device.deviceId"
          >
            <span class="device-option">
              <span class="device-icon">🎤</span>
              <span class="device-label">{{ device.label || `麦克风 ${device.deviceId.slice(0, 6)}` }}</span>
            </span>
          </el-option>
        </el-select>
      </div>

      <el-button
        :icon="Microphone"
        :type="isRecording ? 'danger' : 'default'"
        :disabled="isProcessing"
        :loading="isProcessing"
        @click="toggleRecording"
        circle
        size="large"
      />
    </div>

    <!-- 录音时长 -->
    <div v-if="isRecording" class="recording-info">
      <span class="recording-dot"></span>
      <span>{{ formattedDuration }}</span>
    </div>

    <!-- 音量条 -->
    <div v-if="isRecording" class="volume-bar-container">
      <div class="volume-bar" :style="{ width: `${volumeLevel * 100}%` }"></div>
    </div>

    <!-- 音量过低警告 -->
    <div v-if="isRecording && lowVolumeWarning" class="low-volume-warning">
      ⚠️ 检测不到声音，请检查：麦克风是否开启、系统音量是否过低
    </div>

    <!-- 诊断信息（调试用） -->
    <div v-if="showDiagnostics" class="diagnostics">
      <div>设备: {{ currentDeviceLabel }}</div>
      <div>音量: {{ (volumeLevel * 100).toFixed(1) }}%</div>
      <div>采样值: {{ rawSampleValues.join(', ') }}</div>
      <div>Context: {{ audioContext ? audioContext.state : 'N/A' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Microphone } from '@element-plus/icons-vue'
import { getToken } from '@/utils/storage'

const props = defineProps({
  maxDuration: { type: Number, default: 60 }
})

const emit = defineEmits(['transcription-result'])

const isRecording = ref(false)
const isProcessing = ref(false)
const recordingDuration = ref(0)
const volumeLevel = ref(0)
const lowVolumeWarning = ref(false)
const showDiagnostics = ref(false)

// 设备列表
const audioDevices = ref([])
const selectedDeviceId = ref('')
const currentDeviceLabel = ref('')

// 诊断数据
const rawSampleValues = ref([])

let mediaRecorder = null
let audioChunks = []
let recordingTimer = null
let startTime = null
let selectedMimeType = 'audio/webm'
let audioContext = null
let analyser = null
let microphone = null
let animationFrame = null
let mediaStream = null

const formattedDuration = computed(() => {
  const s = Math.floor(recordingDuration.value / 1000)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
})

/** 检查浏览器是否支持麦克风（需要 HTTPS 或 localhost） */
function isMediaDevicesSupported() {
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
}

/** 页面加载时枚举所有音频输入设备 */
onMounted(async () => {
  if (!isMediaDevicesSupported()) {
    console.warn('[录音] 当前页面不是安全上下文（需要 HTTPS 或 localhost），无法访问麦克风')
    return
  }
  try {
    // 先请求一次麦克风权限，让设备 label 可读（浏览器安全限制，必须在用户手势中才读得到 label）
    const preStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    preStream.getTracks().forEach(t => t.stop())

    const devices = await navigator.mediaDevices.enumerateDevices()
    const inputs = devices.filter(d => d.kind === 'audioinput')
    audioDevices.value = inputs

    if (inputs.length === 0) {
      ElMessage.error('未检测到任何麦克风设备')
      return
    }

    // 默认选中"default"设备
    const def = inputs.find(d => d.deviceId === 'default') || inputs[0]
    selectedDeviceId.value = def.deviceId
    currentDeviceLabel.value = def.label || def.deviceId.slice(0, 8)
  } catch (e) {
    console.error('[录音] 设备枚举失败:', e)
  }
})

/** 切换设备后如果正在录音则停止 */
function onDeviceChanged() {
  if (isRecording.value) {
    stopRecording()
    ElMessage.warning('已切换麦克风，请重新点击录音')
  }
}

const startRecording = async () => {
  // 检查浏览器是否支持麦克风访问
  if (!isMediaDevicesSupported()) {
    ElMessageBox.alert(
      '浏览器无法访问麦克风。\n\n可能原因：\n1. 当前页面未通过 HTTPS 访问（非 localhost 环境需要 HTTPS）\n2. 浏览器不支持麦克风功能\n\n建议：\n• 使用 localhost 访问\n• 或配置 HTTPS 证书后通过 https:// 访问',
      '麦克风不可用',
      { type: 'error', confirmButtonText: '知道了' }
    )
    return
  }
  try {
    // 1. 枚举音频输入设备（每次录音前重新检测，设备可能已插拔）
    const preStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    preStream.getTracks().forEach(t => t.stop())

    const allDevices = await navigator.mediaDevices.enumerateDevices()
    const inputs = allDevices.filter(d => d.kind === 'audioinput')

    if (inputs.length === 0) {
      ElMessage.error('未检测到任何麦克风设备，请检查麦克风是否已连接')
      return
    }

    // 更新设备列表和选项
    audioDevices.value = inputs

    // 如果当前选中的设备已不存在，切换到默认/第一个
    if (selectedDeviceId.value && !inputs.find(d => d.deviceId === selectedDeviceId.value)) {
      const def = inputs.find(d => d.deviceId === 'default') || inputs[0]
      selectedDeviceId.value = def.deviceId
      ElMessage.info(`设备已切换至: ${def.label || '默认麦克风'}`)
    }

    const targetDevice = inputs.find(d => d.deviceId === selectedDeviceId.value)
    currentDeviceLabel.value = targetDevice?.label || selectedDeviceId.value.slice(0, 8)

    // 2. 在用户手势中同步创建 AudioContext
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    audioContext = new AudioCtx()
    if (audioContext.state === 'suspended') {
      await audioContext.resume()
      if (audioContext.state !== 'running') {
        await new Promise(r => setTimeout(r, 100))
        if (audioContext.state === 'suspended') await audioContext.resume()
      }
    }

    // 3. 使用选中的设备获取麦克风流（禁用所有信号处理，避免 Windows AEC 干扰）
    const audioConstraints = {
      deviceId: { exact: selectedDeviceId.value },
      // 关键：不使用 echoCancellation/noiseSuppression/autoGainControl
      // 这些在 Windows 下会被系统 AEC 劫持，导致麦克风输入被静默丢弃
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: audioConstraints })
    const track = mediaStream.getAudioTracks()[0]
    if (!track) throw new Error('未找到音频轨道，请检查麦克风设备')

    console.info('[录音] 轨道设置:', JSON.stringify(track.getSettings()))

    // 4. 建立音频分析器（不连接 destination，避免反馈抑制）
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 1024
    analyser.smoothingTimeConstant = 0.0  // 不平滑，实时反映真实采样值
    microphone = audioContext.createMediaStreamSource(mediaStream)
    microphone.connect(analyser)
    // ❌ 不连接 destination

    // 5. 启动音量监测（直接读原始采样值，不做任何平均/平滑）
    const timeData = new Uint8Array(analyser.frequencyBinCount)
    let lowVolumeCount = 0
    let highVolumeEver = false
    let sampleIndex = 0

    const checkVolume = () => {
      if (!analyser) return
      analyser.getByteTimeDomainData(timeData)

      // 原始采样值展示（取前8个点）
      if (sampleIndex % 6 === 0) {
        rawSampleValues.value = Array.from(timeData.slice(0, 8))
      }
      sampleIndex++

      let maxDeviation = 0
      let sumSq = 0
      for (let i = 0; i < timeData.length; i++) {
        const dev = Math.abs(timeData[i] - 128)
        if (dev > maxDeviation) maxDeviation = dev
        const n = (timeData[i] - 128) / 128
        sumSq += n * n
      }
      const rms = maxDeviation / 128
      volumeLevel.value = Math.min(rms * 4, 1)

      if (rms > 0.02) {
        highVolumeEver = true
        lowVolumeCount = 0
        lowVolumeWarning.value = false
      } else {
        lowVolumeCount++
        if (lowVolumeCount > 180 && highVolumeEver) {
          lowVolumeWarning.value = true
        } else if (lowVolumeCount > 300 && !highVolumeEver) {
          lowVolumeWarning.value = true
        }
      }
      animationFrame = requestAnimationFrame(checkVolume)
    }

    // 让音频数据先流入一帧
    await new Promise(r => setTimeout(r, 100))
    checkVolume()

    // 6. 选择最佳 MIME 类型
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4'
    ]
    let options = { mimeType: 'audio/webm' }
    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        options = { mimeType: type, audioBitsPerSecond: 128000 }
        selectedMimeType = type
        break
      }
    }

    // 7. 初始化 MediaRecorder
    mediaRecorder = new MediaRecorder(mediaStream, options)
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = () => {
      const finalDuration = recordingDuration.value
      cleanup()
      const blob = new Blob(audioChunks, { type: selectedMimeType })
      transcribeAudio(blob, finalDuration)
    }

    mediaRecorder.onerror = () => {
      ElMessage.error('录音发生错误')
      cleanup()
    }

    mediaRecorder.start(250)
    startTime = Date.now()
    isRecording.value = true
    lowVolumeWarning.value = false
    console.info('[录音] 已开始, MIME:', selectedMimeType, 'Context:', audioContext.state)

    recordingTimer = setInterval(() => {
      recordingDuration.value = Date.now() - startTime
      if (recordingDuration.value >= props.maxDuration * 1000) {
        stopRecording()
        ElMessage.warning(`已达到最大录音时长 ${props.maxDuration} 秒`)
      }
    }, 100)

  } catch (error) {
    handleStartError(error)
  }
}

function handleStartError(error) {
  console.error('[录音] 启动失败:', error)
  if (error.name === 'NotAllowedError' || error.message?.includes('permission')) {
    ElMessageBox.alert(
      '麦克风权限被拒绝。\n\n请在浏览器地址栏左侧的"🔒"或"ℹ️"图标中，将"麦克风"权限改为"允许"，然后刷新页面。',
      '麦克风权限被拒绝',
      { type: 'error', confirmButtonText: '知道了' }
    )
  } else if (error.name === 'NotFoundError') {
    ElMessageBox.alert(
      '未找到麦克风设备。请确认：\n1. 麦克风已正确连接\n2. 系统音频设置中麦克风已启用\n3. 未被其他应用独占使用',
      '未找到麦克风',
      { type: 'error', confirmButtonText: '知道了' }
    )
  } else if (error.name === 'NotReadableError') {
    ElMessage.error('麦克风被其他应用占用，请关闭其他使用麦克风的程序后重试')
  } else if (error.name === 'TypeError' && error.message?.includes('getUserMedia')) {
    ElMessageBox.alert(
      '浏览器无法访问麦克风。\n\n可能原因：\n1. 当前页面未通过 HTTPS 访问（非 localhost 环境需要 HTTPS）\n2. 浏览器不支持麦克风功能\n\n建议：\n• 使用 localhost 访问\n• 或配置 HTTPS 证书后通过 https:// 访问',
      '麦克风不可用',
      { type: 'error', confirmButtonText: '知道了' }
    )
  } else {
    ElMessage.error(error.message || '无法启动录音')
  }
  cleanup()
}

function cleanup() {
  if (animationFrame) { cancelAnimationFrame(animationFrame); animationFrame = null }
  if (recordingTimer) { clearInterval(recordingTimer); recordingTimer = null }
  volumeLevel.value = 0
  rawSampleValues.value = []
  lowVolumeWarning.value = false
  isRecording.value = false
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
  if (audioContext) {
    audioContext.close().catch(() => {})
    audioContext = null
    analyser = null
    microphone = null
  }
  mediaRecorder = null
  recordingDuration.value = 0
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
    isProcessing.value = true
  } else {
    cleanup()
  }
}

const toggleRecording = () => {
  isRecording.value ? stopRecording() : startRecording()
}

const getFileExtension = (mimeType) => {
  const map = {
    'audio/webm': 'webm', 'audio/webm;codecs=opus': 'webm',
    'audio/ogg': 'ogg', 'audio/ogg;codecs=opus': 'ogg',
    'audio/mp4': 'm4a', 'audio/mp3': 'mp3'
  }
  return map[mimeType] || 'webm'
}

const transcribeAudio = async (blob, duration) => {
  if (duration < 1000) {
    ElMessage.warning('录音时间太短（至少 1 秒）')
    isProcessing.value = false
    recordingDuration.value = 0
    return
  }
  if (blob.size < 1024) {
    ElMessage.warning('录音数据太小，请重新录制')
    isProcessing.value = false
    recordingDuration.value = 0
    return
  }

  try {
    const token = getToken()
    if (!token) throw new Error('未登录')

    const formData = new FormData()
    formData.append('audio_file', blob, `recording.${getFileExtension(selectedMimeType)}`)
    formData.append('language', 'zh-CN')

    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    const response = await fetch(`${base}/chat/voice-to-text`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '识别失败')
    }

    const result = await response.json()
    if (result.code === 200 && result.data?.text?.trim()) {
      ElMessage.success('语音识别成功')
      emit('transcription-result', result.data.text.trim())
    } else {
      throw new Error('识别结果为空')
    }
  } catch (error) {
    ElMessage.error(error.message || '语音识别失败，请重试')
  } finally {
    isProcessing.value = false
    recordingDuration.value = 0
  }
}
</script>

<style lang="scss" scoped>
.voice-recorder {
  position: relative;
  display: inline-block;
}

.microphone-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-selector {
  :deep(.el-select) {
    .el-input__wrapper {
      background: #f5f7fa;
      border-radius: 20px;
      padding: 0 12px 0 8px;
      transition: all 0.2s;

      &:hover {
        background: #eef0f4;
      }
    }

    .el-input__inner {
      font-size: 12px;
      color: #606266;
    }

    .el-input__suffix {
      .el-select__caret {
        font-size: 14px;
        color: #c0c4cc;
      }
    }
  }
}

.device-option {
  display: flex;
  align-items: center;
  gap: 8px;

  .device-icon {
    font-size: 14px;
    flex-shrink: 0;
  }

  .device-label {
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.recording-info {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f56c6c;
  color: white;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
}

.volume-bar-container {
  position: absolute;
  top: -45px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.volume-bar {
  height: 100%;
  background: linear-gradient(90deg, #67c23a 0%, #e6a23c 70%, #f56c6c 100%);
  transition: width 0.1s ease;
}

.low-volume-warning {
  position: absolute;
  top: -70px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 12px;
  white-space: nowrap;
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.diagnostics {
  position: absolute;
  top: -110px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: #f4f4f5;
  border: 1px solid #d3d3d3;
  border-radius: 4px;
  font-size: 11px;
  color: #666;
  font-family: monospace;
  white-space: nowrap;
  pointer-events: none;
}
</style>

<style lang="scss">
.device-select-popper {
  .el-select-dropdown__item {
    padding: 6px 12px;

    .device-option {
      display: flex;
      align-items: center;
      gap: 8px;

      .device-icon {
        font-size: 14px;
        flex-shrink: 0;
      }

      .device-label {
        font-size: 13px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    &.selected {
      .device-icon { filter: none; }
    }
  }

  .el-select-dropdown__empty {
    padding: 12px;
    font-size: 12px;
    color: #999;
  }
}
</style>
