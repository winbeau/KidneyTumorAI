import { http } from './index'
import type {
  InferenceStartResponse,
  InferenceStatusResponse,
  InferenceResultResponse,
} from './types'
import { UPLOAD_TIMEOUT_MS } from '@/utils/constants'

/**
 * 上传文件（不立即开始推理）
 */
export function uploadInferenceFile(
  file: File,
  model: string = '3d_fullres',
  onProgress?: (percent: number) => void
): Promise<InferenceStartResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('model', model)

  return http.post('/inference/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: UPLOAD_TIMEOUT_MS,
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percent)
      }
    },
  })
}

/**
 * 启动已上传任务的推理
 */
export function startInferenceTask(taskId: string): Promise<InferenceStartResponse> {
  return http.post(`/inference/${taskId}/start`)
}

/**
 * 兼容函数：上传后立即启动推理
 */
export async function startInference(
  file: File,
  model: string = '3d_fullres',
  onProgress?: (percent: number) => void
): Promise<InferenceStartResponse> {
  const uploadRes = await uploadInferenceFile(file, model, onProgress)
  return startInferenceTask(uploadRes.taskId)
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
