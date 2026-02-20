<template>
  <div class="help-page">
    <div class="page-header">
      <h2>
        <el-icon><QuestionFilled /></el-icon>
        帮助中心
      </h2>
      <p class="subtitle">了解系统功能，快速上手微博舆情分析</p>
    </div>

    <!-- 功能卡片概览 -->
    <div class="feature-grid">
      <div v-for="feature in features" :key="feature.title" class="feature-card" @click="$router.push(feature.path)">
        <div class="feature-icon" :style="{ backgroundColor: feature.color + '15', color: feature.color }">
          <el-icon :size="28"><component :is="feature.icon" /></el-icon>
        </div>
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.desc }}</p>
      </div>
    </div>

    <!-- 常见问题 -->
    <el-card class="faq-card">
      <template #header>
        <span class="section-title">💡 常见问题</span>
      </template>
      <el-collapse v-model="activeFaq" accordion>
        <el-collapse-item v-for="(faq, i) in faqs" :key="i" :title="faq.q" :name="i">
          <p class="faq-answer">{{ faq.a }}</p>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 快速指南 -->
    <el-card class="guide-card">
      <template #header>
        <span class="section-title">🚀 快速指南</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(step, i) in guideSteps"
          :key="i"
          :timestamp="'步骤 ' + (i + 1)"
          placement="top"
          :color="step.color"
        >
          <h4>{{ step.title }}</h4>
          <p>{{ step.desc }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 快捷键 -->
    <el-card class="shortcuts-card">
      <template #header>
        <span class="section-title">⌨️ 系统信息</span>
      </template>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">系统版本</span>
          <span class="info-value">v1.0.0</span>
        </div>
        <div class="info-item">
          <span class="info-label">技术栈</span>
          <span class="info-value">Flask + Vue 3 + Element Plus</span>
        </div>
        <div class="info-item">
          <span class="info-label">数据来源</span>
          <span class="info-value">微博开放平台</span>
        </div>
        <div class="info-item">
          <span class="info-label">分析引擎</span>
          <span class="info-value">BERT / SnowNLP 情感分析</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  QuestionFilled, TrendCharts, Document, ChatDotRound,
  Monitor, Bell, DataAnalysis, Share, Cpu, Star
} from '@element-plus/icons-vue'

const activeFaq = ref(0)

const features = [
  { title: '文章分析', desc: '浏览和分析微博文章数据，查看时间趋势和类型分布', icon: 'Document', color: '#2563EB', path: '/article-analysis' },
  { title: '情感分析', desc: '使用 AI 模型分析文章和评论的情感倾向', icon: 'TrendCharts', color: '#7C3AED', path: '/sentiment-analysis' },
  { title: '评论分析', desc: '深入分析评论数据，了解公众意见和情绪', icon: 'ChatDotRound', color: '#059669', path: '/comment-analysis' },
  { title: '传播分析', desc: '追踪信息传播路径，分析信息扩散规律', icon: 'Share', color: '#EA580C', path: '/propagation' },
  { title: '内容预测', desc: '基于历史数据预测内容趋势和传播效果', icon: 'Cpu', color: '#DC2626', path: '/predict' },
  { title: '预警中心', desc: '配置敏感关键词和规则，实时监控舆情异常', icon: 'Bell', color: '#D97706', path: '/alert-center' },
  { title: '数据大屏', desc: '全景数据可视化大屏，一目了然掌握全局', icon: 'Monitor', color: '#0891B2', path: '/big-screen' },
  { title: '我的收藏', desc: '收藏感兴趣的文章，方便后续查阅和跟踪', icon: 'Star', color: '#DB2777', path: '/favorites' },
]

const faqs = [
  { q: '如何开始分析微博数据？', a: '登录系统后，进入"爬虫管理"页面，输入关键词启动爬虫任务。数据采集完成后，即可在各分析模块中查看结果。' },
  { q: '情感分析支持哪些模式？', a: '系统支持两种分析模式：Simple 模式使用 SnowNLP 进行快速分析，Smart 模式使用 BERT 深度学习模型进行更精准的分析。' },
  { q: '如何设置舆情预警？', a: '进入"预警中心"，可以配置预警规则，设置敏感关键词、情感阈值等条件。当新数据触发条件时，系统会自动提醒。' },
  { q: '收藏功能在哪里？', a: '在"文章分析"页面的文章列表中，每篇文章右侧都有收藏按钮。点击即可收藏，通过右上角菜单的"我的收藏"查看收藏列表。' },
  { q: '数据大屏如何使用？', a: '数据大屏提供全景数据可视化，适合在大屏幕上展示。进入后会自动加载最新数据，包含情感趋势、热词云、地域分布等。' },
  { q: '如何生成分析报告？', a: '进入"报告生成"页面，选择时间范围和分析维度，系统会自动生成包含图表和文字说明的分析报告。' },
]

const guideSteps = [
  { title: '注册并登录', desc: '首先在注册页面创建账户，然后登录系统。', color: '#2563EB' },
  { title: '采集数据', desc: '进入"爬虫管理"，输入关键词开始数据采集。系统会自动抓取相关微博和评论。', color: '#7C3AED' },
  { title: '查看分析', desc: '数据采集后，在首页仪表盘查看概览，或进入"文章分析"、"情感分析"等模块深入分析。', color: '#059669' },
  { title: '设置预警', desc: '根据关注的话题，在"预警中心"配置预警规则，及时掌握舆情变化。', color: '#EA580C' },
  { title: '收藏与导出', desc: '收藏重要文章，导出分析结果，生成分析报告。', color: '#DB2777' },
]
</script>

<style lang="scss" scoped>
.help-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;

  h2 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 8px;
  }

  .subtitle {
    color: $text-secondary;
    font-size: 14px;
    margin: 0;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.feature-card {
  padding: 20px;
  background: $surface-color;
  border-radius: $border-radius-large;
  box-shadow: $box-shadow-base;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: $box-shadow-hover;
  }

  .feature-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
  }

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 6px;
  }

  p {
    font-size: 12px;
    color: $text-secondary;
    line-height: 1.5;
    margin: 0;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.faq-card,
.guide-card,
.shortcuts-card {
  margin-bottom: 20px;
  border: none !important;
}

.faq-answer {
  color: $text-regular;
  line-height: 1.7;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .info-label {
    font-size: 12px;
    color: $text-secondary;
  }

  .info-value {
    font-size: 14px;
    font-weight: 500;
    color: $text-primary;
  }
}

@media (max-width: 640px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
