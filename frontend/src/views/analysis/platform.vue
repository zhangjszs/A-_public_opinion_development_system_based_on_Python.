<template>
  <div class="platform-monitor-container">
    <el-row :gutter="24" class="mb-4">
      <el-col :span="24">
        <el-card class="platform-tabs-card">
          <el-tabs v-model="activePlatform" @tab-change="handlePlatformChange">
            <el-tab-pane 
              v-for="platform in platforms" 
              :key="platform.id" 
              :name="platform.id"
              :label="platform.label"
            >
              <template #label>
                <span class="platform-tab">
                  <span class="platform-icon">{{ platform.icon }}</span>
                  <span>{{ platform.name }}</span>
                  <el-tag v-if="platform.enabled" type="success" size="small">启用</el-tag>
                </span>
              </template>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="mb-4">
      <el-col :xs="12" :sm="6" :md="4" v-for="stat in currentStats" :key="stat.label">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24">
      <el-col :xs="24" :lg="16">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>{{ currentPlatformName }}内容列表</span>
              <div class="header-actions">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索内容..."
                  :prefix-icon="Search"
                  style="width: 200px"
                  size="small"
                  clearable
                />
                <el-select v-model="sentimentFilter" placeholder="情感筛选" size="small" style="width: 100px" clearable>
                  <el-option label="正面" value="positive" />
                  <el-option label="中性" value="neutral" />
                  <el-option label="负面" value="negative" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="content-list">
            <div v-for="item in filteredContent" :key="item.content_id" class="content-item">
              <div class="content-header">
                <div class="author-info">
                  <el-avatar :size="36" :icon="User" />
                  <div class="author-detail">
                    <span class="author-name">
                      {{ item.author_name }}
                      <el-icon v-if="item.author_verified" class="verified-icon"><CircleCheckFilled /></el-icon>
                    </span>
                    <span class="author-followers">{{ item.author_followers }} 粉丝</span>
                  </div>
                </div>
                <div class="content-meta">
                  <span class="publish-time">{{ formatTime(item.published_at) }}</span>
                </div>
              </div>
              
              <div class="content-body">
                <p>{{ item.content }}</p>
              </div>
              
              <div class="content-stats">
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ formatNumber(item.view_count) }}
                </span>
                <span class="stat-item">
                  <el-icon><Star /></el-icon>
                  {{ formatNumber(item.like_count) }}
                </span>
                <span class="stat-item">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ formatNumber(item.comment_count) }}
                </span>
                <span class="stat-item">
                  <el-icon><Share /></el-icon>
                  {{ formatNumber(item.repost_count) }}
                </span>
                <el-tag 
                  :type="getSentimentType(item.sentiment)" 
                  size="small" 
                  class="sentiment-tag"
                >
                  {{ getSentimentLabel(item.sentiment) }}
                </el-tag>
              </div>
              
              <div class="content-tags" v-if="item.keywords?.length">
                <el-tag v-for="kw in item.keywords.slice(0, 3)" :key="kw" size="small" effect="plain">
                  {{ kw }}
                </el-tag>
              </div>
            </div>
            
            <el-empty v-if="filteredContent.length === 0" description="暂无数据" />
          </div>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              layout="total, prev, pager, next"
              @current-change="loadData"
            />
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>各平台数据对比</span>
          </template>
          <BaseChart ref="compareChartRef" :options="compareChartOptions" height="300px" />
        </el-card>
        
        <el-card class="trend-card mt-4">
          <template #header>
            <span>情感分布</span>
          </template>
          <BaseChart ref="sentimentChartRef" :options="sentimentChartOptions" height="250px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, User, View, Star, ChatDotRound, Share, CircleCheckFilled } from '@element-plus/icons-vue'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { getPlatformData, getAllPlatformsData, getPlatformStats, comparePlatforms } from '@/api/platform'

const activePlatform = ref('weibo')
const platforms = ref([
  { id: 'weibo', name: '微博', icon: '📱', enabled: true, label: '微博' },
  { id: 'wechat', name: '微信公众号', icon: '💬', enabled: true, label: '微信公众号' },
  { id: 'douyin', name: '抖音', icon: '🎵', enabled: true, label: '抖音' },
  { id: 'zhihu', name: '知乎', icon: '💡', enabled: true, label: '知乎' },
])

const currentPlatformName = computed(() => {
  const p = platforms.value.find(p => p.id === activePlatform.value)
  return p?.name || '未知平台'
})

const contentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const sentimentFilter = ref('')

const platformStats = ref({})
const comparisonData = ref({})

