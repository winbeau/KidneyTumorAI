import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { InferenceStatus } from '@/utils/constants'
import { INFERENCE_STATUS } from '@/utils/constants'
import {
  uploadInferenceFile,
  startInferenceTask as apiStartInferenceTask,
  retryInferenceTask as apiRetryInferenceTask,
  getInferenceStatus,
  getInferenceResult,
  cancelInference as apiCancelInference,
} from '@/api/inference'
import type { InferenceResultResponse } from '@/api/types'

export const useInferenceStore = defineStore('inference', () => {
  // 状态
  const status = ref<InferenceStatus>(INFERENCE_STATUS.IDLE)
  const progress = ref(0)
  const currentFile = ref<File | null>(null)
  const taskId = ref<string | null>(null)
  const result = ref<InferenceResultResponse | null>(null)
  const error = ref<string | null>(null)
  const uploadProgress = ref(0)
  const waitingStart = ref(false)
  const statusMessage = ref<string | null>(null)
  const elapsedSeconds = ref(0)

  const processingStatuses: InferenceStatus[] = [
    INFERENCE_STATUS.UPLOADING,
    INFERENCE_STATUS.QUEUED,
    INFERENCE_STATUS.PROCESSING,
  ]

  // 计算属性
  const isProcessing = computed(() => {
    if (status.value === INFERENCE_STATUS.QUEUED && waitingStart.value) {
      return false
    }
    return processingStatuses.includes(status.value)
  })
  const isWaitingStart = computed(() => status.value === INFERENCE_STATUS.QUEUED && waitingStart.value)

  const isCompleted = computed(() => status.value === INFERENCE_STATUS.COMPLETED)

  const statusText = computed(() => {
    if (status.value === INFERENCE_STATUS.QUEUED && waitingStart.value) return '待开始'
    switch (status.value) {
      case INFERENCE_STATUS.IDLE: return '等待上传'
      case INFERENCE_STATUS.UPLOADING: return '上传中...'
      case INFERENCE_STATUS.QUEUED: return '排队中...'
      case INFERENCE_STATUS.PROCESSING: return '分割处理中...'
      case INFERENCE_STATUS.COMPLETED: return '处理完成'
      case INFERENCE_STATUS.FAILED: return '处理失败'
      default: return ''
    }
  })

  // 轮询定时器
  let pollTimer: ReturnType<typeof setInterval> | null = null
  let elapsedTimer: ReturnType<typeof setInterval> | null = null

  const fallbackMessages: Record<InferenceStatus, string> = {
    [INFERENCE_STATUS.IDLE]: '等待上传',
    [INFERENCE_STATUS.UPLOADING]: '上传中',
    [INFERENCE_STATUS.QUEUED]: '排队中',
    [INFERENCE_STATUS.PROCESSING]: '分割处理中',
    [INFERENCE_STATUS.COMPLETED]: '处理完成',
    [INFERENCE_STATUS.FAILED]: '处理失败',
  }

  const startElapsedTimer = (reset = false) => {
    if (elapsedTimer && !reset) return
    if (elapsedTimer) clearInterval(elapsedTimer)
    if (reset) elapsedSeconds.value = 0
    elapsedTimer = setInterval(() => {
      elapsedSeconds.value += 1
    }, 1000)
  }

  const stopElapsedTimer = () => {
    if (elapsedTimer) {
      clearInterval(elapsedTimer)
      elapsedTimer = null
    }
  }

  // 上传文件但不立即启动推理
  async function uploadFile(file: File) {
    try {
      reset()
      currentFile.value = file
      status.value = INFERENCE_STATUS.UPLOADING
      statusMessage.value = '文件上传中...'
      startElapsedTimer(true)

      // 上传文件并开始推理
      const response = await uploadInferenceFile(file, '3d_fullres', (percent) => {
        uploadProgress.value = percent
      })

      taskId.value = response.taskId
      status.value = INFERENCE_STATUS.QUEUED
      waitingStart.value = true
      statusMessage.value = '上传完成，等待开始推理'
    } catch (e: any) {
      status.value = INFERENCE_STATUS.FAILED
      error.value = e.message || '启动推理失败'
      statusMessage.value = error.value
      throw e
    }
  }

  // 手动启动推理
  async function startInference() {
    if (!taskId.value) {
      throw new Error('没有任务可启动')
    }
    try {
      waitingStart.value = false
      status.value = INFERENCE_STATUS.QUEUED
      error.value = null
      result.value = null
      startPolling()
      startElapsedTimer(false)
      statusMessage.value = '排队中...'
      await apiStartInferenceTask(taskId.value)
    } catch (e: any) {
      status.value = INFERENCE_STATUS.FAILED
      error.value = e.message || '启动推理失败'
      statusMessage.value = error.value
      stopPolling()
      stopElapsedTimer()
      throw e
    }
  }

  // 失败后重试推理（复用已上传文件）
  async function retryInference() {
    if (!taskId.value) {
      throw new Error('没有任务可重试')
    }
    try {
      waitingStart.value = false
      status.value = INFERENCE_STATUS.QUEUED
      progress.value = 0
      uploadProgress.value = 0
      result.value = null
      error.value = null
      statusMessage.value = '重新排队中...'
      startPolling()
      startElapsedTimer()
      await apiRetryInferenceTask(taskId.value)
    } catch (e: any) {
      status.value = INFERENCE_STATUS.FAILED
      error.value = e.message || '重试推理失败'
      statusMessage.value = error.value
      stopPolling()
      stopElapsedTimer()
      throw e
    }
  }

  // 轮询状态
  function startPolling() {
    if (pollTimer) clearInterval(pollTimer)

    pollTimer = setInterval(async () => {
      if (!taskId.value) return

      try {
        const statusResponse = await getInferenceStatus(taskId.value)
        progress.value = statusResponse.progress
        statusMessage.value = statusResponse.message || fallbackMessages[statusResponse.status as InferenceStatus]

        if (statusResponse.status === 'processing') {
          status.value = INFERENCE_STATUS.PROCESSING
        } else if (statusResponse.status === 'completed') {
          stopPolling()
          stopElapsedTimer()
          status.value = INFERENCE_STATUS.COMPLETED
          statusMessage.value = statusResponse.message || '分割完成'
          // 获取结果
          result.value = await getInferenceResult(taskId.value)
        } else if (statusResponse.status === 'failed') {
          stopPolling()
          stopElapsedTimer()
          status.value = INFERENCE_STATUS.FAILED
          error.value = statusResponse.message || '推理失败'
          statusMessage.value = error.value
        }
      } catch (e: any) {
        console.error('Poll error:', e)
      }
    }, 2000) // 每2秒轮询
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // 取消推理
  async function cancelInference() {
    if (taskId.value) {
      try {
        await apiCancelInference(taskId.value)
      } catch (e) {
        console.error('Cancel error:', e)
      }
    }
    stopPolling()
    reset()
  }

  // 重置状态
  function reset() {
    stopPolling()
    status.value = INFERENCE_STATUS.IDLE
    progress.value = 0
    uploadProgress.value = 0
    waitingStart.value = false
    currentFile.value = null
    taskId.value = null
    result.value = null
    error.value = null
    statusMessage.value = null
    elapsedSeconds.value = 0
    stopElapsedTimer()
  }

  return {
    // 状态
    status,
    progress,
    uploadProgress,
    currentFile,
    taskId,
    result,
    error,
    waitingStart,
    statusMessage,
    elapsedSeconds,
    // 计算属性
    isProcessing,
    isWaitingStart,
    isCompleted,
    statusText,
    // 方法
    uploadFile,
    startInference,
    retryInference,
    cancelInference,
    reset,
  }
})
