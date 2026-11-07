<template>
  <div class="privacy-page">
    <div class="container">

      <!-- 页头 -->
      <div class="page-title">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <div>
          <h2>隐私设置</h2>
          <p>管理你的数据保存与可见性偏好</p>
        </div>
      </div>

      <div v-loading="loading">

        <!-- 对话隐私 -->
        <div class="section-card">
          <div class="section-title">
            <div class="title-icon chat"><el-icon><ChatDotSquare /></el-icon></div>
            <div>
              <span>对话隐私</span>
              <p>控制你的 AI 对话记录的保存和可见性</p>
            </div>
          </div>
          <div class="toggle-list">
            <div class="toggle-item">
              <div class="toggle-info">
                <span class="lbl">保存对话历史</span>
                <span class="desc">开启后，你的对话记录将被保存</span>
              </div>
              <el-switch v-model="settings.saveChatHistory" />
            </div>
            <div class="toggle-item">
              <div class="toggle-info">
                <span class="lbl">允许管理员查看对话记录</span>
                <span class="desc">关闭后，管理员将无法查看你的对话内容</span>
              </div>
              <el-switch v-model="settings.chatVisible" />
            </div>
          </div>
        </div>

        <!-- 测试隐私 -->
        <div class="section-card">
          <div class="section-title">
            <div class="title-icon test"><el-icon><DocumentCopy /></el-icon></div>
            <div>
              <span>测试隐私</span>
              <p>控制你的心理测试记录的保存和可见性</p>
            </div>
          </div>
          <div class="toggle-list">
            <div class="toggle-item">
              <div class="toggle-info">
                <span class="lbl">保存测试记录</span>
                <span class="desc">开启后，你的测试记录将被保存</span>
              </div>
              <el-switch v-model="settings.saveTestRecords" />
            </div>
            <div class="toggle-item">
              <div class="toggle-info">
                <span class="lbl">允许查看测试趋势分析</span>
                <span class="desc">需要保存测试记录才能查看</span>
              </div>
              <el-switch v-model="settings.allowTrendAnalysis" />
            </div>
          </div>
        </div>

        <!-- 数据安全 -->
        <div class="section-card danger-card">
          <div class="section-title">
            <div class="title-icon danger"><el-icon><Lock /></el-icon></div>
            <div>
              <span>数据安全</span>
              <p>管理你的个人数据，以下操作均不可恢复</p>
            </div>
          </div>
          <div class="action-list">
            <div class="action-item">
              <div class="action-info">
                <span class="lbl">清除所有对话记录</span>
                <span class="desc">删除全部 AI 对话历史，不影响账号</span>
              </div>
              <el-button size="small" plain round @click="handleClearChat">
                <el-icon><Delete /></el-icon> 清除
              </el-button>
            </div>
            <div class="action-item">
              <div class="action-info">
                <span class="lbl">清除所有测试记录</span>
                <span class="desc">删除全部心理测试历史，不影响账号</span>
              </div>
              <el-button size="small" plain round @click="handleClearTest">
                <el-icon><Delete /></el-icon> 清除
              </el-button>
            </div>

          </div>
        </div>

        <!-- 保存 -->
        <div class="save-row">
          <el-button type="primary" round size="large" :loading="saving" @click="saveSettings">
            保存设置
          </el-button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  ChatDotSquare,
  DocumentCopy,
  Lock,
  Delete
} from '@element-plus/icons-vue'
import { getPrivacySettings, updatePrivacySettings } from '@/api/user'
import { clearChatHistory, clearTestRecords } from '@/api/user'

const router = useRouter()

// 加载状态
const loading = ref(true)
const saving = ref(false)

// 设置项
const settings = reactive({
  saveChatHistory: true,
  chatVisible: true,
  saveTestRecords: true,
  allowTrendAnalysis: true
})

// 加载隐私设置
const loadSettings = async () => {
  try {
    loading.value = true
    const res = await getPrivacySettings()
    Object.assign(settings, res.data)
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    saving.value = true
    await updatePrivacySettings(settings)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 清除对话记录
const handleClearChat = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有对话记录吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await clearChatHistory()
    ElMessage.success('清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除失败:', error)
      ElMessage.error('清除失败')
    }
  }
}

// 清除测试记录
const handleClearTest = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有测试记录吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await clearTestRecords()
    ElMessage.success('清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除失败:', error)
      ElMessage.error('清除失败')
    }
  }
}

// 返回
const goBack = () => {
  router.push('/profile')
}

// 组件挂载
onMounted(() => {
  loadSettings()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.privacy-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

// ── 页头 ──────────────────────────────────────────────
.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;

  h2 { font-size: 20px; font-weight: 700; color: $text-primary; margin: 0 0 2px; }
  p  { font-size: 12px; color: $text-secondary; margin: 0; }
}

// ── 通用卡片 ──────────────────────────────────────────
.section-card {
  background: #fff;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);
  padding: 24px 28px;
  margin-bottom: 18px;
}

// ── 区块标题 ──────────────────────────────────────────
.section-title {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid $border-lighter;

  .title-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 18px;

    &.chat   { background: linear-gradient(135deg, #ede8f5, #c4b5d8); color: #7b5ea7; }
    &.test   { background: linear-gradient(135deg, #fde8d8, #f4a57a); color: #c96f42; }
    &.danger { background: linear-gradient(135deg, #fce4ec, #f48fb1); color: #c2185b; }
  }

  > div:last-child {
    span {
      display: block;
      font-size: 15px;
      font-weight: 700;
      color: $text-primary;
      margin-bottom: 2px;
    }
    p {
      font-size: 12px;
      color: $text-secondary;
      margin: 0;
    }
  }
}

// ── 开关列表 ──────────────────────────────────────────
.toggle-list { display: flex; flex-direction: column; }

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid $bg-page;

  &:last-child { border-bottom: none; padding-bottom: 0; }

  .toggle-info {
    flex: 1;

    .lbl {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: $text-primary;
      margin-bottom: 3px;
    }

    .desc {
      display: block;
      font-size: 12px;
      color: $text-secondary;
      line-height: 1.4;
    }
  }
}

// ── 数据安全卡片 ──────────────────────────────────────
.danger-card {
  border-color: rgba(245,108,108,0.2);
  background: rgba(255,248,248,0.7);
}

.action-list { display: flex; flex-direction: column; }

.action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(245,108,108,0.1);

  &:last-child { border-bottom: none; padding-bottom: 0; }

  .action-info {
    flex: 1;

    .lbl {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: $text-primary;
      margin-bottom: 3px;

      &.danger-lbl { color: #e53935; }
    }

    .desc {
      display: block;
      font-size: 12px;
      color: $text-secondary;
    }
  }
}

// ── 保存按钮 ──────────────────────────────────────────
.save-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}
</style>
