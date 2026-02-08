<template>
  <div class="weibo-stats-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词搜索">
          <el-input
            v-model="filterForm.keyword"
            placeholder="请输入搜索关键词"
            prefix-icon="Search"
            clearable
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>微博舆情统计</span>
          <el-button type="primary" :icon="Refresh" @click="handleRefresh">
            刷新数据
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="tableData"
        :loading="loading"
        stripe
        border
        style="width: 100%"
        :default-sort="{ prop: 'likes', order: 'descending' }"
      >
        <el-table-column prop="id" label="文章ID" width="100" sortable />
        <el-table-column prop="user" label="评论用户" width="150" />
        <el-table-column prop="location" label="用户地址" width="150" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="time" label="评论时间" width="180" sortable />
        <el-table-column prop="likes" label="点赞数" width="120" align="center" sortable>
          <template #default="{ row }">
            <el-tag type="danger">👍 {{ row.likes }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reposts" label="转发数" width="100" align="center" sortable />
        <el-table-column prop="comments" label="评论数" width="100" align="center" sortable />
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getTableData } from '@/api/stats'

const loading = ref(false)
const tableData = ref([])
const hotWordList = ref([])

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = ref({
  keyword: '',
  dateRange: []
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getTableData({
      page: currentPage.value,
      pageSize: pageSize.value,
      keyword: filterForm.value.keyword,
      startDate: filterForm.value.dateRange?.[0],
      endDate: filterForm.value.dateRange?.[1]
    })
    
    if (res.code === 200) {
      const data = res.data
      hotWordList.value = data.hotWordList || []
      tableData.value = (data.tableList || []).map(item => ({
        id: item[0],
        user: item[5],
        location: item[7],
        content: item[4],
        time: item[1],
        likes: item[2],
        reposts: item[3] || 0,
        comments: item[6] || 0
      }))
      total.value = data.total || tableData.value.length
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  filterForm.value.keyword = ''
  filterForm.value.dateRange = []
  currentPage.value = 1
  loadData()
}

const handleRefresh = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.weibo-stats-container {
  .filter-card {
    margin-bottom: 20px;
  }
  
  .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .pagination-wrapper {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
