import { http } from './index'
import type { HistoryListResponse, HistoryRecord } from './types'

/**
 * 获取历史记录列表
 */
export function getHistoryList(
  page: number = 1,
  pageSize: number = 20
): Promise<HistoryListResponse> {
  return http.get('/history', {
    params: { page, pageSize },
  })
}

/**
 * 获取单条历史记录
 */
export function getHistoryRecord(id: string): Promise<HistoryRecord> {
  return http.get(`/history/${id}`)
}

/**
 * 删除历史记录
 */
export function deleteHistoryRecord(id: string): Promise<void> {
  return http.delete(`/history/${id}`)
}

/**
 * 批量删除历史记录
 */
export function batchDeleteHistory(ids: string[]): Promise<void> {
  return http.post('/history/batch-delete', { ids })
}
