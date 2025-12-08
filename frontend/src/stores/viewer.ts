import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'
import { Niivue } from '@niivue/niivue'
import { SLICE_TYPES } from '@/utils/constants'

export const useViewerStore = defineStore('viewer', () => {
  // NiiVue 实例
  const nv = shallowRef<Niivue | null>(null)

  // 视图状态
  const sliceType = ref<typeof SLICE_TYPES[keyof typeof SLICE_TYPES]>(SLICE_TYPES.MULTIPLANAR)
  const overlayVisible = ref(true)
  const overlayOpacity = ref(0.6)

  // 当前切片索引
  const sliceIndices = ref<{ axial: number; coronal: number; sagittal: number }>({
    axial: 0,
    coronal: 0,
    sagittal: 0,
  })

  // 体积维度
  const dimensions = ref<{ x: number; y: number; z: number }>({ x: 0, y: 0, z: 0 })

  // 加载状态
  const isLoading = ref(false)
  const loadError = ref<string | null>(null)
  const downloadProgress = ref<{ original: number; segmentation: number }>({ original: 0, segmentation: 0 })
  const objectUrls = ref<string[]>([])

  // 渐进式加载状态
  const isPreviewMode = ref(false)
  const isLoadingFullRes = ref(false)

  // 初始化 NiiVue
  async function initNiiVue(canvas: HTMLCanvasElement) {
    try {
      nv.value = new Niivue({
        backColor: [0.1, 0.1, 0.15, 1],
        show3Dcrosshair: true,
        crosshairColor: [0, 1, 0, 0.5],
        crosshairWidth: 1,
      })

      await nv.value.attachToCanvas(canvas)
      nv.value.setSliceType(SLICE_TYPES.MULTIPLANAR)
    } catch (e: any) {
      console.error('NiiVue init error:', e)
      loadError.value = '初始化查看器失败'
      throw e
    }
  }

  async function fetchNiftiWithProgress(url: string, key: 'original' | 'segmentation'): Promise<ArrayBuffer> {
    const resp = await fetch(url)
    if (!resp.ok || !resp.body) {
      throw new Error(`下载失败: ${resp.status} ${resp.statusText}`)
    }
    const reader = resp.body.getReader()
    const total = Number(resp.headers.get('Content-Length') || 0)
    const chunks: Uint8Array[] = []
    let received = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      if (value) {
        chunks.push(value)
        received += value.length
        if (total > 0) {
          downloadProgress.value[key] = Math.min(100, Math.round((received / total) * 100))
        }
      }
    }

    const size = chunks.reduce((acc, c) => acc + c.length, 0)
    const buffer = new Uint8Array(size)
    let offset = 0
    for (const c of chunks) {
      buffer.set(c, offset)
      offset += c.length
    }
    downloadProgress.value[key] = 100
    return buffer.buffer
  }

  // 渐进式加载：先预览后高清
  async function loadCase(originalUrl: string, segmentationUrl: string) {
    if (!nv.value) throw new Error('NiiVue not initialized')
    isLoading.value = true
    loadError.value = null
    downloadProgress.value = { original: 0, segmentation: 0 }
    isPreviewMode.value = false
    isLoadingFullRes.value = false

    // 清理旧的 object URLs
    objectUrls.value.forEach((u) => URL.revokeObjectURL(u))
    objectUrls.value = []

    try {
      // 构建预览 URL（添加 preview=true 参数）
      const previewOriginalUrl = `${originalUrl}${originalUrl.includes('?') ? '&' : '?'}preview=true&factor=4`
      const previewSegUrl = `${segmentationUrl}${segmentationUrl.includes('?') ? '&' : '?'}preview=true&factor=4`

      // 第一阶段：快速加载预览版本
      console.log('加载预览版本...')
      const [previewOrigBuffer, previewSegBuffer] = await Promise.all([
        fetchNiftiWithProgress(previewOriginalUrl, 'original'),
        fetchNiftiWithProgress(previewSegUrl, 'segmentation'),
      ])

      const previewOrigUrlObj = URL.createObjectURL(new Blob([previewOrigBuffer]))
      const previewSegUrlObj = URL.createObjectURL(new Blob([previewSegBuffer]))
      objectUrls.value = [previewOrigUrlObj, previewSegUrlObj]

      const previewVolumes: any[] = [
        { url: previewOrigUrlObj },
        { url: previewSegUrlObj, colormap: 'actc', opacity: overlayOpacity.value },
      ]

      await nv.value.loadVolumes(previewVolumes)
      isPreviewMode.value = true
      isLoading.value = false

      // 获取维度信息（预览版本也可以获取）
      const vol = nv.value.volumes[0]
      if (vol) {
        const [, x = 0, y = 0, z = 0] = vol.dims
        // 预览版本维度需要乘以 factor 来获取真实维度
        dimensions.value = { x: x * 4, y: y * 4, z: z * 4 }
        sliceIndices.value = {
          axial: Math.floor((z * 4) / 2),
          coronal: Math.floor((y * 4) / 2),
          sagittal: Math.floor((x * 4) / 2),
        }
      }

      // 第二阶段：后台加载高分辨率版本
      console.log('后台加载高分辨率版本...')
      isLoadingFullRes.value = true

      // 使用 requestIdleCallback 或 setTimeout 延迟加载，避免阻塞 UI
      await new Promise(resolve => setTimeout(resolve, 100))

      const [fullOrigBuffer, fullSegBuffer] = await Promise.all([
        fetchNiftiWithProgress(originalUrl, 'original'),
        fetchNiftiWithProgress(segmentationUrl, 'segmentation'),
      ])

      // 创建新的 Blob URLs
      const fullOrigUrlObj = URL.createObjectURL(new Blob([fullOrigBuffer]))
      const fullSegUrlObj = URL.createObjectURL(new Blob([fullSegBuffer]))

      // 清理预览版本的 URLs
      objectUrls.value.forEach((u) => URL.revokeObjectURL(u))
      objectUrls.value = [fullOrigUrlObj, fullSegUrlObj]

      const fullVolumes: any[] = [
        { url: fullOrigUrlObj },
        { url: fullSegUrlObj, colormap: 'actc', opacity: overlayOpacity.value },
      ]

      // 替换为高分辨率版本
      await nv.value.loadVolumes(fullVolumes)

      // 更新真实维度
      const fullVol = nv.value.volumes[0]
      if (fullVol) {
        const [, x = 0, y = 0, z = 0] = fullVol.dims
        dimensions.value = { x, y, z }
        sliceIndices.value = {
          axial: Math.floor(z / 2),
          coronal: Math.floor(y / 2),
          sagittal: Math.floor(x / 2),
        }
      }

      isPreviewMode.value = false
      isLoadingFullRes.value = false
      console.log('高分辨率版本加载完成')

    } catch (e: any) {
      loadError.value = '加载影像失败: ' + e.message
      isLoading.value = false
      isLoadingFullRes.value = false
      throw e
    }
  }

  // 设置视图类型
  function setSliceType(type: typeof SLICE_TYPES[keyof typeof SLICE_TYPES]) {
    if (!nv.value) return
    sliceType.value = type
    nv.value.setSliceType(type)
  }

  // 设置叠加层透明度
  function setOverlayOpacity(opacity: number) {
    overlayOpacity.value = opacity
    if (nv.value && nv.value.volumes.length > 1) {
      nv.value.setOpacity(1, opacity)
    }
  }

  // 切换叠加层显示
  function toggleOverlay(visible?: boolean) {
    overlayVisible.value = visible ?? !overlayVisible.value
    if (nv.value && nv.value.volumes.length > 1) {
      nv.value.setOpacity(1, overlayVisible.value ? overlayOpacity.value : 0)
    }
  }

  // 截图
  async function takeScreenshot(): Promise<Blob> {
    if (!nv.value) throw new Error('NiiVue not initialized')

    return new Promise((resolve, reject) => {
      try {
        const canvas = nv.value!.canvas
        canvas.toBlob((blob) => {
          if (blob) resolve(blob)
          else reject(new Error('截图失败'))
        }, 'image/png')
      } catch (e) {
        reject(e)
      }
    })
  }

  // 重置视图
  function resetView() {
    if (!nv.value) return
    nv.value.setSliceType(SLICE_TYPES.MULTIPLANAR)
    sliceType.value = SLICE_TYPES.MULTIPLANAR
  }

  // 销毁
  function destroy() {
    if (nv.value) {
      nv.value = null
    }
    objectUrls.value.forEach((u) => URL.revokeObjectURL(u))
    objectUrls.value = []
    isPreviewMode.value = false
    isLoadingFullRes.value = false
  }

  return {
    nv,
    sliceType,
    overlayVisible,
    overlayOpacity,
    sliceIndices,
    dimensions,
    isLoading,
    loadError,
    downloadProgress,
    isPreviewMode,
    isLoadingFullRes,
    initNiiVue,
    loadCase,
    setSliceType,
    setOverlayOpacity,
    toggleOverlay,
    takeScreenshot,
    resetView,
    destroy,
  }
})
