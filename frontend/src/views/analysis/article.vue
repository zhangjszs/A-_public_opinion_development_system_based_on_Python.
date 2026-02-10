<template>
  <div class="article-analysis-container">
    <el-row :gutter="24" class="mb-4">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span class="header-title">文章发布时间分布</span>
          </template>
          <BaseChart
            ref="timeChartRef"
            :options="timeChartOptions"
            height="400px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="24" class="mb-4">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span class="header-title">文章类型分布</span>
          </template>
          <BaseChart
            ref="typeChartRef"
            :options="typeChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span class="header-title">文章情感分布</span>
          </template>
          <BaseChart
            ref="sentimentChartRef"
            :options="sentimentChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="24">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">热门文章排行</span>
              <el-button type="primary" plain size="small" @click="loadData">
                刷新数据
              </el-button>
            </div>
          </template>
          <el-table
            :data="articleList"
            :loading="loading"
            style="width: 100%"
          >
            <el-table-column prop="id" label="文章ID" width="100" align="center" />
            <el-table-column prop="user" label="发布用户" width="150">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar :size="24" :style="{ backgroundColor: '#2563EB', color: '#fff' }">{{ row.user.charAt(0) }}</el-avatar>
                  <span>{{ row.user }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="文章内容" min-width="400" show-overflow-tooltip />
            <el-table-column prop="time" label="发布时间" width="180" align="center" />
            <el-table-column prop="likes" label="点赞数" width="120" align="center">
              <template #default="{ row }">
                <span class="stat-text likes">👍 {{ row.likes }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="reposts" label="转发数" width="120" align="center">
              <template #default="{ row }">
                <span class="stat-text reposts">🔁 {{ row.reposts }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { getArticleData } from '@/api/stats'

const loading = ref(false)
const articleList = ref([])
const timeData = ref({ x: [], y: [] })
const typeData = ref([])
const sentimentData = ref([])

const timeChartRef = ref(null)
const typeChartRef = ref(null)
const sentimentChartRef = ref(null)

const timeChartOptions = computed(() => ({
  tooltip: { 
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderColor: '#E2E8F0',
    textStyle: { color: '#1E293B' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: { 
    type: 'category', 
    data: timeData.value.x,
    axisLine: { lineStyle: { color: '#E2E8F0' } },
    axisLabel: { color: '#64748B' }
  },
  yAxis: { 
    type: 'value',
    splitLine: { lineStyle: { color: '#F1F5F9' } },
    axisLabel: { color: '#64748B' }
  },
  series: [{
    name: '发布数量',
    type: 'line',
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: '#2563EB' },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(37, 99, 235, 0.2)' }, { offset: 1, color: 'rgba(37, 99, 235, 0)' }]
      }
    },
    data: timeData.value.y
  }]
}))

const typeChartOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { 
    orient: 'vertical', 
    right: 10,
    textStyle: { color: '#64748B' }
  },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: { show: false },
    data: typeData.value
  }]
}))

const sentimentChartOptions = computed(() => ({
  tooltip: { 
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: { 
    type: 'category', 
    data: ['正面', '中性', '负面'],
    axisLine: { lineStyle: { color: '#E2E8F0' } },
    axisLabel: { color: '#64748B' }
  },
  yAxis: { 
    type: 'value',
    splitLine: { lineStyle: { color: '#F1F5F9' } },
    axisLabel: { color: '#64748B' }
  },
  series: [{
    type: 'bar',
    barWidth: '40%',
    data: sentimentData.value,
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      color: (params) => {
        const colors = ['#10B981', '#64748B', '#EF4444'] // Emerald, Slate, Red
        return colors[params.dataIndex] || '#2563EB'
      }
    }
  }]
}))

const loadData = async () => {
  loading.value = true
  try {
    const res = await getArticleData()
    if (res.code === 200) {
      const data = res.data
      timeData.value = { x: data.xData || [], y: data.yData || [] }
      typeData.value = data.typeData || []
      sentimentData.value = data.sentimentData || [0, 0, 0]
      articleList.value = (data.articleList || []).map(item => ({
        id: item[0],
        user: item[5],
        content: item[4],
        time: item[1],
        likes: item[2],
        reposts: item[3] || 0
      }))
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.article-analysis-container {
  .chart-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .header-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
    }
  }
  
  .user-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }
  
  .stat-text {
    font-weight: 600;
    
    &.likes { color: #F59E0B; } // Amber
    &.reposts { color: #3B82F6; } // Blue
  }
}
</style>
