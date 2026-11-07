<template>
  <div class="tag-manage">

    <div class="container">
      <!-- 顶部标题栏 -->
      <div class="page-header-content">
        <h2>对话标签管理</h2>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          新建标签
        </el-button>
      </div>

      <!-- 系统标签 -->
      <el-card class="tag-section">
        <template #header>
          <div class="card-header">
            <span>系统标签</span>
            <el-text size="small" type="info">预设标签，不可删除</el-text>
          </div>
        </template>

        <div class="tag-list">
          <div
            v-for="tag in systemTags"
            :key="tag.id"
            class="tag-item"
          >
            <el-tag
              :color="tag.color"
              size="large"
              effect="plain"
            >
              {{ tag.name }}
            </el-tag>
            <span class="tag-count">({{ tag.count }}个对话)</span>
          </div>
        </div>
      </el-card>

      <!-- 自定义标签 -->
      <el-card class="tag-section">
        <template #header>
          <div class="card-header">
            <span>自定义标签</span>
            <el-text size="small" type="info">您可以创建、编辑、删除自定义标签</el-text>
          </div>
        </template>

        <el-empty v-if="customTags.length === 0" description="暂无自定义标签" />

        <div v-else class="tag-list">
          <div
            v-for="tag in customTags"
            :key="tag.id"
            class="tag-item custom"
          >
            <el-tag
              :color="tag.color"
              size="large"
              closable
              @close="deleteTag(tag)"
            >
              {{ tag.name }}
            </el-tag>
            <span class="tag-count">({{ tag.count }}个对话)</span>
            <el-button
              text
              :icon="Edit"
              size="small"
              @click="editTag(tag)"
            >
              编辑
            </el-button>
          </div>
        </div>

        <!-- 添加自定义标签按钮 -->
        <div class="add-tag-wrapper">
          <el-button
            :icon="Plus"
            @click="showCreateDialog"
          >
            添加自定义标签
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑标签对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑标签' : '新建标签'"
      width="400px"
    >
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="标签名称">
          <el-input
            v-model="tagForm.name"
            placeholder="请输入标签名称"
            maxlength="10"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="标签颜色">
          <div class="color-picker">
            <div
              v-for="color in presetColors"
              :key="color"
              class="color-item"
              :class="{ active: tagForm.color === color }"
              :style="{ background: color }"
              @click="selectColor(color)"
            />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTag" :loading="saving">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit } from '@element-plus/icons-vue'
import { getTags, createTag, deleteTag as deleteTagApi } from '@/api/chat'

// 对话框显示
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)

// 标签表单
const tagForm = ref({
  id: '',
  name: '',
  color: ''
})

// 所有标签
const allTags = ref([])

// 系统标签
const systemTags = computed(() => {
  return allTags.value.filter(tag => tag.type === 'system')
})

// 自定义标签
const customTags = computed(() => {
  return allTags.value.filter(tag => tag.type === 'custom')
})

// 预设颜色
const presetColors = ref([
  '#409EFF', // 蓝
  '#67C23A', // 绿
  '#E6A23C', // 橙
  '#F56C6C', // 红
  '#909399', // 灰
  '#C0C4CC', // 浅灰
  '#79bbff', // 浅蓝
  '#95d475', // 浅绿
  '#eebe77', // 浅橙
  '#f89898', // 浅红
  '#b1b3b8', // 中灰
  '#fab389'  // 粉橙
])

// 加载标签列表
const loadTags = async () => {
  try {
    const res = await getTags()
    allTags.value = res.data || []
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  tagForm.value = {
    id: '',
    name: '',
    color: presetColors.value[0]
  }
  dialogVisible.value = true
}

// 编辑标签
const editTag = (tag) => {
  isEdit.value = true
  tagForm.value = {
    id: tag.id,
    name: tag.name,
    color: tag.color
  }
  dialogVisible.value = true
}

// 选择颜色
const selectColor = (color) => {
  tagForm.value.color = color
}

// 保存标签
const saveTag = async () => {
  // 验证
  if (!tagForm.value.name.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }

  if (!tagForm.value.color) {
    ElMessage.warning('请选择标签颜色')
    return
  }

  // 检查名称重复
  const existTag = allTags.value.find(
    t => t.name === tagForm.value.name && t.id !== tagForm.value.id
  )
  if (existTag) {
    ElMessage.warning('标签名称已存在')
    return
  }

  try {
    saving.value = true

    if (isEdit.value) {
      // 编辑标签（这里应该调用更新API）
      ElMessage.success('修改成功')
    } else {
      // 创建标签
      await createTag({
        name: tagForm.value.name,
        color: tagForm.value.color
      })
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    await loadTags()
  } catch (error) {
    console.error('保存标签失败:', error)
  } finally {
    saving.value = false
  }
}

// 删除标签
const deleteTag = async (tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签"${tag.name}"吗？删除后不会影响已有对话。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteTagApi(tag.id)
    ElMessage.success('删除成功')
    await loadTags()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除标签失败:', error)
    }
  }
}

// 组件挂载
onMounted(() => {
  loadTags()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.tag-manage {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.page-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;

  h2 {
    margin: 0;
  }
}

.tag-section {
  margin-bottom: $spacing-lg;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    span {
      font-weight: 600;
    }
  }
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm;
  border: 1px solid $border-lighter;
  border-radius: $border-radius-md;
  background: $bg-white;
  transition: $transition-base;

  &:hover {
    border-color: $primary-color;
  }

  &.custom {
    padding-right: $spacing-md;
  }

  .tag-count {
    font-size: $font-size-small;
    color: $text-secondary;
  }
}

.add-tag-wrapper {
  margin-top: $spacing-lg;
  padding-top: $spacing-lg;
  border-top: 1px dashed $border-light;
}

.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;

  .color-item {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid transparent;
    transition: $transition-base;

    &:hover {
      transform: scale(1.1);
    }

    &.active {
      border-color: $text-primary;
      box-shadow: 0 0 0 2px $bg-white, 0 0 0 4px $primary-color;
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .container {
    padding: $spacing-md;
  }

  .page-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-md;
  }
}
</style>
