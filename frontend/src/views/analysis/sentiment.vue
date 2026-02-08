<template>
  <div class="sentiment-analysis-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card">
          <el-statistic title="正面评价" :value="sentimentStats.positive" suffix="条">
            <template #suffix>
              <el-icon color="#67c23a"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card">
          <el-statistic title="中性评价" :value="sentimentStats.neutral" suffix="条">
            <template #suffix>
              <el-icon color="#909399"><Remove /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card">
          <el-statistic title="负面评价" :value="sentimentStats.negative" suffix="条">
            <template #suffix>
              <el-icon color="#f56c6c"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>舆情情感分布</span>
          </template>
          <BaseChart
            ref="sentimentPieRef"
            :options="sentimentPieOptions"
            height="350px"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>舆情趋势变化</span>
          </template>
          <BaseChart
            ref="trendChartRef"
            :options="trendChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>关键词云</span>
          </template>
          <div class="keywords-cloud">
            <div
              v-for="(keyword, index) in keywords"
              :key="index"
              class="keyword-item"
              :style="{
                fontSize: (12 + keyword.weight) + 'px',
                color: keyword.color
              }"
            >
              {{ keyword.text }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>舆情详情列表</span>
              <el-button type="primary" @click="loadData">
                刷新数据
              </el-button>
            </div>
          </template>
          <el-table
            :data="sentimentList"
            :loading="loading"
            stripe
            border
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
            <el-table-column prop="sentiment" label="情感倾向" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="getSentimentType(row.sentiment)">
                  {{ row.sentiment }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="情感分数" width="100" align="center" />
            <el-table-column prop="source" label="来源" width="150" />
            <el-table-column prop="time" label="时间" width="180" />
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
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { CircleCheck, Remove, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { getYuqingData } from '@/api/stats'

const loading = ref(false)
const sentimentList = ref([])
const sentimentStats = ref({
  positive: 0,
  neutral: 0,
  negative: 0
})
const sentimentData = ref([])
const trendData = ref([])
const keywords = ref([])

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const sentimentPieRef = ref(null)
const trendChartRef = ref(null)

const sentimentPieOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: sentimentStats.value.positive, name: '正面', itemStyle: { color: '#67c23a' } },
      { value: sentimentStats.value.neutral, name: '中性', itemStyle: { color: '#909399' } },
      { value: sentimentStats.value.negative, name: '负面', itemStyle: { color: '#f56c6c' } }
    ]
  }]
}))

const trendChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: trendData.value.dates || []
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '正面',
      type: 'line',
      smooth: true,
      data: trendData.value.positive || [],
      itemStyle: { color: '#67c23a' }
    },
    {
      name: '中性',
      type: 'line',
      smooth: true,
      data: trendData.value.neutral || [],
      itemStyle: { color: '#909399' }
    },
    {
      name: '负面',
      type: 'line',
      smooth: true,
      data: trendData.value.negative || [],
      itemStyle: { color: '#f56c6c' }
    }
  ]
}))

const getSentimentType = (sentiment) => {
  if (!sentiment) return 'info'
  const lower = sentiment.toLowerCase()
  if (lower.includes('正面') || lower.includes('positive')) return 'success'
  if (lower.includes('负面') || lower.includes('negative')) return 'danger'
  return 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getYuqingData({
      page: currentPage.value,
      pageSize: pageSize.value
    })
    
    if (res.code === 200) {
      const data = res.data
      sentimentStats.value = data.stats || { positive: 0, neutral: 0, negative: 0 }
      sentimentList.value = data.list || []
      trendData.value = data.trend || { dates: [], positive: [], neutral: [], negative: [] }
      keywords.value = data.keywords || []
      total.value = data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
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
.sentiment-analysis-container {
  .stat-card {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .chart-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .keywords-cloud {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 16px;
    padding: 20px;
    
    .keyword-item {
      padding: 8px 16px;
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.05);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: scale(1.1);
        background: rgba(0, 0, 0, 0.1);
      }
    }
  }
  
  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
