<template>
  <div class="home-container">
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <StatCard
          :value="statsData.articleCount"
          label="总文章数"
          icon="Document"
          bg-color="#e3f2fd"
          icon-color="#1976d2"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <StatCard
          :value="statsData.todayCount"
          label="今日新增"
          icon="TrendCharts"
          bg-color="#e8f5e9"
          icon-color="#388e3c"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <StatCard
          :value="statsData.topAuthor"
          label="最火作者"
          icon="User"
          bg-color="#fff3e0"
          icon-color="#f57c00"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <StatCard
          :value="statsData.topRegion"
          label="热门地区"
          icon="Location"
          bg-color="#fce4ec"
          icon-color="#c2185b"
        />
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>文章发布时间分布</span>
              <el-button type="primary" :icon="Refresh" @click="refreshData">
                刷新数据
              </el-button>
            </div>
          </template>
          <BaseChart
            ref="lineChartRef"
            :options="lineChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>评论点赞量 Top 5</span>
          </template>
          <div class="top-comments">
            <div
              v-for="(comment, index) in topComments"
              :key="index"
              class="comment-item"
            >
              <div class="comment-info">
                <span class="comment-user">🧑‍{{ comment.user }}</span>
                <span class="comment-content">{{ comment.content }}</span>
              </div>
              <div class="comment-likes">
                👍 {{ comment.likes }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>文章类型占比</span>
          </template>
          <BaseChart
            ref="pieChartRef"
            :options="pieChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>评论用户时间占比</span>
          </template>
          <BaseChart
            ref="timePieChartRef"
            :options="timePieChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import StatCard from '@/components/Common/StatCard.vue'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { getHomeStats, getTodayStats, refreshSpiderData } from '@/api/stats'

const lineChartRef = ref(null)
const pieChartRef = ref(null)
const timePieChartRef = ref(null)

const statsData = ref({
  articleCount: 0,
  todayCount: '0篇',
  topAuthor: '-',
  topRegion: '-'
})

const topComments = ref([])

const xData = ref([])
const yData = ref([])
const articleTypeData = ref([])
const commentTimeData = ref([])

const lineChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: xData.value
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    name: '文章数',
    type: 'line',
    smooth: true,
    areaStyle: {
      color: 'rgba(0, 128, 255, 0.2)'
    },
    data: yData.value
  }]
}))

const pieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    right: 10
  },
  series: [{
    type: 'pie',
    radius: '70%',
    data: articleTypeData.value
  }]
}))

const timePieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    right: 10
  },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: commentTimeData.value
  }]
}))

const loadData = async () => {
  try {
    const homeRes = await getHomeStats()
    if (homeRes.code === 200) {
      const data = homeRes.data
      statsData.value = {
        articleCount: data.articleLen || 0,
        todayCount: '0篇',
        topAuthor: data.maxLikeAuthorName || '-',
        topRegion: data.maxCity || '-'
      }
      xData.value = data.xData || []
      yData.value = data.yData || []
      topComments.value = (data.topFiveComments || []).map(comment => ({
        user: comment[5] || '',
        content: comment[4] || '',
        likes: comment[2] || 0
      }))
      articleTypeData.value = data.userCreatedDicData || []
      commentTimeData.value = data.commentUserCreatedDicData || []
    }
    
    const todayRes = await getTodayStats()
    if (todayRes.code === 200) {
      statsData.value.todayCount = (todayRes.data.today_articles || 0) + '篇'
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  }
}

const refreshData = async () => {
  try {
    ElMessage.info('开始刷新数据...')
    const res = await refreshSpiderData({ page_num: 3 })
    if (res.code === 200) {
      ElMessage.success(`刷新成功，共爬取 ${res.data.crawled} 条数据`)
      await loadData()
    } else {
      ElMessage.error(res.msg || '刷新失败')
    }
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.home-container {
  .stat-row {
    margin-bottom: 20px;
  }
  
  .chart-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .top-comments {
    .comment-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .comment-info {
        flex: 1;
        
        .comment-user {
          font-weight: bold;
          margin-right: 8px;
        }
        
        .comment-content {
          color: #999;
          font-size: 12px;
          display: block;
          width: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
      
      .comment-likes {
        color: #f56c6c;
        font-weight: bold;
      }
    }
  }
}
</style>
