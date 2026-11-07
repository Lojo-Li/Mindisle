<template>
  <div class="profile-page">

    <div class="container">

      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-wrap" @click="editAvatar">
            <el-avatar :size="88" :src="userInfo?.avatar">
              <el-icon :size="44"><User /></el-icon>
            </el-avatar>
            <div class="avatar-mask"><el-icon><Camera /></el-icon></div>
          </div>

          <div class="user-info">
            <h2>{{ userInfo?.nickname || '未设置昵称' }}</h2>
            <p class="email">{{ userInfo?.email }}</p>
            <el-tag :type="userRoleType" size="small" round>{{ userRoleText }}</el-tag>
          </div>

          <el-button class="edit-btn" :icon="Edit" round @click="goToEdit">编辑资料</el-button>
        </div>

        <!-- 数据统计行 -->
        <div class="stats-row">
          <div class="stat-cell" @click="navigateTo('/test')">
            <el-icon :size="20" color="#e8845a"><DocumentCopy /></el-icon>
            <span class="num">{{ statistics.test_count || 0 }}</span>
            <span class="lbl">心理测试</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-cell" @click="navigateTo('/chat')">
            <el-icon :size="20" color="#9b8bb4"><ChatDotSquare /></el-icon>
            <span class="num">{{ statistics.chat_count || 0 }}</span>
            <span class="lbl">智能问答</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-cell" @click="navigateTo('/counselor/orders')">
            <el-icon :size="20" color="#56ab91"><Calendar /></el-icon>
            <span class="num">{{ statistics.appointment_count || 0 }}</span>
            <span class="lbl">咨询预约</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-cell" @click="navigateTo('/knowledge')">
            <el-icon :size="20" color="#f4a57a"><Star /></el-icon>
            <span class="num">{{ statistics.favorite_count || 0 }}</span>
            <span class="lbl">收藏内容</span>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="section-card">
        <div class="section-title">快捷入口</div>
        <div class="quick-grid">
          <div class="quick-item" @click="router.push('/test?tab=history')">
            <div class="quick-icon" style="background:linear-gradient(135deg,#fde8d8,#f4a57a)">
              <el-icon :size="26" color="#c96f42"><DocumentCopy /></el-icon>
            </div>
            <span>我的测试</span>
          </div>
          <div class="quick-item" @click="navigateTo('/chat')">
            <div class="quick-icon" style="background:linear-gradient(135deg,#ede8f5,#c4b5d8)">
              <el-icon :size="26" color="#7b5ea7"><ChatDotSquare /></el-icon>
            </div>
            <span>我的对话</span>
          </div>
          <div class="quick-item" @click="navigateTo('/counselor/orders')">
            <div class="quick-icon" style="background:linear-gradient(135deg,#e0f5ee,#a8e6cf)">
              <el-icon :size="26" color="#3d8a6e"><Calendar /></el-icon>
            </div>
            <span>我的预约</span>
          </div>
          <div class="quick-item" @click="navigateTo('/profile/favorites')">
            <div class="quick-icon" style="background:linear-gradient(135deg,#fff9e6,#ffe082)">
              <el-icon :size="26" color="#c68a00"><Star /></el-icon>
            </div>
            <span>我的收藏</span>
          </div>
          <div class="quick-item" @click="navigateTo('/profile/account')">
            <div class="quick-icon" style="background:linear-gradient(135deg,#fff3e0,#ffcc80)">
              <el-icon :size="26" color="#e65100"><Setting /></el-icon>
            </div>
            <span>账号设置</span>
          </div>
          <div class="quick-item" @click="goToPrivacy">
            <div class="quick-icon" style="background:linear-gradient(135deg,#fce4ec,#f48fb1)">
              <el-icon :size="26" color="#c2185b"><Lock /></el-icon>
            </div>
            <span>隐私设置</span>
          </div>
          <div class="quick-item" @click="goToStatistics">
            <div class="quick-icon" style="background:linear-gradient(135deg,#e8eaf6,#9fa8da)">
              <el-icon :size="26" color="#3949ab"><DataAnalysis /></el-icon>
            </div>
            <span>数据统计</span>
          </div>
          <div class="quick-item" @click="goToCounselorApply" v-if="!isCounselor">
            <div class="quick-icon" style="background:linear-gradient(135deg,#e8f5e9,#a5d6a7)">
              <el-icon :size="26" color="#2e7d32"><Briefcase /></el-icon>
            </div>
            <span>加入我们</span>
          </div>
          <div class="quick-item" @click="goToCounselorDashboard" v-else>
            <div class="quick-icon" style="background:linear-gradient(135deg,#fff8e1,#ffca28)">
              <el-icon :size="26" color="#f57f17"><Briefcase /></el-icon>
            </div>
            <span>咨询师中心</span>
          </div>
          <div class="quick-item" @click="handleLogout">
            <div class="quick-icon" style="background:linear-gradient(135deg,#f5f5f5,#eeeeee)">
              <el-icon :size="26" color="#9e9e9e"><SwitchButton /></el-icon>
            </div>
            <span>退出登录</span>
          </div>
          <div class="quick-item" @click="handleDeleteAccount">
            <div class="quick-icon" style="background:linear-gradient(135deg,#fde8e8,#ffcdd2)">
              <el-icon :size="26" color="#e53935"><Delete /></el-icon>
            </div>
            <span>注销账户</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="avatarDialogVisible"
      title="更换头像"
      width="400px"
      @closed="handleDialogClosed"
    >
      <el-upload
        class="avatar-uploader"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleAvatarChange"
        accept="image/*"
      >
        <img v-if="avatarPreview" :src="avatarPreview" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>

      <template #footer>
        <el-button @click="avatarDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadAvatar" :loading="uploading">
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Camera,
  Edit,
  DocumentCopy,
  ChatDotSquare,
  Calendar,
  Star,
  Setting,
  Lock,
  DataAnalysis,
  SwitchButton,
  Plus,
  Delete,
  Briefcase
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUserProfile, uploadAvatar as uploadAvatarApi, getUserStatistics, deleteAccount } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 用户角色
const userRoleType = computed(() => {
  const role = userInfo.value?.role
  if (role === 'admin') return 'danger'
  if (role === 'counselor') return 'warning'
  return ''
})

