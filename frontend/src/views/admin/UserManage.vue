<template>
  <div class="user-manage">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名、手机号或邮箱"
        style="width: 280px"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="users" stripe border style="width: 100%">
        <el-table-column prop="avatar" label="头像" width="70" align="center">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar" />
          </template>
        </el-table-column>
        <el-table-column label="用户信息" min-width="180">
          <template #default="{ row }">
            <div class="user-info">
              <span class="user-name">{{ row.nickname || '—' }}</span>
              <span class="user-email">{{ row.email }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" align="center">
          <template #default="{ row }">
            <span>{{ row.phone || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.role === 'admin' ? 'danger' : row.role === 'counselor' ? 'success' : 'primary'"
            >{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.banned ? 'danger' : 'success'">
              {{ row.banned ? '已封禁' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数据统计" width="150" align="center">
          <template #default="{ row }">
            <div class="stats">
              <span>测试 <b>{{ row.testCount }}</b></span>
              <span>对话 <b>{{ row.chatCount }}</b></span>
              <span>预约 <b>{{ row.appointmentCount }}</b></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginTime" label="最后登录" width="165" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ row.lastLoginTime || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="注册时间" width="165" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ row.createdAt }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120" align="center">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button class="btn-detail" size="small" @click="viewDetail(row)">详情</el-button>
              <el-button
                class="btn-ban"
                :class="row.banned ? 'btn-success' : 'btn-danger'"
                size="small"
                @click="toggleBan(row)"
              >{{ row.banned ? '解封' : '封禁' }}</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailVisible" title="用户详情" width="580px" destroy-on-close>
      <div v-if="currentUser" class="detail-content">
        <div class="detail-header">
          <el-avatar :size="72" :src="currentUser.avatar" />
          <div class="header-info">
            <h3>{{ currentUser.nickname || currentUser.email }}</h3>
            <p><el-icon><Message /></el-icon> {{ currentUser.email }}</p>
            <p v-if="currentUser.phone"><el-icon><Phone /></el-icon> {{ currentUser.phone }}</p>
          </div>
          <div class="header-tags">
            <el-tag
              size="small"
              :type="currentUser.role === 'admin' ? 'danger' : currentUser.role === 'counselor' ? 'success' : 'primary'"
            >{{ getRoleText(currentUser.role) }}</el-tag>
            <el-tag size="small" :type="currentUser.banned ? 'danger' : 'success'" style="margin-left:6px">
              {{ currentUser.banned ? '已封禁' : '正常' }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="用户 ID">{{ currentUser.id }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ genderText(currentUser.gender) }}</el-descriptions-item>
          <el-descriptions-item label="邮箱验证">
            <el-tag size="small" :type="currentUser.is_verified ? 'success' : 'info'">
              {{ currentUser.is_verified ? '已验证' : '未验证' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="生日">{{ currentUser.birthDate || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="最后登录" :span="2">{{ currentUser.lastLoginTime || '—' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间" :span="2">{{ currentUser.createdAt }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.testCount }}</span>
            <span class="stat-label">完成测试</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.chatCount }}</span>
            <span class="stat-label">对话次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.appointmentCount }}</span>
            <span class="stat-label">预约次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.favoriteCount }}</span>
            <span class="stat-label">收藏文章</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          :type="currentUser?.banned ? 'success' : 'danger'"
          @click="toggleBan(currentUser); detailVisible = false"
        >{{ currentUser?.banned ? '解封用户' : '封禁用户' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Message, Phone } from '@element-plus/icons-vue'
import { getAdminUsers, banUser } from '@/api/admin'

const loading = ref(false)
const searchKeyword = ref('')
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const currentUser = ref(null)

const loadUsers = async () => {
  try {
    loading.value = true
    const res = await getAdminUsers({
      keyword: searchKeyword.value,
      page: currentPage.value,
      page_size: pageSize.value
    })
    users.value = res.data.list || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

const getRoleText = (role) => {
  const map = { admin: '管理员', counselor: '咨询师', user: '用户' }
  return map[role] || role
}

const genderText = (gender) => {
  const map = { male: '男', female: '女', secret: '保密' }
  return map[gender] || '未知'
}

const viewDetail = (row) => {
  currentUser.value = row
  detailVisible.value = true
}

const toggleBan = async (row) => {
  const action = row.banned ? '解封' : '封禁'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${row.nickname || row.username} 吗？`, '提示', { type: 'warning' })
    await banUser(row.id, { banned: !row.banned })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

onMounted(() => loadUsers())
</script>

<style scoped>
.user-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* 用户信息列 */
.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.user-email {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

/* 数据统计列 */
.stats {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
}

.stats b {
  color: #409eff;
  font-weight: 600;
}

/* 时间文字 */
.time-text {
  font-size: 12px;
  color: #606266;
}

/* 操作按钮组 */
.action-btns {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.action-btns .el-button {
  margin: 0;
  width: 58px;
  padding: 0;
  height: 26px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #fff !important;
}

.btn-detail {
  background-color: #409eff !important;
}

.btn-danger {
  background-color: #f56c6c !important;
}

.btn-success {
  background-color: #67c23a !important;
}

.action-btns .el-button:hover,
.action-btns .el-button:focus,
.action-btns .el-button:active {
  color: #fff !important;
  opacity: 1 !important;
  filter: none !important;
}

.btn-detail:hover { background-color: #409eff !important; }
.btn-danger:hover  { background-color: #f56c6c !important; }
.btn-success:hover { background-color: #67c23a !important; }

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 详情弹窗 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding-bottom: 4px;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.header-info h3 {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-info p {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 4px 0;
  font-size: 13px;
  color: #606266;
}

.header-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
  flex-shrink: 0;
}

.header-tags .el-tag {
  margin: 0;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  text-align: center;
}

.stat-item {
  padding: 14px 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  line-height: 1.2;
}

.stat-label {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
