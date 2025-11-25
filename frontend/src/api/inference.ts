import { http } from './index'
import type {
  InferenceStartResponse,
  InferenceStatusResponse,
  InferenceResultResponse,
} from './types'

/**
 * 开始推理任务
 */
export function startInference(
  file: File,
  model: string = '3d_fullres',
  onProgress?: (percent: number) => void
): Promise<InferenceStartResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('model', model)

  return http.post('/inference/start', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percent)
      }
    },
  })
}

/**
 * 查询推理状态
 */
export function getInferenceStatus(taskId: string): Promise<InferenceStatusResponse> {
  return http.get(`/inference/${taskId}/status`)
}

/**
 * 获取推理结果
 */
export function getInferenceResult(taskId: string): Promise<InferenceResultResponse> {
  return http.get(`/inference/${taskId}/result`)
}

/**
 * 取消推理任务
 */
export function cancelInference(taskId: string): Promise<void> {
  return http.delete(`/inference/${taskId}`)
}
