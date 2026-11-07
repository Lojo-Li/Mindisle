/**
 * 视频/语音通话全局状态管理
 * 管理完整的通话生命周期：idle → checking → calling/ringing → connected → ended
 * 与聊天状态分离，支持悬浮球和聊天页面跨组件共享
 */
import { ref, computed, shallowRef } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import { getSignalMessages, sendSignalMessage, clearSignals } from '@/api/consultation'

// ── 常量 ──
const CALL_TIMEOUT = 30000        // 30秒超时
const SIGNAL_POLL_INTERVAL = 800  // 信令轮询间隔
const ENDED_AUTO_CLOSE_DELAY = 2000 // 结束后自动关闭延时
const RTC_CONFIG = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
}

export const useCallStore = defineStore('call', () => {
  // ==================== 核心状态 ====================
  const callStage = ref('idle')      // idle | checking | calling | ringing | connected | ended
  const uiMode = ref('fullscreen')   // fullscreen | minimized | screenshare
  const appointmentId = ref(null)
  const consultationType = ref('video')
  const peerName = ref('')
  const peerAvatar = ref('')
  const isCaller = ref(false)
  const callDuration = ref(0)        // 通话秒数
  const endReason = ref('')          // cancel | reject | timeout | remote_hangup | hangup | check_failed | network_lost
  const isMuted = ref(false)
  const isCameraOff = ref(false)
  const isScreenSharing = ref(false)
  const floatBallPos = ref({ x: null, y: null })  // 悬浮球坐标（null=默认位置）

  // ── WebRTC 相关（使用 shallowRef 避免深度响应式导致性能问题） ──
  const localStream = shallowRef(null)     // MediaStream | null
  const remoteStream = shallowRef(null)    // MediaStream | null
  const screenStream = shallowRef(null)    // MediaStream | null（屏幕共享流）
  const pc = shallowRef(null)              // RTCPeerConnection | null
  const pendingOffer = shallowRef(null)    // 暂存的 SDP offer
  const pendingIce = shallowRef([])        // 暂存的 ICE candidates

  // ── 内部变量（不需要响应式） ──
  let callTimer = null
  let timeoutTimer = null
  let signalPoller = null
  let lastSignalId = 0
  let soundCtx = null        // AudioContext
  let soundTimer = null      // 铃声循环定时器
  let soundsStopped = false  // 铃声是否已停止

  // ==================== 计算属性 ====================
  /** 是否正在通话中（不能发起新通话） */
  const isBusy = computed(() => {
    return callStage.value !== 'idle' && callStage.value !== 'ended'
  })

  /** 通话是否已接通 */
  const isCallActive = computed(() => callStage.value === 'connected')

  /** 是否为纯语音通话 */
  const isVoiceOnly = computed(() => consultationType.value === 'voice')

  /** 当前状态可读文本 */
  const statusText = computed(() => {
    const map = {
      idle: '空闲',
      checking: '正在检查设备...',
      calling: '等待对方接听...',
      ringing: '来电中...',
      connected: '通话中',
      ended: '通话已结束'
    }
    return map[callStage.value] || ''
  })

  /** 结束原因可读文本 */
  const endTitle = computed(() => {
    const map = {
      cancel: '已取消',
      reject: '对方已拒绝',
      timeout: '对方无应答',
      remote_hangup: '对方已挂断',
      hangup: '已挂断',
      network_lost: '通话已断开',
      check_failed: '发起失败'
    }
    return map[endReason.value] || '通话已结束'
  })

  // ==================== 内部工具函数 ====================

  /** 格式化秒数为 mm:ss */
  const formatDuration = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  }

  /** 播放来电铃声（Web Audio API 模拟重复提示音） */
  const startRingSound = () => {
    try {
      soundCtx = new (window.AudioContext || window.webkitAudioContext)()
      soundsStopped = false
      const playBeep = () => {
        if (soundsStopped || !soundCtx) return
        const osc = soundCtx.createOscillator()
        const gain = soundCtx.createGain()
        osc.connect(gain)
        gain.connect(soundCtx.destination)
        osc.type = 'sine'
        osc.frequency.setValueAtTime(800, soundCtx.currentTime)
        osc.frequency.setValueAtTime(1000, soundCtx.currentTime + 0.15)
        gain.gain.setValueAtTime(0.3, soundCtx.currentTime)
        gain.gain.exponentialRampToValueAtTime(0.01, soundCtx.currentTime + 0.4)
        osc.start(soundCtx.currentTime)
        osc.stop(soundCtx.currentTime + 0.4)
      }
      playBeep()
      soundTimer = setInterval(playBeep, 1600)
    } catch { /* 忽略音频播放失败 */ }
  }

  /** 停止所有铃声 */
  const stopAllSounds = () => {
    soundsStopped = true
    if (soundTimer) { clearInterval(soundTimer); soundTimer = null }
    if (soundCtx) { soundCtx.close().catch(() => {}); soundCtx = null }
  }

  // ==================== 信令轮询 ====================

  const startSignalPolling = () => {
    stopSignalPolling()
    signalPoller = setInterval(pollSignals, SIGNAL_POLL_INTERVAL)
  }

  const stopSignalPolling = () => {
    if (signalPoller) { clearInterval(signalPoller); signalPoller = null }
  }

  const pollSignals = async () => {
    if (!appointmentId.value) return
    try {
      const res = await getSignalMessages(appointmentId.value, lastSignalId || 0)
      const items = res.data?.items || []
      for (const m of items) {
        if (m.id > lastSignalId) lastSignalId = m.id
        await handleSignal(m)
      }
    } catch { /* 网络错误静默处理 */ }
  }

  /** 处理收到的信令消息 */
  const handleSignal = async (msg) => {
    const SIGNAL_TYPES = ['webrtc_offer', 'webrtc_answer', 'webrtc_ice', 'webrtc_hangup']
    if (!SIGNAL_TYPES.includes(msg.message_type)) return

    let data = {}
    try { data = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content } catch { return }

    switch (msg.message_type) {
      case 'webrtc_offer': {
        // 发起方忽略收到的 offer（自己发的 offer 不会进入此分支，但防御性保留）
        if (isCaller.value) return
        // 接收方：如果不在 idle 状态（已在通话中），自动拒绝
        if (callStage.value !== 'idle') {
          await sendSignalMessage(appointmentId.value, 'webrtc_hangup', { reason: 'busy' }).catch(() => {})
          return
        }
        pendingOffer.value = { type: data.type, sdp: data.sdp }
        callStage.value = 'ringing'
        startRingSound()
        startSignalPolling()
        break
      }

      case 'webrtc_answer': {
        // 发起方：对方已接听
        if (!pc.value || !isCaller.value) return
        await pc.value.setRemoteDescription(new RTCSessionDescription(data))
        // 处理在收到 answer 前缓存的 ICE candidates
        for (const ice of pendingIce.value) {
          await pc.value.addIceCandidate(new RTCIceCandidate(ice))
        }
        pendingIce.value = []
        break
      }

      case 'webrtc_ice': {
        // 双方都可能收到
        if (!data.candidate) return
        if (pc.value?.remoteDescription) {
          await pc.value.addIceCandidate(new RTCIceCandidate(data.candidate))
        } else {
          pendingIce.value.push(data.candidate)
        }
        break
      }

      case 'webrtc_hangup': {
        // 任意一方挂断
        if (callStage.value === 'ringing') {
          endReason.value = 'cancel'
        } else if (callStage.value === 'calling') {
          endReason.value = data.reason === 'reject' ? 'reject' : 'timeout'
        } else if (callStage.value === 'connected') {
          endReason.value = 'remote_hangup'
        } else {
          return
        }
        showEnd()
        break
      }
    }
  }

  // ==================== 媒体设备 ====================

  /** 获取本地音视频流 */
  const getLocalStream = async () => {
    const constraints = {
      audio: true,
      video: !isVoiceOnly.value
        ? { width: { ideal: 720 }, height: { ideal: 480 }, facingMode: 'user' }
        : false
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      localStream.value = stream
      return stream
    } catch (e) {
      const msg = e.name === 'NotAllowedError' ? '请允许摄像头和麦克风权限'
        : e.name === 'NotReadableError' ? '设备被占用，请关闭其他应用后重试'
        : '无法访问媒体设备'
      ElMessage.error(msg)
      throw e
    }
  }

  // ==================== WebRTC 连接 ====================

  /** 创建 RTCPeerConnection 并绑定事件 */
  const createPeerConnection = (stream) => {
    const conn = new RTCPeerConnection(RTC_CONFIG)

    // 添加本地流的所有轨
    stream.getTracks().forEach(t => conn.addTrack(t, stream))

    // 收到远程流
    conn.ontrack = (event) => {
      // 兼容不同浏览器的 ontrack 实现
      const s = event.streams[0] || (() => {
        const ms = new MediaStream()
        ms.addTrack(event.track)
        return ms
      })()
      remoteStream.value = s
    }

    // 发送 ICE candidate 给对方
    conn.onicecandidate = (e) => {
      if (e.candidate) {
        sendSignalMessage(appointmentId.value, 'webrtc_ice', {
          candidate: e.candidate.toJSON()
        }).catch(() => {})
      }
    }

    // 监听连接状态变化
    conn.onconnectionstatechange = () => {
      const state = conn.connectionState
      if (state === 'connected') {
        // 连接成功
        callStage.value = 'connected'
        stopAllSounds()
        startCallTimer()
        // 清除超时定时器
        if (timeoutTimer) { clearTimeout(timeoutTimer); timeoutTimer = null }
      } else if (state === 'disconnected' || state === 'failed' || state === 'closed') {
        // 连接断开（对方关闭浏览器、网络中断等）
        if (callStage.value === 'connected') {
          endReason.value = 'network_lost'
          showEnd()
        } else if (callStage.value !== 'idle' && callStage.value !== 'ended') {
          endReason.value = 'network_lost'
          showEnd()
        }
      }
    }

    pc.value = conn
    return conn
  }

  // ==================== 预检查（发起方） ====================

  /** 检测网络连接 */
  const checkNetwork = () => {
    if (!navigator.onLine) {
      return { ok: false, error: '当前网络不可用，请检查网络连接' }
    }
    return { ok: true }
  }

  /** 检测摄像头可用性 */
  const checkCamera = async () => {
    if (isVoiceOnly.value) return { ok: true }
    // 先检查设备是否存在
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      const hasCamera = devices.some(d => d.kind === 'videoinput')
      if (!hasCamera) return { ok: false, error: '未检测到摄像头设备' }
    } catch { /* enumerateDevices 失败继续尝试 getUserMedia */ }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      stream.getTracks().forEach(t => t.stop())
      return { ok: true }
    } catch (e) {
      if (e.name === 'NotAllowedError') return { ok: false, error: '摄像头权限被拒绝，请在浏览器设置中允许摄像头访问' }
      if (e.name === 'NotFoundError') return { ok: false, error: '未检测到摄像头设备' }
      return { ok: false, error: '无法访问摄像头：' + e.message }
    }
  }

  /** 检测麦克风可用性 */
  const checkMicrophone = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      const hasMic = devices.some(d => d.kind === 'audioinput')
      if (!hasMic) return { ok: false, error: '未检测到麦克风设备' }
    } catch { /* 继续 */ }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      stream.getTracks().forEach(t => t.stop())
      return { ok: true }
    } catch (e) {
      if (e.name === 'NotAllowedError') return { ok: false, error: '麦克风权限被拒绝，请在浏览器设置中允许麦克风访问' }
      if (e.name === 'NotFoundError') return { ok: false, error: '未检测到麦克风设备' }
      return { ok: false, error: '无法访问麦克风：' + e.message }
    }
  }

  // ==================== 通话控制（actions） ====================

  /** 发起方入口：初始化通话 */
  const initiateCall = async ({ appointmentId: aId, type, peerName: pName, peerAvatar: pAvatar }) => {
    if (isBusy.value) {
      ElMessage.warning('当前正在通话中，请先结束当前通话')
      return
    }

    // 设置通话参数
    appointmentId.value = aId
    consultationType.value = type
    peerName.value = pName
    peerAvatar.value = pAvatar
    isCaller.value = true
    callDuration.value = 0
    lastSignalId = 0

    await startCall()
  }

  /** 发起方：执行预检查并开始通话 */
  const startCall = async () => {
    // 1. 预检查阶段
    callStage.value = 'checking'

    // 网络检查
    const netCheck = checkNetwork()
    if (!netCheck.ok) {
      endReason.value = 'check_failed'
      ElMessage.error(netCheck.error)
      await sleep(600)
      reset()
      return
    }

    // 摄像头检查
    const camCheck = await checkCamera()
    if (!camCheck.ok) {
      endReason.value = 'check_failed'
      ElMessage.error(camCheck.error)
      await sleep(600)
      reset()
      return
    }

    // 麦克风检查
    const micCheck = await checkMicrophone()
    if (!micCheck.ok) {
      endReason.value = 'check_failed'
      ElMessage.error(micCheck.error)
      await sleep(600)
      reset()
      return
    }

    // 2. 清除旧信令
    await clearSignals(aId()).catch(() => {})

    // 3. 获取本地媒体流
    try {
      await getLocalStream()
    } catch {
      endReason.value = 'check_failed'
      await sleep(600)
      reset()
      return
    }

    // 4. 创建 PeerConnection
    const conn = createPeerConnection(localStream.value)

    // 5. 创建并发送 offer，记录消息 ID 用于信令轮询
    const offer = await conn.createOffer()
    await conn.setLocalDescription(offer)
    const offerRes = await sendSignalMessage(appointmentId.value, 'webrtc_offer', {
      type: offer.type,
      sdp: offer.sdp
    })
    // 使用 offer 消息的数据库 ID 作为轮询起点，确保只获取后续的 answer/ICE
    lastSignalId = offerRes.data?.id || 0

    // 6. 进入 calling 状态
    callStage.value = 'calling'
    startSignalPolling()

    // 7. 30秒超时计时
    timeoutTimer = setTimeout(() => {
      if (callStage.value === 'calling') {
        sendSignalMessage(appointmentId.value, 'webrtc_hangup', { reason: 'timeout' }).catch(() => {})
        endReason.value = 'timeout'
        showEnd()
      }
    }, CALL_TIMEOUT)
  }

  /** 接收方：收到来电（由聊天页面 checkIncomingCall 触发） */
  const receiveOffer = (msg) => {
    if (callStage.value !== 'idle') return

    let data = {}
    try { data = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content } catch { return }

    appointmentId.value = msg.appointment_id
    isCaller.value = false
    callDuration.value = 0
    pendingOffer.value = { type: data.type, sdp: data.sdp }
    // 记录 offer 消息的数据库 ID，防止信令轮询重复处理导致误发 busy
    lastSignalId = msg.id || 0
    callStage.value = 'ringing'
    startRingSound()
    startSignalPolling()
  }

  /** 接收方：接听来电 */
  const acceptCall = async () => {
    stopAllSounds()
    try {
      const stream = await getLocalStream()
      const conn = createPeerConnection(stream)

      // 设置远程 SDP
      if (pendingOffer.value) {
        await conn.setRemoteDescription(new RTCSessionDescription(pendingOffer.value))
        const answer = await conn.createAnswer()
        await conn.setLocalDescription(answer)
        await sendSignalMessage(appointmentId.value, 'webrtc_answer', {
          type: answer.type,
          sdp: answer.sdp
        })
      }

      // 添加缓存的 ICE candidates
      for (const ice of pendingIce.value) {
        await conn.addIceCandidate(new RTCIceCandidate(ice))
      }
      pendingIce.value = []
      pendingOffer.value = null

      callStage.value = 'connected'
      startCallTimer()
    } catch (e) {
      console.error('接听失败:', e)
      ElMessage.error('接听失败，请重试')
      endReason.value = 'check_failed'
      showEnd()
    }
  }

  /** 接收方：拒绝来电 */
  const rejectCall = async () => {
    stopAllSounds()
    await sendSignalMessage(appointmentId.value, 'webrtc_hangup', { reason: 'reject' }).catch(() => {})
    endReason.value = 'reject'
    showEnd()
  }

  /** 发起方：取消呼叫 */
  const cancelCall = async () => {
    stopAllSounds()
    await sendSignalMessage(appointmentId.value, 'webrtc_hangup', { reason: 'cancel' }).catch(() => {})
    endReason.value = 'cancel'
    showEnd()
  }

  /** 通话中：挂断 */
  const hangUp = async () => {
    stopAllSounds()
    await sendSignalMessage(appointmentId.value, 'webrtc_hangup', {}).catch(() => {})
    endReason.value = 'hangup'
    showEnd()
  }

  /** 显示结束状态，定时后自动关闭 */
  const showEnd = () => {
    const wasConnected = callStage.value === 'connected'
    const dur = wasConnected ? callDuration.value : 0
    callStage.value = 'ended'
    stopAllSounds()
    stopCallTimer()
    stopSignalPolling()
    if (timeoutTimer) { clearTimeout(timeoutTimer); timeoutTimer = null }
    cleanupMedia()

    // 通知聊天页面记录系统消息
    // 通过 event 机制让聊天页面处理（避免直接引入聊天 store 造成循环依赖）
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('call-ended', {
        detail: { endReason: endReason.value, duration: dur, appointmentId: appointmentId.value }
      }))
    }

    // 2秒后自动关闭
    setTimeout(() => {
      reset()
    }, ENDED_AUTO_CLOSE_DELAY)
  }

  // ==================== 通话中控制 ====================

  /** 切换静音 */
  const toggleMute = () => {
    if (!localStream.value) return
    isMuted.value = !isMuted.value
    localStream.value.getAudioTracks().forEach(t => { t.enabled = !isMuted.value })
  }

  /** 切换摄像头 */
  const toggleCamera = () => {
    if (!localStream.value) return
    isCameraOff.value = !isCameraOff.value
    localStream.value.getVideoTracks().forEach(t => { t.enabled = !isCameraOff.value })
  }

  /** 切换屏幕共享 */
  const toggleScreenShare = async () => {
    if (isScreenSharing.value) {
      stopScreenShare()
      return
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true })
      screenStream.value = stream
      isScreenSharing.value = true
      uiMode.value = 'screenshare'

      // 替换发送的视频轨为屏幕共享轨
      const sender = pc.value?.getSenders().find(s => s.track?.kind === 'video')
      const screenTrack = stream.getVideoTracks()[0]
      if (sender && screenTrack) {
        await sender.replaceTrack(screenTrack)
      }

      // 用户通过浏览器 UI 关闭共享时自动恢复
      screenTrack.onended = () => {
        stopScreenShare()
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        ElMessage.error('无法启动屏幕共享')
      }
    }
  }

  /** 停止屏幕共享，恢复摄像头画面 */
  const stopScreenShare = () => {
    const sender = pc.value?.getSenders().find(s => s.track?.kind === 'video')
    const cameraTrack = localStream.value?.getVideoTracks()[0]
    if (sender && cameraTrack) {
      sender.replaceTrack(cameraTrack)
    }
    screenStream.value?.getTracks().forEach(t => t.stop())
    screenStream.value = null
    isScreenSharing.value = false
    if (uiMode.value === 'screenshare') {
      uiMode.value = 'fullscreen'
    }
  }

  /** 最小化到悬浮球 */
  const minimize = () => {
    uiMode.value = 'minimized'
  }

  /** 从悬浮球恢复全屏 */
  const restore = () => {
    uiMode.value = isScreenSharing.value ? 'screenshare' : 'fullscreen'
  }

  /** 设置悬浮球位置 */
  const setFloatBallPos = (x, y) => {
    floatBallPos.value = { x, y }
  }

  // ==================== 计时器 ====================

  const startCallTimer = () => {
    callDuration.value = 0
    callTimer = setInterval(() => { callDuration.value++ }, 1000)
  }

  const stopCallTimer = () => {
    if (callTimer) { clearInterval(callTimer); callTimer = null }
  }

  // ==================== 资源清理 ====================

  /** 清理所有媒体资源和连接 */
  const cleanupMedia = () => {
    // 停止所有媒体轨
    localStream.value?.getTracks().forEach(t => t.stop())
    remoteStream.value?.getTracks().forEach(t => t.stop())
    screenStream.value?.getTracks().forEach(t => t.stop())
    localStream.value = null
    remoteStream.value = null
    screenStream.value = null

    // 关闭 PeerConnection
    pc.value?.close()
    pc.value = null

    // 清除信令缓存
    pendingOffer.value = null
    pendingIce.value = []
  }

  /** 完全重置到初始状态 */
  const reset = () => {
    stopAllSounds()
    stopCallTimer()
    stopSignalPolling()
    if (timeoutTimer) { clearTimeout(timeoutTimer); timeoutTimer = null }
    cleanupMedia()

    callStage.value = 'idle'
    uiMode.value = 'fullscreen'
    appointmentId.value = null
    consultationType.value = 'video'
    peerName.value = ''
    peerAvatar.value = ''
    isCaller.value = false
    callDuration.value = 0
    endReason.value = ''
    isMuted.value = false
    isCameraOff.value = false
    isScreenSharing.value = false
    lastSignalId = 0
    floatBallPos.value = { x: null, y: null }
  }

  // ==================== 工具 ====================

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

  // 辅助：简化 appointmentId 取值
  const aId = () => appointmentId.value

  return {
    // 状态
    callStage, uiMode, appointmentId, consultationType, peerName, peerAvatar,
    isCaller, callDuration, endReason, isMuted, isCameraOff, isScreenSharing,
    floatBallPos, localStream, remoteStream, screenStream,
    pc, pendingOffer, pendingIce,
    // 计算属性
    isBusy, isCallActive, isVoiceOnly, statusText, endTitle,
    formatDuration,
    // 通话生命周期
    initiateCall, receiveOffer, startCall,
    // 接听/拒绝/取消/挂断
    acceptCall, rejectCall, cancelCall, hangUp,
    // 通话中控制
    toggleMute, toggleCamera, toggleScreenShare, stopScreenShare,
    minimize, restore, setFloatBallPos,
    // 信令
    startSignalPolling, stopSignalPolling,
    // 资源管理
    cleanupMedia, reset,
    // 铃音
    startRingSound, stopAllSounds
  }
})
