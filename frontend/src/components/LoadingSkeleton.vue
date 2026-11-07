<template>
  <div class="skeleton-wrapper">
    <!-- 卡片骨架屏 -->
    <div v-if="type === 'card'" class="skeleton-card">
      <el-skeleton animated>
        <template #template>
          <div class="skeleton-card-content">
            <el-skeleton-item variant="image" style="width: 100%; height: 200px" />
            <div style="padding: 14px">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <div style="margin-top: 10px">
                <el-skeleton-item variant="text" />
                <el-skeleton-item variant="text" style="width: 70%" />
              </div>
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 列表骨架屏 -->
    <div v-if="type === 'list'" class="skeleton-list">
      <el-skeleton :rows="rows" animated />
    </div>

    <!-- 表格骨架屏 -->
    <div v-if="type === 'table'" class="skeleton-table">
      <el-skeleton animated>
        <template #template>
          <div v-for="i in 3" :key="i" class="skeleton-table-row">
            <el-skeleton-item variant="text" style="width: 20%" />
            <el-skeleton-item variant="text" style="width: 30%" />
            <el-skeleton-item variant="text" style="width: 25%" />
            <el-skeleton-item variant="text" style="width: 25%" />
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 默认骨架屏 -->
    <div v-if="type === 'default'" class="skeleton-default">
      <el-skeleton :rows="rows" animated />
    </div>
  </div>
</template>

<script setup>
defineProps({
  // 骨架屏类型: card, list, table, default
  type: {
    type: String,
    default: 'default'
  },
  // 行数（用于list和default类型）
  rows: {
    type: Number,
    default: 5
  }
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.skeleton-wrapper { width: 100%; }

.skeleton-card {
  .skeleton-card-content {
    border-radius: 20px;
    overflow: hidden;
    background: $bg-white;
    border: 1px solid $border-lighter;
  }
}

.skeleton-list {
  padding: 20px 24px;
  background: $bg-white;
  border-radius: 16px;
  border: 1px solid $border-lighter;
}

.skeleton-table {
  background: $bg-white;
  border-radius: 16px;
  border: 1px solid $border-lighter;
  padding: 20px 24px;

  .skeleton-table-row {
    display: flex;
    gap: 16px;
    padding: 14px 0;
    border-bottom: 1px solid $border-lighter;

    &:last-child { border-bottom: none; }
  }
}

.skeleton-default {
  padding: 20px 24px;
  background: $bg-white;
  border-radius: 16px;
  border: 1px solid $border-lighter;
}
</style>
