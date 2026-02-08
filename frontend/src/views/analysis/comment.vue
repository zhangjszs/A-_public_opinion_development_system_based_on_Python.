<template>
  <div class="comment-analysis-container">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>评论时间分布</span>
          </template>
          <BaseChart
            ref="timeChartRef"
            :options="timeChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>评论用户活跃度</span>
          </template>
          <BaseChart
            ref="userActivityChartRef"
            :options="userActivityChartOptions"
            height="350px"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>评论情感分布</span>
          </template>
          <BaseChart
            ref="sentimentPieRef"
            :options="sentimentPieOptions"
            height="300px"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <span>热门评论</span>
          </template>
          <div class="hot-comments">
            <div
              v-for="(comment, index) in hotComments"
              :key="index"
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-user">🧑‍{{ comment.user }}</span>
                <span class="comment-time">{{ comment.time }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-footer">
                <span>👍 {{ comment.likes }}</span>
                <span>💬 {{ comment.replies }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { getCommentData } from '@/api/stats'

const loading = ref(false)
const hotComments = ref([])
const timeData = ref([])
const userActivityData = ref([])
const sentimentData = ref([])

const timeChartRef = ref(null)
const userActivityChartRef = ref(null)
const sentimentPieRef = ref(null)

const timeChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: timeData.value.hours || []
  },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    smooth: true,
    areaStyle: { color: 'rgba(0, 128, 255, 0.2)' },
    data: timeData.value.counts || []
  }]
}))

const userActivityChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: userActivityData.value.users || []
  },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: userActivityData.value.counts || [],
    itemStyle: { color: '#005AA0' }
  }]
}))

const sentimentPieOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: sentimentData.value
  }]
}))

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCommentData()
    if (res.code === 200) {
      const data = res.data
      timeData.value = data.timeDistribution || { hours: [], counts: [] }
      userActivityData.value = data.userActivity || { users: [], counts: [] }
      sentimentData.value = data.sentimentData || []
      hotComments.value = data.hotComments || []
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
.comment-analysis-container {
  .chart-card {
    margin-bottom: 20px;
  }
  
  .hot-comments {
    .comment-item {
      padding: 16px;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .comment-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        
        .comment-user {
          font-weight: bold;
        }
        
        .comment-time {
          color: #999;
          font-size: 12px;
        }
      }
      
      .comment-content {
        color: #333;
        margin-bottom: 8px;
        line-height: 1.5;
      }
      
      .comment-footer {
        display: flex;
        gap: 16px;
        color: #999;
        font-size: 12px;
      }
    }
  }
}
</style>
