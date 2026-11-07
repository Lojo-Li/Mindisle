<template>
  <div class="article-editor">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <h2>{{ isEdit ? '编辑文章' : '新建文章' }}</h2>
      <div class="header-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveArticle">保存</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="文章标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="文章分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 200px">
            <el-option label="焦虑抑郁" value="anxiety" />
            <el-option label="人际关系" value="relationship" />
            <el-option label="职业发展" value="career" />
            <el-option label="家庭婚姻" value="family" />
            <el-option label="个人成长" value="growth" />
          </el-select>
        </el-form-item>

        <el-form-item label="封面图片">
          <el-upload
            class="cover-uploader"
            :show-file-list="false"
            :before-upload="handleUploadCover"
            accept="image/*"
          >
            <img v-if="form.cover" :src="form.cover" class="cover-image" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="cover-tip">建议尺寸：800x450，支持 jpg、png 格式</div>
        </el-form-item>

        <el-form-item label="文章摘要">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文章摘要（选填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="文章内容" prop="content">
          <div class="editor-container">
            <div class="editor-toolbar">
              <el-button-group>
                <el-button size="small" @click="insertFormat('bold')"><b>B</b></el-button>
                <el-button size="small" @click="insertFormat('italic')"><i>I</i></el-button>
                <el-button size="small" @click="insertFormat('underline')"><u>U</u></el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertFormat('h2')">H2</el-button>
                <el-button size="small" @click="insertFormat('h3')">H3</el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertList('ul')">• 列表</el-button>
                <el-button size="small" @click="insertList('ol')">1. 列表</el-button>
              </el-button-group>
              <el-upload
                :show-file-list="false"
                :before-upload="handleUploadImage"
                accept="image/*"
                style="margin-left: 10px"
              >
                <el-button size="small">插入图片</el-button>
              </el-upload>
            </div>
            <el-input
              ref="editorRef"
              v-model="form.content"
              type="textarea"
              :rows="20"
              placeholder="支持 Markdown 格式，也可以使用上方工具栏插入格式..."
            />
          </div>
        </el-form-item>

        <el-form-item label="发布设置">
          <el-checkbox v-model="form.published">立即发布</el-checkbox>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { saveKnowledgeArticle } from '@/api/admin'
import { getKnowledgeDetail } from '@/api/knowledge'
import { uploadFile } from '@/api/consultation'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const editorRef = ref(null)

const isEdit = !!route.params.id
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  title: '',
  category: '',
  cover: '',
  summary: '',
  content: '',
  published: true
})

const rules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择文章分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const loadArticle = async () => {
  if (!isEdit) return
  try {
    loading.value = true
    const res = await getKnowledgeDetail(route.params.id)
    const data = res.data
    form.title = data.title || ''
    form.category = data.category || ''
    form.cover = data.cover_image || ''
    form.summary = data.summary || ''
    form.content = data.content || ''
    form.published = data.status === 'published'
  } finally {
    loading.value = false
  }
}

const handleUploadCover = async (file) => {
  try {
    const res = await uploadFile(file)
    form.cover = res.data.url
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
  return false
}

const handleUploadImage = async (file) => {
  try {
    const res = await uploadFile(file)
    const markdown = `![图片](${res.data.url})`
    insertText(markdown)
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
  return false
}

const insertFormat = (type) => {
  const formats = {
    bold: '**粗体**',
    italic: '*斜体*',
    underline: '~~下划线~~',
    h2: '## 标题2',
    h3: '### 标题3'
  }
  insertText(formats[type] || '')
}

const insertList = (type) => {
  const text = type === 'ul' ? '- 列表项' : '1. 列表项'
  insertText(text)
}

const insertText = (text) => {
  const textarea = editorRef.value?.textarea || editorRef.value?.$el?.querySelector('textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = form.content

  form.content = value.substring(0, start) + text + value.substring(end)

  setTimeout(() => {
    textarea.focus()
    textarea.selectionStart = textarea.selectionEnd = start + text.length
  }, 0)
}

const saveArticle = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    saving.value = true
    await saveKnowledgeArticle({
      id: isEdit ? Number(route.params.id) : null,
      title: form.title,
      category: form.category,
      cover_image: form.cover,
      summary: form.summary,
      content: form.content,
      status: form.published ? 'published' : 'draft'
    })
    ElMessage.success(isEdit ? '更新成功' : '创建成功')
    goBack()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/admin/knowledge')
}

onMounted(() => loadArticle())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.article-editor { padding: $spacing-lg; }
.page-header { display: flex; align-items: center; gap: $spacing-lg; margin-bottom: $spacing-lg; }
.page-header h2 { flex: 1; margin: 0; }
.header-actions { display: flex; gap: $spacing-sm; }

.cover-uploader { display: inline-block; }
.cover-image { width: 300px; height: 170px; object-fit: cover; border-radius: $border-radius; }
.cover-uploader-icon { width: 300px; height: 170px; border: 1px dashed $border-color; border-radius: $border-radius; display: flex; align-items: center; justify-content: center; font-size: 28px; color: $text-secondary; cursor: pointer; }
.cover-uploader-icon:hover { border-color: $primary-color; color: $primary-color; }
.cover-tip { font-size: 12px; color: $text-secondary; margin-top: $spacing-sm; }

.editor-container { width: 100%; }
.editor-toolbar { display: flex; align-items: center; padding: $spacing-sm; background: #f5f7fa; border: 1px solid $border-color; border-bottom: none; border-radius: $border-radius $border-radius 0 0; }
:deep(.el-textarea__inner) { border-radius: 0 0 $border-radius $border-radius; }
</style>
