import request from '@/api'

export function getTaskStatus(taskId) {
  return request({
    url: `/api/tasks/${encodeURIComponent(taskId)}/status`,
    method: 'get',
    loadingOptions: false,
  })
}
