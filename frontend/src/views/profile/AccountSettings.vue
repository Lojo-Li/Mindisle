<template>
  <div class="account-settings-page">
    <div class="container">

      <div class="page-title">
        <el-button :icon="ArrowLeft" text @click="router.back()">返回</el-button>
        <div>
          <h2>账号设置</h2>
          <p>管理你的账号安全与绑定信息</p>
        </div>
      </div>

      <!-- 账号信息 -->
      <div class="section-card">
        <div class="section-title">
          <el-icon><User /></el-icon> 账号信息
        </div>
        <div class="info-row">
          <span class="label">注册邮箱</span>
          <span class="value">{{ userInfo?.email }}</span>
        </div>
        <div class="info-row">
          <span class="label">注册时间</span>
          <span class="value">{{ formatDate(userInfo?.created_at) }}</span>
        </div>
        <div class="info-row">
          <span class="label">账号角色</span>
          <el-tag :type="roleType" size="small" round>{{ roleText }}</el-tag>
        </div>
        <div class="info-row">
          <span class="label">最后登录</span>
          <span class="value">{{ formatDate(userInfo?.last_login_at) || '未记录' }}</span>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="section-card">
        <div class="section-title">
          <el-icon><Lock /></el-icon> 修改密码
        </div>

        <el-form
          ref="pwdFormRef"
          :model="pwdForm"
          :rules="pwdRules"
          label-width="90px"
          class="pwd-form"
        >
          <el-form-item label="旧密码" prop="old_password">
            <el-input
              v-model="pwdForm.old_password"
              type="password"
              placeholder="请输入当前密码"
              show-password
              autocomplete="current-password"
            />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="pwdForm.new_password"
              type="password"
              placeholder="至少6位，包含字母和数字"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input
              v-model="pwdForm.confirm_password"
              type="password"
              placeholder="再次输入新密码"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" round :loading="pwdLoading" @click="submitPwd">
              确认修改
            </el-button>
            <el-button round @click="resetPwdForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 危险操作 -->
      <div class="section-card danger-zone">
        <div class="section-title danger">
          <el-icon><Warning /></el-icon> 危险操作
        </div>
        <div class="danger-item">
          <div>
            <p class="danger-label">注销账户</p>
            <p class="danger-desc">永久删除你的账号及所有数据，此操作不可恢复</p>
          </div>
          <el-button type="danger" plain round size="small" @click="handleDeleteAccount">注销账户</el-button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, User, Lock, Warning } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { changePassword, deleteAccount } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const roleType = computed(() => {
  const r = userInfo.value?.role
  if (r === 'admin') return 'danger'
  if (r === 'counselor') return 'warning'
  return ''
})
const roleText = computed(() => {
  const r = userInfo.value?.role
  if (r === 'admin') return '管理员'
  if (r === 'counselor') return '咨询师'
  return '普通用户'
})

const formatDate = (str) => {
  if (!str) return ''
  const d = new Date(str)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// ── 修改密码 ──────────────────────────────────────────
const pwdFormRef = ref()
const pwdLoading = ref(false)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })

const validateConfirm = (rule, value, callback) => {
  if (value !== pwdForm.value.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const submitPwd = async () => {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    pwdLoading.value = true
    await changePassword({
      old_password: pwdForm.value.old_password,
      new_password: pwdForm.value.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
    setTimeout(() => {
      userStore.logout()
    }, 1500)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '修改失败，请检查旧密码是否正确')
  } finally {
    pwdLoading.value = false
  }
}

const resetPwdForm = () => {
  pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  pwdFormRef.value?.clearValidate()
}

// ── 注销账户 ──────────────────────────────────────────
const handleDeleteAccount = async () => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除你的账号及所有数据，确定要继续吗？',
      '注销账户',
      { confirmButtonText: '确定注销', cancelButtonText: '取消', type: 'error', confirmButtonClass: 'el-button--danger' }
    )
    await deleteAccount()
    userStore.setToken('')
    userStore.setUserInfo(null)
    ElMessage.success('账户已注销')
    setTimeout(() => { window.location.href = '/' }, 1200)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败，请稍后重试')
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.account-settings-page {
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

  h2 {
    font-size: 20px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 2px;
  }

  p {
    font-size: 12px;
    color: $text-secondary;
    margin: 0;
  }
}

// ── 通用卡片 ──────────────────────────────────────────
.section-card {
  background: #fff;
  border-radius: 20px;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06);
  padding: 24px 28px;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid $border-lighter;

  &.danger { color: #f56c6c; }
}

// ── 账号信息行 ────────────────────────────────────────
.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid $bg-page;

  &:last-child { border-bottom: none; }

  .label {
    font-size: 13px;
    color: $text-secondary;
    min-width: 80px;
  }

  .value {
    font-size: 14px;
    color: $text-primary;
    font-weight: 500;
  }
}

// ── 修改密码表单 ──────────────────────────────────────
.pwd-form {
  max-width: 420px;

  :deep(.el-input__wrapper) { border-radius: 10px !important; }
  :deep(.el-form-item__label) { font-size: 13px; color: $text-regular; }
}

// ── 危险区域 ──────────────────────────────────────────
.danger-zone {
  border-color: rgba(245, 108, 108, 0.25);
  background: rgba(255, 245, 245, 0.6);
}

.danger-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;

  .danger-label {
    font-size: 14px;
    font-weight: 600;
    color: #e63232;
    margin: 0 0 4px;
  }

  .danger-desc {
    font-size: 12px;
    color: $text-secondary;
    margin: 0;
  }
}
</style>
