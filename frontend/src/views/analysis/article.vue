<template>
  <div class="article-analysis-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>文章发布时间分布</span>
          </template>
          <BaseChart
            ref="timeChartRef"
            :options="timeChartOptions"
            height="400px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>文章类型分布</span>
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
            <span>文章情感分布</span>
          </template>
          <BaseChart
            ref="sentimentChartRef"
            :options="sentimentChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>热门文章排行</span>
              <el-button type="primary" @click="loadData">
                刷新
              </el-button>
            </div>
          </template>
          <el-table
            :data="articleList"
            :loading="loading"
            stripe
            border
            style="width: 100%"
          >
            <el-table-column prop="id" label="文章ID" width="100" />
            <el-table-column prop="user" label="发布用户" width="150" />
            <el-table-column prop="content" label="文章内容" min-width="400" show-overflow-tooltip />
            <el-table-column prop="time" label="发布时间" width="180" />
            <el-table-column prop="likes" label="点赞数" width="100" align="center">
              <template #default="{ row }">
                👍 {{ row.likes }}
              </template>
            </el-table-column>
            <el-table-column prop="reposts" label="转发数" width="100" align="center" />
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
const timeData = ref([])
const typeData = ref([])
const sentimentData = ref([])

const timeChartRef = ref(null)
const typeChartRef = ref(null)
const sentimentChartRef = ref(null)

const timeChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: timeData.value.x },
  yAxis: { type: 'value' },
  series: [{
    name: '发布数量',
    type: 'line',
    smooth: true,
    areaStyle: { color: 'rgba(0, 128, 255, 0.2)' },
    data: timeData.value.y
  }]
}))

const typeChartOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', right: 10 },
  series: [{
    type: 'pie',
    radius: '70%',
    data: typeData.value
  }]
}))

const sentimentChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['正面', '中性', '负面'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: sentimentData.value,
    itemStyle: {
      color: (params) => {
        const colors = ['#67c23a', '#909399', '#f56c6c']
        return colors[params.dataIndex] || '#409eff'
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
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}
</style>
