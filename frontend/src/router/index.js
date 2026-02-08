import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册', public: true }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/index.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'hot-words',
        name: 'HotWords',
        component: () => import('@/views/analysis/hotWords.vue'),
        meta: { title: '热词统计', icon: 'DataAnalysis' }
      },
      {
        path: 'weibo-stats',
        name: 'WeiboStats',
        component: () => import('@/views/analysis/weiboStats.vue'),
        meta: { title: '微博舆情统计', icon: 'ChatLineRound' }
      },
      {
        path: 'article-analysis',
        name: 'ArticleAnalysis',
        component: () => import('@/views/analysis/article.vue'),
        meta: { title: '文章分析', icon: 'Document' }
      },
      {
        path: 'ip-analysis',
        name: 'IPAnalysis',
        component: () => import('@/views/analysis/ip.vue'),
        meta: { title: 'IP分析', icon: 'Location' }
      },
      {
        path: 'comment-analysis',
        name: 'CommentAnalysis',
        component: () => import('@/views/analysis/comment.vue'),
        meta: { title: '评论分析', icon: 'ChatDotRound' }
      },
      {
        path: 'sentiment-analysis',
        name: 'SentimentAnalysis',
        component: () => import('@/views/analysis/sentiment.vue'),
        meta: { title: '舆情分析', icon: 'TrendCharts' }
      },
      {
        path: 'word-cloud',
        name: 'WordCloud',
        component: () => import('@/views/analysis/wordCloud.vue'),
        meta: { title: '词云图', icon: 'Cloudy' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404', public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 微博舆情分析系统`
  }

  const whiteList = ['/login', '/register', '/404', '/500']
  if (whiteList.includes(to.path)) {
    next()
    return
  }

  const token = localStorage.getItem('weibo_token')
  if (!token) {
    next(`/login?redirect=${to.fullPath}`)
    return
  }

  next()
})

export default router
