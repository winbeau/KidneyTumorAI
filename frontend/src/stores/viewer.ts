import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'
import { Niivue } from '@niivue/niivue'
import { SLICE_TYPES, SEGMENTATION_COLORS } from '@/utils/constants'

export const useViewerStore = defineStore('viewer', () => {
  // NiiVue 实例
  const nv = shallowRef<Niivue | null>(null)

  // 视图状态
  const sliceType = ref(SLICE_TYPES.MULTIPLANAR)
  const overlayVisible = ref(true)
  const overlayOpacity = ref(0.6)

  // 当前切片索引
  const sliceIndices = ref({
    axial: 0,
    coronal: 0,
    sagittal: 0,
  })

  // 体积维度
  const dimensions = ref({ x: 0, y: 0, z: 0 })

  // 加载状态
  const isLoading = ref(false)
  const loadError = ref<string | null>(null)

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

  // 加载原始影像
  async function loadVolume(url: string) {
    if (!nv.value) throw new Error('NiiVue not initialized')

    isLoading.value = true
    loadError.value = null

    try {
      await nv.value.loadVolumes([{ url }])

      // 获取维度信息
      const vol = nv.value.volumes[0]
      if (vol) {
        dimensions.value = {
          x: vol.dims[1],
          y: vol.dims[2],
          z: vol.dims[3],
        }
        // 设置初始切片为中间位置
        sliceIndices.value = {
          axial: Math.floor(vol.dims[3] / 2),
          coronal: Math.floor(vol.dims[2] / 2),
          sagittal: Math.floor(vol.dims[1] / 2),
        }
      }
    } catch (e: any) {
      loadError.value = '加载影像失败: ' + e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 加载分割叠加层
  async function loadOverlay(url: string) {
    if (!nv.value) throw new Error('NiiVue not initialized')

    try {
      await nv.value.loadVolumes([{
        url,
        colormap: 'actc', // 使用内置 colormap，后续可自定义
        opacity: overlayOpacity.value,
      }])
    } catch (e: any) {
      console.error('Load overlay error:', e)
      throw e
    }
  }

  // 设置视图类型
  function setSliceType(type: number) {
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
    initNiiVue,
    loadVolume,
    loadOverlay,
    setSliceType,
    setOverlayOpacity,
    toggleOverlay,
    takeScreenshot,
    resetView,
    destroy,
  }
})