const userRoleText = computed(() => {
  const role = userInfo.value?.role
  if (role === 'admin') return '管理员'
  if (role === 'counselor') return '咨询师'
  return '普通用户'
})

// 是否是咨询师
const isCounselor = computed(() => {
  return userInfo.value?.role === 'counselor'
})

// 统计数据
const statistics = ref({
  testCount: 0,
  chatCount: 0,
  appointmentCount: 0,
  favoriteCount: 0
})

// 头像对话框
const avatarDialogVisible = ref(false)
const avatarPreview = ref('')
const avatarFile = ref(null)
const uploading = ref(false)

// 加载用户信息
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile()
    userStore.setUserInfo(res.data)
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const res = await getUserStatistics()
    statistics.value = res.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 编辑头像
const editAvatar = () => {
  // 重置状态
  avatarFile.value = null
  // 显示当前头像或预览
  if (userInfo.value?.avatar) {
    avatarPreview.value = userInfo.value.avatar
  } else {
    avatarPreview.value = ''
  }
  avatarDialogVisible.value = true
}

// 对话框关闭时的处理
const handleDialogClosed = () => {
  avatarFile.value = null
  avatarPreview.value = ''
}

// 头像文件选择
const handleAvatarChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  const isLt2M = file.raw.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }

  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }

  avatarFile.value = file.raw
  avatarPreview.value = URL.createObjectURL(file.raw)
  return false
}

// 上传头像
const uploadAvatar = async () => {
  if (!avatarFile.value) {
    ElMessage.warning('请选择头像')
    return
  }

  try {
    uploading.value = true
    const res = await uploadAvatarApi(avatarFile.value)

    // 重新获取用户信息，确保显示最新的头像
    await loadUserProfile()

    ElMessage.success('头像更新成功')
    avatarDialogVisible.value = false
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
    avatarFile.value = null
  }
}

