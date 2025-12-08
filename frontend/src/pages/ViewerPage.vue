<script setup lang="ts">
import { NCard, NButton, NButtonGroup, NSlider, NSwitch, NSpace, NSpin, NAlert } from 'naive-ui'
import { useRoute } from 'vue-router'
import { useViewerStore } from '@/stores/viewer'
import { SLICE_TYPES, SEGMENTATION_COLORS } from '@/utils/constants'
import { getInferenceResult } from '@/api/inference'
import type { StatsInfo } from '@/api/types'

const route = useRoute()
const viewerStore = useViewerStore()

// Canvas 引用
const canvasRef = ref<HTMLCanvasElement | null>(null)

// 加载状态
const isInitializing = ref(true)
const initError = ref<string | null>(null)

// 统计信息
const stats = ref<StatsInfo | null>(null)

// 初始化
onMounted(async () => {
  if (!canvasRef.value) return

  try {
    await viewerStore.initNiiVue(canvasRef.value)

    // 如果有 taskId，加载结果
    const taskId = route.params.taskId as string
    if (taskId) {
      const result = await getInferenceResult(taskId)
      stats.value = result.stats

      // 加载原始影像和分割结果
      await viewerStore.loadCase(result.originalUrl, result.segmentationUrl)
    }

    isInitializing.value = false
  } catch (e: any) {
    initError.value = e.message || '初始化失败'
    isInitializing.value = false
  }
})

// 清理
onUnmounted(() => {
  viewerStore.destroy()
})

// 视图切换
const viewOptions = [
  { label: '多平面', value: SLICE_TYPES.MULTIPLANAR, icon: 'i-carbon-grid' },
  { label: '横断面', value: SLICE_TYPES.AXIAL, icon: 'i-carbon-subtract-alt' },
  { label: '冠状面', value: SLICE_TYPES.CORONAL, icon: 'i-carbon-subtract-alt' },
  { label: '矢状面', value: SLICE_TYPES.SAGITTAL, icon: 'i-carbon-subtract-alt' },
  { label: '3D', value: SLICE_TYPES.RENDER, icon: 'i-carbon-cube' },
]

// 格式化体积
const formatVolume = (mm3?: number) => {
  if (mm3 === undefined || mm3 === null) return '-'
  if (mm3 > 1000000) {
    return `${(mm3 / 1000000).toFixed(2)} cm³`
  }
  return `${mm3.toFixed(0)} mm³`
}

// 截图下载
const downloadScreenshot = async () => {
  try {
    const blob = await viewerStore.takeScreenshot()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `kidney-tumor-${Date.now()}.png`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Screenshot error:', e)
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- 工具栏 -->
    <NCard size="small" class="mb-4">
      <div class="flex-between">
        <!-- 视图切换 -->
        <NButtonGroup>
          <NButton
            v-for="opt in viewOptions"
            :key="opt.value"
            :type="viewerStore.sliceType === opt.value ? 'primary' : 'default'"
            :strong="viewerStore.sliceType === opt.value"
            @click="viewerStore.setSliceType(opt.value)"
          >
            <template #icon>
              <div :class="opt.icon" />
            </template>
            {{ opt.label }}
          </NButton>
        </NButtonGroup>

        <!-- 控制选项 -->
        <NSpace align="center">
          <!-- 叠加层控制 -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">分割叠加</span>
            <NSwitch
              :value="viewerStore.overlayVisible"
              @update:value="viewerStore.toggleOverlay"
            />
          </div>

          <!-- 透明度 -->
          <div class="flex items-center gap-2 w-40">
            <span class="text-sm text-gray-500">透明度</span>
            <NSlider
              :value="viewerStore.overlayOpacity * 100"
              :min="0"
              :max="100"
              :step="5"
              :disabled="!viewerStore.overlayVisible"
              @update:value="(v: number) => viewerStore.setOverlayOpacity(v / 100)"
            />
          </div>

          <!-- 截图 -->
          <NButton type="primary" strong @click="downloadScreenshot">
            <template #icon>
              <div class="i-carbon-camera" />
            </template>
            截图
          </NButton>
        </NSpace>
      </div>
    </NCard>

    <!-- 主内容区 -->
    <div class="flex-1 flex gap-4">
      <!-- 查看器 -->
      <div class="flex-1">
        <NCard class="h-full" content-style="height: 100%; padding: 0;">
          <div class="niivue-container h-full relative">
            <!-- 加载中 -->
            <div v-if="isInitializing" class="absolute inset-0 flex-center bg-gray-900">
              <div class="space-y-3 text-center text-gray-200">
                <NSpin size="large" />
                <div class="text-sm">下载影像中...</div>
                <div class="text-xs">
                  原始 {{ viewerStore.downloadProgress.original }}% / 分割 {{ viewerStore.downloadProgress.segmentation }}%
                </div>
              </div>
            </div>

            <!-- 错误提示 -->
            <NAlert v-else-if="initError" type="error" class="m-4">
              {{ initError }}
            </NAlert>

            <!-- Canvas -->
            <canvas ref="canvasRef" class="w-full h-full" />
          </div>
        </NCard>
      </div>

      <!-- 信息面板 -->
      <div class="w-64 flex flex-col gap-4">
        <!-- 颜色图例 -->
        <NCard title="分割图例" size="small">
          <div class="space-y-2">
            <div
              v-for="(info, label) in SEGMENTATION_COLORS"
              :key="label"
              class="flex items-center gap-2"
            >
              <div
                class="w-4 h-4 rounded"
                :style="{ backgroundColor: info.color === 'transparent' ? '#666' : info.color }"
              />
              <span>{{ info.name }}</span>
            </div>
          </div>
        </NCard>

        <!-- 统计信息 -->
        <NCard v-if="stats" title="分析结果" size="small">
          <div class="space-y-3">
            <div>
              <div class="text-gray-500 text-sm">肾脏体积</div>
              <div class="text-lg font-bold text-kidney">
                {{ formatVolume(stats.kidneyVolume) }}
              </div>
            </div>
            <div>
              <div class="text-gray-500 text-sm">肿瘤体积</div>
              <div class="text-lg font-bold text-tumor">
                {{ formatVolume(stats.tumorVolume) }}
              </div>
            </div>
            <div>
              <div class="text-gray-500 text-sm">肿瘤/肾脏比例</div>
              <div class="text-lg font-bold">
                {{ stats?.kidneyVolume && stats?.tumorVolume
                  ? ((stats.tumorVolume / stats.kidneyVolume) * 100).toFixed(1) + '%'
                  : '-' }}
              </div>
            </div>
          </div>
        </NCard>

        <!-- 维度信息 -->
        <NCard v-if="viewerStore.dimensions.x > 0" title="影像信息" size="small">
          <div class="space-y-1 text-sm">
            <div class="flex-between">
              <span class="text-gray-500">尺寸</span>
              <span>{{ viewerStore.dimensions.x }} × {{ viewerStore.dimensions.y }} × {{ viewerStore.dimensions.z }}</span>
            </div>
          </div>
        </NCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-kidney {
  color: var(--kidney-color);
}
.text-tumor {
  color: var(--tumor-color);
}
</style>