const currentStats = computed(() => {
  const stats = platformStats.value[activePlatform.value] || {}
  return [
    { label: '内容总数', value: formatNumber(stats.total_content || 0) },
    { label: '用户总数', value: formatNumber(stats.total_users || 0) },
    { label: '互动总量', value: formatNumber((stats.total_likes || 0) + (stats.total_comments || 0)) },
    { label: '增长率', value: `${((stats.growth_rate || 0) * 100).toFixed(1)}%` },
  ]
})

const filteredContent = computed(() => {
  let list = contentList.value
  
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(item => 
      item.content.toLowerCase().includes(kw) ||
      item.author_name.toLowerCase().includes(kw)
    )
  }
  
  if (sentimentFilter.value) {
    list = list.filter(item => item.sentiment === sentimentFilter.value)
  }
  
  return list
})

const compareChartOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['内容数', '点赞数', '评论数'], textStyle: { fontSize: 10 } },
  xAxis: {
    type: 'category',
    data: ['微博', '微信', '抖音', '知乎'],
    axisLabel: { fontSize: 10 }
  },
  yAxis: { type: 'value' },
  series: [
    { name: '内容数', type: 'bar', data: [50, 30, 45, 25] },
    { name: '点赞数', type: 'bar', data: [1200, 800, 1500, 900] },
    { name: '评论数', type: 'bar', data: [300, 200, 400, 250] }
  ]
}))

const sentimentChartOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 45, name: '正面', itemStyle: { color: '#10B981' } },
      { value: 30, name: '中性', itemStyle: { color: '#64748B' } },
      { value: 25, name: '负面', itemStyle: { color: '#EF4444' } }
    ],
    label: { fontSize: 10 }
  }]
}))

const formatNumber = (num) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const getSentimentType = (sentiment) => {
  const types = { 'positive': 'success', 'neutral': 'info', 'negative': 'danger' }
  return types[sentiment] || 'info'
}

const getSentimentLabel = (sentiment) => {
  const labels = { 'positive': '正面', 'neutral': '中性', 'negative': '负面' }
  return labels[sentiment] || '未知'
}

const loadData = async () => {
  try {
    const res = await getPlatformData(activePlatform.value, {
      page: currentPage.value,
      page_size: pageSize.value,
      demo: true
    })
    
    if (res.code === 200) {
      contentList.value = res.data.data
      total.value = res.data.pagination.total
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const loadStats = async () => {
  try {
    const res = await getPlatformStats('all')
    if (res.code === 200) {
      platformStats.value = res.data
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadComparison = async () => {
  try {
    const res = await comparePlatforms(['weibo', 'wechat', 'douyin', 'zhihu'])
    if (res.code === 200) {
      comparisonData.value = res.data.comparison
    }
  } catch (error) {
    console.error('加载对比数据失败:', error)
  }
}

const handlePlatformChange = () => {
  currentPage.value = 1
  loadData()
}

onMounted(() => {
  loadData()
  loadStats()
  loadComparison()
})
</script>

<style lang="scss" scoped>
.platform-monitor-container {
  .platform-tabs-card {
    .platform-tab {
      display: flex;
      align-items: center;
      gap: 6px;
      
      .platform-icon {
        font-size: 16px;
      }
    }
  }
  
  .stat-card {
    margin-bottom: 16px;
    
    .stat-content {
      text-align: center;
      
      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-color-primary);
      }
      
      .stat-label {
        font-size: 13px;
        color: var(--el-text-color-secondary);
        margin-top: 4px;
      }
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .content-list {
    .content-item {
      padding: 16px;
      border-bottom: 1px solid var(--el-border-color-lighter);
      
      &:last-child {
        border-bottom: none;
      }
      
      .content-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        
        .author-info {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .author-detail {
            display: flex;
            flex-direction: column;
            
            .author-name {
              font-weight: 500;
              display: flex;
              align-items: center;
              gap: 4px;
              
              .verified-icon {
                color: var(--el-color-primary);
              }
            }
            
            .author-followers {
              font-size: 12px;
              color: var(--el-text-color-secondary);
            }
          }
        }
        
        .content-meta {
          .publish-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
      
      .content-body {
        margin-bottom: 12px;
        
        p {
          margin: 0;
          line-height: 1.6;
        }
      }
      
      .content-stats {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 8px;
        
        .stat-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: var(--el-text-color-secondary);
        }
        
        .sentiment-tag {
          margin-left: auto;
        }
      }
      
      .content-tags {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
    }
  }
  
  .pagination-container {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
  
  .mt-4 { margin-top: 16px; }
  .mb-4 { margin-bottom: 16px; }
}
</style>
