// API 响应类型定义

// 通用响应
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 推理任务创建响应
export interface InferenceStartResponse {
  taskId: string
  status: string
  estimatedTime: number
}

// 推理状态响应
export interface InferenceStatusResponse {
  taskId: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
}

// 推理结果响应
export interface InferenceResultResponse {
  taskId: string
  originalUrl: string
  segmentationUrl: string
  stats: {
    kidneyVolume: number    // mm³
    tumorVolume: number     // mm³
    processingTime: number  // seconds
  }
}

// 历史记录
export interface HistoryRecord {
  id: string
  filename: string
  uploadTime: string
  status: 'completed' | 'failed'
  stats?: {
    kidneyVolume: number
    tumorVolume: number
    tumorKidneyRatio: number
  }
  originalUrl: string
  segmentationUrl: string
  thumbnailUrl?: string
}

// 历史记录列表响应
export interface HistoryListResponse {
  total: number
  records: HistoryRecord[]
}
