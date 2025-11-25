// NiiVue 类型扩展
declare module '@niivue/niivue' {
  export class Niivue {
    constructor(options?: NiivueOptions)
    canvas: HTMLCanvasElement
    volumes: NVImage[]
    attachToCanvas(canvas: HTMLCanvasElement): Promise<void>
    loadVolumes(volumes: NVVolumeOptions[]): Promise<void>
    setSliceType(type: number): void
    setOpacity(volumeIndex: number, opacity: number): void
    setColormap(volumeIndex: number, colormap: string): void
  }

  export interface NiivueOptions {
    backColor?: number[]
    show3Dcrosshair?: boolean
    crosshairColor?: number[]
    crosshairWidth?: number
  }

  export interface NVVolumeOptions {
    url: string
    colormap?: string
    opacity?: number
  }

  export interface NVImage {
    dims: number[]
    pixDims: number[]
  }
}
