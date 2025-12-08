// 分割标签颜色配置
export const SEGMENTATION_COLORS = {
  0: { name: '背景', color: 'transparent', rgba: [0, 0, 0, 0] },
  1: { name: '肾脏', color: '#E74C3C', rgba: [231, 76, 60, 153] },
  2: { name: '肿瘤', color: '#3498DB', rgba: [52, 152, 219, 204] },
} as const

// API 基础路径
export const API_BASE_URL = '/api/v1'

// 文件上传限制
export const UPLOAD_CONFIG = {
  maxSize: 1024 * 1024 * 1024, // 1GB
  acceptTypes: ['.nii', '.nii.gz'],
  mimeTypes: ['application/gzip', 'application/x-gzip'],
}
export const UPLOAD_TIMEOUT_MS = 10 * 60 * 1000 // 10 分钟，适配大文件上传

// 推理状态
export const INFERENCE_STATUS = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  QUEUED: 'queued',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

export type InferenceStatus = typeof INFERENCE_STATUS[keyof typeof INFERENCE_STATUS]

// NiiVue 渲染模式
export const RENDER_MODES = {
  VOLUME: 0,
  MIP: 1,
  SURFACE: 2,
} as const

// 切片视图类型
export const SLICE_TYPES = {
  AXIAL: 0,     // 横断面
  CORONAL: 1,   // 冠状面
  SAGITTAL: 2,  // 矢状面
  RENDER: 3,    // 3D渲染
  MULTIPLANAR: 4, // 多平面
} as const
