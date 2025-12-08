<script setup lang="ts">
import {
  NCard,
  NUpload,
  NUploadDragger,
  NButton,
  NProgress,
  NAlert,
  NSpace,
  NStatistic,
  NGrid,
  NGi,
  useMessage,
} from 'naive-ui'
import type { UploadFileInfo } from 'naive-ui'
import { useInferenceStore } from '@/stores/inference'
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { UPLOAD_CONFIG, INFERENCE_STATUS } from '@/utils/constants'

const router = useRouter()
const message = useMessage()
const inferenceStore = useInferenceStore()
const maxSizeText = computed(() => {
  const gb = UPLOAD_CONFIG.maxSize / 1024 / 1024 / 1024
  if (gb >= 1) return `${gb.toFixed(gb % 1 === 0 ? 0 : 1)}GB`
  return `${(UPLOAD_CONFIG.maxSize / 1024 / 1024).toFixed(0)}MB`
})

// 文件验证
const handleBeforeUpload = (data: { file: UploadFileInfo }) => {
  const file = data.file.file
  if (!file) return false

  // 检查文件类型
  const isValidType = file.name.endsWith('.nii') || file.name.endsWith('.nii.gz')
  if (!isValidType) {
    message.error('请上传 NIfTI 格式文件 (.nii 或 .nii.gz)')
    return false
  }

  // 检查文件大小
  if (file.size > UPLOAD_CONFIG.maxSize) {
    message.error(`文件大小不能超过 ${maxSizeText.value}`)
    return false
  }

  return true
}

// 处理文件选择
const handleFileChange = async (options: { file: UploadFileInfo; fileList: UploadFileInfo[] }) => {
  const file = options.file.file
  if (!file) return

  try {
    await inferenceStore.uploadFile(file)
    message.success('文件上传成功，请点击“开始推理”')
  } catch (e: any) {
    message.error(e.message || '上传失败')
  }
}

const startManualInference = async () => {
  try {
    await inferenceStore.startInference()
    message.success('任务已开始')
  } catch (e: any) {
    message.error(e.message || '启动推理失败')
  }
}

// 查看结果
const viewResult = () => {
  if (inferenceStore.taskId) {
    router.push(`/viewer/${inferenceStore.taskId}`)
  }
}

// 重新开始
const restart = () => {
  inferenceStore.reset()
}

