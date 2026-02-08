import request from '@/api'

export function getHomeStats() {
  return request({
    url: '/getAllData/getHomeData',
    method: 'get'
  })
}

export function getTodayStats() {
  return request({
    url: '/api/stats/today',
    method: 'get'
  })
}

export function refreshSpiderData(data = {}) {
  return request({
    url: '/api/spider/refresh',
    method: 'post',
    data
  })
}

export function getHotWords(hotWord = '') {
  return request({
    url: '/getAllData/getTableData',
    method: 'get',
    params: { hotWord }
  })
}

export function getTableData(params = {}) {
  return request({
    url: '/getAllData/getTableData',
    method: 'get',
    params
  })
}

export function getArticleData(params = {}) {
  return request({
    url: '/getAllData/getArticleData',
    method: 'get',
    params
  })
}

export function getCommentData(params = {}) {
  return request({
    url: '/getAllData/getCommentData',
    method: 'get',
    params
  })
}

export function getIPData(params = {}) {
  return request({
    url: '/getAllData/getIPData',
    method: 'get',
    params
  })
}

export function getYuqingData(params = {}) {
  return request({
    url: '/getAllData/getYuqingData',
    method: 'get',
    params
  })
}

export function getContentCloudData(params = {}) {
  return request({
    url: '/getAllData/getContentCloudData',
    method: 'get',
    params
  })
}
