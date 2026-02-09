import request from '@/api/request'

export function getHomeStats() {
  return request({
    url: '/getAllData/getHomeData',
    method: 'get',
    loadingOptions: { text: '加载首页数据...' }
  })
}

export function getTodayStats() {
  return request({
    url: '/api/stats/today',
    method: 'get',
    loadingOptions: { text: '加载今日统计...' }
  })
}

export function refreshSpiderData(data = {}) {
  return request({
    url: '/api/spider/refresh',
    method: 'post',
    data,
    loadingOptions: { text: '正在刷新数据...' }
  })
}

export function getHotWords(hotWord = '') {
  return request({
    url: '/getAllData/getTableData',
    method: 'get',
    params: { hotWord },
    loadingOptions: hotWord ? { text: '搜索中...' } : { text: '加载热词数据...' }
  })
}

export function getTableData(params = {}) {
  return request({
    url: '/getAllData/getTableData',
    method: 'get',
    params,
    loadingOptions: { text: '加载表格数据...' }
  })
}

export function getArticleData(params = {}) {
  return request({
    url: '/getAllData/getArticleData',
    method: 'get',
    params,
    loadingOptions: { text: '加载文章分析数据...' }
  })
}

export function getCommentData(params = {}) {
  return request({
    url: '/getAllData/getCommentData',
    method: 'get',
    params,
    loadingOptions: { text: '加载评论分析数据...' }
  })
}

export function getIPData(params = {}) {
  return request({
    url: '/getAllData/getIPData',
    method: 'get',
    params,
    loadingOptions: { text: '加载IP分析数据...' }
  })
}

export function getYuqingData(params = {}) {
  return request({
    url: '/getAllData/getYuqingData',
    method: 'get',
    params,
    loadingOptions: { text: '加载舆情分析数据...' }
  })
}

export function getContentCloudData(params = {}) {
  return request({
    url: '/getAllData/getContentCloudData',
    method: 'get',
    params,
    loadingOptions: { text: '加载词云数据...' }
  })
}

// 清空缓存
export function clearCache() {
  return request({
    url: '/getAllData/clearCache',
    method: 'post',
    loadingOptions: { text: '清空缓存...' }
  })
}
