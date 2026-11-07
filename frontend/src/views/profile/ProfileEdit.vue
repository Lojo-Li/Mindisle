<template>
  <div class="profile-edit">

    <div class="container">
      <!-- 顶部导航 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>编辑个人资料</h2>
      </div>

      <!-- 编辑表单 -->
      <el-card v-loading="loading" class="form-card">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="profile-form"
        >
          <!-- 头像 -->
          <el-form-item label="头像">
            <div class="avatar-upload">
              <el-avatar :size="100" :src="form.avatar || previewUrl">
                <el-icon :size="50"><User /></el-icon>
              </el-avatar>
              <el-upload
                class="avatar-uploader"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarChange"
                accept="image/*"
              >
                <el-button type="primary" :icon="Camera">更换头像</el-button>
              </el-upload>
              <div class="upload-tip">支持 JPG、PNG 格式，大小不超过 2MB</div>
            </div>
          </el-form-item>

          <!-- 昵称 -->
          <el-form-item label="昵称" prop="nickname">
            <el-input
              v-model="form.nickname"
              placeholder="请输入昵称（2-20个字符）"
              maxlength="20"
              show-word-limit
            />
          </el-form-item>

          <!-- 邮箱 -->
          <el-form-item label="邮箱">
            <el-input v-model="form.email" disabled />
            <div class="form-tip">邮箱不可修改</div>
          </el-form-item>

          <!-- 手机号 -->
          <el-form-item label="手机号" prop="phone">
            <el-input
              v-model="form.phone"
              placeholder="请输入手机号（选填）"
              maxlength="11"
            />
          </el-form-item>

          <!-- 出生日期 -->
          <el-form-item label="出生日期" prop="birthDate">
            <el-date-picker
              v-model="form.birthDate"
              type="date"
              placeholder="选择日期"
              :disabled-date="disabledDate"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>

          <!-- 性别 -->
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio label="male">男</el-radio>
              <el-radio label="female">女</el-radio>
              <el-radio label="secret">保密</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 个人简介 -->
          <el-form-item label="个人简介">
            <el-input
              v-model="form.bio"
              type="textarea"
              :rows="4"
              placeholder="介绍一下自己吧（最多200字）"
              maxlength="200"
              show-word-limit
              resize="none"
            />
          </el-form-item>

          <!-- 操作按钮 -->
          <el-form-item>
            <el-button @click="goBack">取消</el-button>
            <el-button type="primary" :loading="saving" @click="handleSubmit">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Camera, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUserProfile, updateUserProfile, uploadAvatar } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)

// 加载状态
const loading = ref(true)
const saving = ref(false)

// 预览URL
const previewUrl = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')

// 表单数据
const form = reactive({
  avatar: '',
  nickname: '',
  email: '',
  phone: '',
  birthDate: '',
  gender: 'secret',
  bio: ''
})

// 头像文件
const avatarFile = ref(null)

// 表单校验规则
const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度应为2-20个字符', trigger: 'blur' }
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号',
      trigger: 'blur'
    }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ]
}

// 禁用未来日期
const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

// 加载用户信息
const loadProfile = async () => {
  try {
    loading.value = true
    const res = await getUserProfile()
    const data = res.data

    // 填充表单
    Object.keys(form).forEach(key => {
      if (data[key] !== undefined) {
        form[key] = data[key]
      }
    })

    if (data.avatar) {
      previewUrl.value = data.avatar
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
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
  const newPreviewUrl = URL.createObjectURL(file.raw)
  previewUrl.value = newPreviewUrl
  // 同时更新 form.avatar，确保显示新选择的图片
  form.avatar = newPreviewUrl
  return false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    // 表单校验
    await formRef.value.validate()

    saving.value = true

    // 如果有新头像，先上传
    if (avatarFile.value) {
      const avatarRes = await uploadAvatar(avatarFile.value)
      // 更新预览URL为服务器返回的URL
      if (avatarRes.data?.avatar) {
        previewUrl.value = avatarRes.data.avatar
      }
    }

    // 更新用户信息
    const updateData = {
      nickname: form.nickname,
      phone: form.phone || undefined,
      birthDate: form.birthDate || undefined,
      gender: form.gender,
      bio: form.bio || undefined
    }

    await updateUserProfile(updateData)

    // 重新获取用户信息，确保显示最新数据
    await loadProfile()

    // 更新 store 中的用户信息
    userStore.setUserInfo({
      ...userStore.userInfo,
      ...updateData,
      avatar: previewUrl.value
    })

    ElMessage.success('保存成功')

    // 清空头像文件
    avatarFile.value = null

    goBack()
  } catch (error) {
    console.error('保存失败:', error)
    if (error !== false) {
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/profile')
}

// 组件挂载
onMounted(() => {
  loadProfile()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.profile-edit-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 24px 24px 60px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;

  h2 { margin: 0; font-size: 24px; font-weight: 700; color: $text-primary; }
}

.edit-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  :deep(.el-card__body) { padding: 36px 40px; }
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
  gap: 12px;
}

.avatar-tip { font-size: 13px; color: $text-secondary; }

.form-section-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  margin: 28px 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid $border-lighter;

  &:first-of-type { margin-top: 0; }
}

.action-row {
  display: flex;
  gap: 12px;
  margin-top: 28px;
  justify-content: flex-end;
}

.tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
</style>
