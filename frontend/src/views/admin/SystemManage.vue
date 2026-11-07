<template>
  <div class="system-manage">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <el-tabs v-model="activeTab" class="system-tabs">
      <el-tab-pane label="基本设置" name="basic">
        <el-card>
          <el-form :model="basicForm" label-width="150px">
            <el-form-item label="网站名称">
              <el-input v-model="basicForm.siteName" />
            </el-form-item>
            <el-form-item label="网站副标题">
              <el-input v-model="basicForm.siteSubtitle" />
            </el-form-item>
            <el-form-item label="联系邮箱">
              <el-input v-model="basicForm.contactEmail" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="basicForm.contactPhone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveBasic">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="管理员管理" name="admin">
        <el-card>
          <div class="admin-actions">
            <el-button type="primary" @click="handleAddAdmin">
              <el-icon><Plus /></el-icon>
              添加管理员
            </el-button>
          </div>
          <el-table :data="adminList" style="width: 100%; margin-top: 20px">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="createTime" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" text size="small" @click="handleEditAdmin(row)">编辑</el-button>
                <el-button type="danger" text size="small" @click="handleDeleteAdmin(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <el-table :data="logList" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="action" label="操作" />
            <el-table-column prop="operator" label="操作人" width="120" />
            <el-table-column prop="createTime" label="时间" width="180" />
            <el-table-column prop="ip" label="IP地址" width="150" />
          </el-table>
          <el-pagination
            v-model:current-page="logPagination.page"
            v-model:page-size="logPagination.pageSize"
            :total="logPagination.total"
            layout="total, prev, pager, next"
            style="margin-top: 20px"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('basic')

const basicForm = ref({
  siteName: '心理咨询平台',
  siteSubtitle: '心灵驿站，守护您的心理健康',
  contactEmail: 'contact@example.com',
  contactPhone: '400-123-4567'
})

const adminList = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    createTime: '2026-01-01 10:00:00'
  }
])

const logList = ref([
  {
    id: 1,
    action: '管理员登录',
    operator: 'admin',
    createTime: '2026-04-04 10:00:00',
    ip: '192.168.1.100'
  }
])

const logPagination = ref({
  page: 1,
  pageSize: 20,
  total: 1
})

const handleSaveBasic = () => {
  ElMessage.success('保存成功')
}

const handleAddAdmin = () => {
  ElMessage.info('添加管理员功能开发中...')
}

const handleEditAdmin = (row) => {
  ElMessage.info('编辑管理员功能开发中...')
}

const handleDeleteAdmin = (row) => {
  ElMessage.info('删除管理员功能开发中...')
}
</script>

<style scoped>
.system-manage {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.system-tabs {
  flex: 1;
}

.admin-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