// 格式化体积
const formatVolume = (mm3: number) => {
  if (mm3 > 1000000) {
    return `${(mm3 / 1000000).toFixed(2)} cm³`
  }
  return `${mm3.toFixed(0)} mm³`
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- 欢迎卡片 -->
    <NCard class="mb-6">
      <div class="text-center py-4">
        <div class="i-carbon-analytics text-6xl text-blue-500 mx-auto mb-4" />
        <h1 class="text-2xl font-bold mb-2">肾脏肿瘤 AI 分割系统</h1>
        <p class="text-gray-500">
          基于 nnU-Net 深度学习模型，自动分割 CT 影像中的肾脏和肿瘤区域
        </p>
      </div>
    </NCard>

    <!-- 上传区域 -->
    <NCard title="上传 CT 影像" class="mb-6">
      <template v-if="inferenceStore.status === INFERENCE_STATUS.IDLE">
        <NUpload
          accept=".nii,.nii.gz"
          :max="1"
          :show-file-list="false"
          @before-upload="handleBeforeUpload"
          @change="handleFileChange"
        >
          <NUploadDragger>
            <div class="py-8">
              <div class="i-carbon-cloud-upload text-5xl text-gray-400 mx-auto mb-4" />
              <p class="text-lg mb-2">点击或拖拽文件到此区域上传</p>
              <p class="text-gray-400 text-sm">
                支持 NIfTI 格式 (.nii, .nii.gz)，最大 {{ maxSizeText }}
              </p>
            </div>
          </NUploadDragger>
        </NUpload>
      </template>

      <!-- 上传完成，等待手动启动 -->
      <template v-else-if="inferenceStore.isWaitingStart">
        <div class="py-6 text-center space-y-4">
          <div class="i-carbon-checkmark text-5xl text-green-500 mx-auto" />
          <p class="text-lg font-medium">上传完成，准备开始推理</p>
          <p class="text-gray-500">
            {{ inferenceStore.currentFile?.name }}
          </p>
          <NProgress
            type="line"
            :percentage="100"
            :status="'success'"
            :indicator-placement="'inside'"
            class="max-w-md mx-auto"
          />
          <NSpace justify="center">
            <NButton type="primary" size="large" @click="startManualInference">
              开始推理
            </NButton>
            <NButton size="large" @click="inferenceStore.reset">
              取消
            </NButton>
          </NSpace>
        </div>
      </template>

      <!-- 处理中状态 -->
      <template v-else-if="inferenceStore.isProcessing">
        <div class="py-8 text-center">
          <div class="i-carbon-rotate-360 text-5xl text-blue-500 mx-auto mb-4 loading-spin" />
          <p class="text-lg mb-2">{{ inferenceStore.statusText }}</p>
          <p class="text-gray-500 mb-4">{{ inferenceStore.currentFile?.name }}</p>

          <NProgress
            type="line"
            :percentage="inferenceStore.status === INFERENCE_STATUS.UPLOADING
              ? inferenceStore.uploadProgress
              : inferenceStore.progress"
            :status="'default'"
            :indicator-placement="'inside'"
            class="max-w-md mx-auto mb-4"
          />

          <NButton type="error" ghost @click="inferenceStore.cancelInference">
            取消
          </NButton>
        </div>
      </template>

      <!-- 完成状态 -->
      <template v-else-if="inferenceStore.isCompleted && inferenceStore.result">
        <NAlert type="success" title="分割完成" class="mb-4">
          文件 {{ inferenceStore.currentFile?.name }} 已成功处理
        </NAlert>

        <NGrid :cols="3" :x-gap="16" class="mb-6">
          <NGi>
            <NStatistic label="肾脏体积">
              <template #default>
                {{ formatVolume(inferenceStore.result.stats.kidneyVolume) }}
              </template>
            </NStatistic>
          </NGi>
          <NGi>
            <NStatistic label="肿瘤体积">
              <template #default>
                {{ formatVolume(inferenceStore.result.stats.tumorVolume) }}
              </template>
            </NStatistic>
          </NGi>
          <NGi>
            <NStatistic label="处理时间">
              <template #default>
                {{ inferenceStore.result.stats.processingTime.toFixed(1) }}s
              </template>
            </NStatistic>
          </NGi>
        </NGrid>

        <NSpace justify="center">
          <NButton type="primary" size="large" @click="viewResult">
            <template #icon>
              <div class="i-carbon-view" />
            </template>
            查看分割结果
          </NButton>
          <NButton size="large" @click="restart">
            <template #icon>
              <div class="i-carbon-reset" />
            </template>
            分析新影像
          </NButton>
        </NSpace>
      </template>

      <!-- 失败状态 -->
      <template v-else-if="inferenceStore.status === INFERENCE_STATUS.FAILED">
        <NAlert type="error" title="处理失败" class="mb-4">
          {{ inferenceStore.error || '未知错误' }}
        </NAlert>

        <div class="text-center">
          <NButton type="primary" @click="restart">
            重新上传
          </NButton>
        </div>
      </template>
    </NCard>

    <!-- 功能介绍 -->
    <NGrid :cols="3" :x-gap="16">
      <NGi>
        <NCard>
          <div class="text-center">
            <div class="i-carbon-machine-learning-model text-3xl text-blue-500 mb-3" />
            <h3 class="font-bold mb-2">深度学习模型</h3>
            <p class="text-gray-500 text-sm">
              基于 nnU-Net 架构，在 KiTS19 数据集上训练
            </p>
          </div>
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <div class="text-center">
            <div class="i-carbon-cube text-3xl text-green-500 mb-3" />
            <h3 class="font-bold mb-2">3D 可视化</h3>
            <p class="text-gray-500 text-sm">
              支持 3D 体渲染和多平面重建视图
            </p>
          </div>
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <div class="text-center">
            <div class="i-carbon-analytics text-3xl text-orange-500 mb-3" />
            <h3 class="font-bold mb-2">定量分析</h3>
            <p class="text-gray-500 text-sm">
              自动计算肾脏和肿瘤体积
            </p>
          </div>
        </NCard>
      </NGi>
    </NGrid>
  </div>
</template>
