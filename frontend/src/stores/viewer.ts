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

  // 并行加载原始影像与分割
  async function loadCase(originalUrl: string, segmentationUrl: string) {
    if (!nv.value) throw new Error('NiiVue not initialized')
    isLoading.value = true
    loadError.value = null
    downloadProgress.value = { original: 0, segmentation: 0 }

    try {
      const [origBuffer, segBuffer] = await Promise.all([
        fetchNiftiWithProgress(originalUrl, 'original'),
        fetchNiftiWithProgress(segmentationUrl, 'segmentation'),
      ])

      const volumes: any[] = [
        { url: originalUrl, data: origBuffer },
        { url: segmentationUrl, data: segBuffer, colormap: 'actc', opacity: overlayOpacity.value },
      ]

      await nv.value.loadVolumes(volumes)

      // 获取维度信息
      const vol = nv.value.volumes[0]
      if (vol) {
        const [, x = 0, y = 0, z = 0] = vol.dims
        dimensions.value = { x, y, z }
        sliceIndices.value = {
          axial: Math.floor(z / 2),
          coronal: Math.floor(y / 2),
          sagittal: Math.floor(x / 2),
        }
      }
    } catch (e: any) {
      loadError.value = '加载影像失败: ' + e.message
      throw e
    } finally {
      isLoading.value = false
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