// 导航到指定路径
const navigateTo = (path) => {
  router.push(path)
}

// 跳转到编辑资料
const goToEdit = () => {
  router.push('/profile/edit')
}

// 跳转到隐私设置
const goToPrivacy = () => {
  router.push('/profile/privacy')
}

// 跳转到数据统计
const goToStatistics = () => {
  router.push('/profile/statistics')
}

// 跳转到咨询师申请
const goToCounselorApply = () => {
  router.push('/counselor/apply')
}

// 跳转到咨询师中心
const goToCounselorDashboard = () => {
  router.push('/counselor/dashboard')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await userStore.logout()
  } catch {
    // 取消退出
  }
}

// 注销账户
const handleDeleteAccount = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要注销账户吗？注销后将无法恢复。',
      '注销账户',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用注销账户API
    await deleteAccount()

    // 清除用户状态
    userStore.setToken('')
    userStore.setUserInfo(null)

    ElMessage.success('账户已注销，感谢您的使用')

    // 跳转到首页
    setTimeout(() => {
      window.location.href = '/'
    }, 1000)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('注销账户失败:', error)
      ElMessage.error('注销账户失败，请稍后重试')
    }
  }
}

// 组件挂载
onMounted(() => {
  loadUserProfile()
  loadStatistics()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.profile-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 860px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

// ── 个人信息卡片 ──────────────────────────────────────
.profile-card {
  background: linear-gradient(150deg, #fde8d8 0%, #f9d4c0 50%, #fff 100%);
  border-radius: 24px;
  border: 1px solid rgba(232,132,90,0.18);
  box-shadow: 0 4px 24px rgba(107,82,68,0.1);
  padding: 32px 36px 0;
  margin-bottom: 24px;
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 28px;

  .avatar-wrap {
    position: relative;
    cursor: pointer;
    flex-shrink: 0;

    &:hover .avatar-mask { opacity: 1; }
  }

  .avatar-mask {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba(0,0,0,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 20px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .user-info {
    flex: 1;
    min-width: 0;

    h2 {
      font-size: 22px;
      font-weight: 700;
      color: $text-primary;
      margin: 0 0 4px;
    }

    .email {
      font-size: 13px;
      color: $text-secondary;
      margin: 0 0 10px;
    }
  }

  .edit-btn {
    flex-shrink: 0;
    background: rgba(232,132,90,0.12);
    border-color: rgba(232,132,90,0.3);
    color: $primary-color;

    &:hover {
      background: $primary-color;
      border-color: $primary-color;
      color: #fff;
    }
  }
}

// 数据统计行
.stats-row {
  display: flex;
  border-top: 1px solid rgba(232,132,90,0.15);

  .stat-cell {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 18px 8px;
    cursor: pointer;
    transition: background 0.2s;
    border-radius: 0 0 4px 4px;

    &:hover { background: rgba(232,132,90,0.08); }

    .num {
      font-size: 20px;
      font-weight: 700;
      color: $text-primary;
      line-height: 1;
    }

    .lbl {
      font-size: 12px;
      color: $text-secondary;
    }
  }

  .stat-divider {
    width: 1px;
    background: rgba(232,132,90,0.15);
    margin: 12px 0;
  }
}

// ── 快捷入口 ──────────────────────────────────────────
.section-card {
  background: #fff;
  border-radius: 24px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);
  padding: 24px 28px 28px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid $border-lighter;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 14px 8px;
  border-radius: 16px;
  transition: background 0.2s, transform 0.2s;

  &:hover {
    background: $bg-page;
    transform: translateY(-3px);
  }

  .quick-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }

  span {
    font-size: 12px;
    color: $text-regular;
    font-weight: 500;
    text-align: center;
  }
}

// ── 响应式 ──────────────────────────────────────────
@media (max-width: $breakpoint-md) {
  .profile-header { flex-wrap: wrap; justify-content: center; text-align: center; }
  .quick-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: $breakpoint-sm) {
  .profile-card { padding: 24px 20px 0; }
  .quick-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>

