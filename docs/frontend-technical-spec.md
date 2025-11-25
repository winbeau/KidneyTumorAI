# KidneyTumorAI 前端技术文档

## 1. 项目概述

### 1.1 项目目标
为 KidneyTumorAI 肾脏肿瘤分割系统构建一个功能完整的 Web 前端，实现医学影像上传、AI 推理、3D/2D 可视化、历史记录管理等功能。

### 1.2 核心功能
| 功能模块 | 描述 |
|---------|------|
| 影像上传 | 支持 NIfTI (.nii.gz) 格式的 CT 影像上传 |
| AI 推理 | 调用后端 nnU-Net 模型进行肾脏/肿瘤分割 |
| 3D 可视化 | 3D 体渲染展示原始影像和分割结果 |
| 2D 切片浏览 | 横断面/矢状面/冠状面三视图切片浏览 |
| 结果叠加 | 在原始影像上叠加分割掩码（肾脏/肿瘤着色） |
| 历史记录 | 管理和查看历史分析记录 |
| 结果导出 | 下载分割结果 NIfTI 文件和分析报告 |

---

## 2. 技术栈选型

### 2.1 核心框架
```yaml
框架: Vue 3.4+
语言: TypeScript 5.x
构建工具: Vite 5.x
包管理器: pnpm
```

### 2.2 主要依赖

| 类别 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| UI 框架 | Naive UI | ^2.38 | TypeScript 友好、现代设计、Tree-shaking 支持好 |
| 状态管理 | Pinia | ^2.1 | Vue 3 官方推荐、TypeScript 原生支持 |
| 路由 | Vue Router | ^4.3 | Vue 3 标准路由方案 |
| HTTP 客户端 | Axios | ^1.6 | 成熟稳定、拦截器机制完善 |
| 医学影像可视化 | NiiVue | ^0.40 | 原生支持 NIfTI、3D/2D 一体化、WebGL2 渲染 |
| 图表 | ECharts | ^5.5 | 用于统计分析图表 |
| 样式方案 | UnoCSS | ^0.58 | 原子化 CSS、构建性能优秀 |
| 图标 | Iconify | ^3.1 | 统一图标方案 |

### 2.3 为什么选择 NiiVue？

NiiVue 是专为神经影像设计的 WebGL2 可视化库，相比其他方案有以下优势：

| 对比项 | NiiVue | VTK.js | Cornerstone.js |
|-------|--------|--------|----------------|
| NIfTI 原生支持 | ✅ 原生 | ❌ 需转换 | ❌ 需插件 |
| 3D 体渲染 | ✅ 内置 | ✅ 强大 | ❌ 需扩展 |
| 2D MPR 视图 | ✅ 内置 | ⚠️ 复杂 | ✅ 擅长 |
| 分割叠加 | ✅ 原生 | ✅ 支持 | ✅ 支持 |
| 包体积 | 较小 | 很大 | 中等 |
| 学习曲线 | 低 | 高 | 中 |

---

## 3. 项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # API 接口层
│   │   ├── index.ts            # Axios 实例配置
│   │   ├── inference.ts        # 推理相关接口
│   │   ├── history.ts          # 历史记录接口
│   │   └── types.ts            # API 类型定义
│   │
│   ├── assets/                 # 静态资源
│   │   ├── styles/
│   │   │   ├── variables.css   # CSS 变量
│   │   │   └── global.css      # 全局样式
│   │   └── images/
│   │
│   ├── components/             # 通用组件
│   │   ├── common/             # 基础组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── LoadingOverlay.vue
│   │   │
│   │   └── viewer/             # 影像查看器组件
│   │       ├── NiiVueViewer.vue      # NiiVue 封装
│   │       ├── ViewerToolbar.vue     # 工具栏
│   │       ├── SliceNavigator.vue    # 切片导航
│   │       ├── ColorLegend.vue       # 分割颜色图例
│   │       └── VolumeControls.vue    # 3D渲染控制
│   │
│   ├── composables/            # 组合式函数
│   │   ├── useNiiVue.ts        # NiiVue 初始化与控制
│   │   ├── useInference.ts     # 推理流程管理
│   │   ├── useHistory.ts       # 历史记录管理
│   │   └── useNotification.ts  # 消息通知
│   │
│   ├── layouts/                # 布局组件
│   │   └── DefaultLayout.vue
│   │
│   ├── pages/                  # 页面视图
│   │   ├── HomePage.vue        # 首页/上传页
│   │   ├── ViewerPage.vue      # 影像查看器页
│   │   ├── HistoryPage.vue     # 历史记录页
│   │   └── AboutPage.vue       # 关于页面
│   │
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   │
│   ├── stores/                 # Pinia 状态管理
│   │   ├── viewer.ts           # 查看器状态
│   │   ├── inference.ts        # 推理状态
│   │   └── history.ts          # 历史状态
│   │
│   ├── types/                  # TypeScript 类型
│   │   ├── viewer.d.ts
│   │   ├── inference.d.ts
│   │   └── niivue.d.ts         # NiiVue 类型扩展
│   │
│   ├── utils/                  # 工具函数
│   │   ├── file.ts             # 文件处理
│   │   ├── format.ts           # 格式化
│   │   └── constants.ts        # 常量定义
│   │
│   ├── App.vue
│   └── main.ts
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── uno.config.ts
├── package.json
└── README.md
```

---

## 4. 核心模块设计

### 4.1 影像查看器模块

#### 4.1.1 NiiVue 封装 (composables/useNiiVue.ts)

```typescript
// 核心功能接口
interface UseNiiVue {
  // 初始化
  init(canvas: HTMLCanvasElement): Promise<void>

  // 加载影像
  loadVolume(url: string | File): Promise<void>
  loadOverlay(url: string | File, colormap?: string): Promise<void>

  // 视图控制
  setSliceType(type: 'axial' | 'coronal' | 'sagittal' | 'render'): void
  setSliceIndex(axis: number, index: number): void

  // 3D 渲染控制
  setRenderMode(mode: 'volume' | 'mip' | 'surface'): void
  setOpacity(value: number): void

  // 分割叠加控制
  setOverlayOpacity(value: number): void
  toggleOverlay(visible: boolean): void

  // 窗宽窗位
  setWindowLevel(window: number, level: number): void

  // 截图
  takeScreenshot(): Promise<Blob>
}
```

#### 4.1.2 视图布局

```
┌─────────────────────────────────────────────────────────────┐
│                        工具栏 Toolbar                        │
├───────────────────┬───────────────────┬─────────────────────┤
│                   │                   │                     │
│   横断面 Axial    │   矢状面 Sagittal │    冠状面 Coronal   │
│                   │                   │                     │
├───────────────────┴───────────────────┴─────────────────────┤
│                                                             │
│                      3D 体渲染 Volume                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  图例：█ 肾脏 (红色)  █ 肿瘤 (蓝色)    不透明度: ████░░ 70% │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 推理流程模块

#### 4.2.1 状态机设计

```typescript
type InferenceState =
  | 'idle'           // 空闲
  | 'uploading'      // 上传中
  | 'queued'         // 排队中
  | 'processing'     // 处理中
  | 'completed'      // 完成
  | 'failed'         // 失败

interface InferenceStore {
  state: InferenceState
  progress: number           // 0-100
  currentFile: File | null
  taskId: string | null
  result: InferenceResult | null
  error: string | null

  // Actions
  startInference(file: File): Promise<void>
  cancelInference(): void
  pollStatus(): Promise<void>
  reset(): void
}
```

#### 4.2.2 推理流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  选择文件 │ -> │  上传中   │ -> │  处理中   │ -> │  查看结果 │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │              │                │               │
     v              v                v               v
  验证格式      显示进度条      轮询状态        加载可视化
  (.nii.gz)    (上传进度)     (每2秒)        (原图+掩码)
```

### 4.3 历史记录模块

```typescript
interface HistoryRecord {
  id: string
  filename: string
  uploadTime: Date
  status: 'completed' | 'failed'

  // 分割统计
  stats?: {
    kidneyVolume: number      // 肾脏体积 (mm³)
    tumorVolume: number       // 肿瘤体积 (mm³)
    tumorKidneyRatio: number  // 肿瘤/肾脏比例
  }

  // 文件引用
  originalUrl: string
  segmentationUrl: string
  thumbnailUrl: string
}
```

---

## 5. API 接口设计

### 5.1 后端 API 规范

```yaml
Base URL: /api/v1

认证: 暂不需要 (内网使用)
格式: JSON (文件上传使用 multipart/form-data)
```

### 5.2 接口列表

#### 上传并开始推理
```http
POST /inference/start
Content-Type: multipart/form-data

Request:
  - file: NIfTI 文件 (.nii.gz)
  - model: 模型选择 (默认 "3d_fullres")

Response: 201 Created
{
  "taskId": "uuid-string",
  "status": "queued",
  "estimatedTime": 120  // 预估秒数
}
```

#### 查询推理状态
```http
GET /inference/{taskId}/status

Response: 200 OK
{
  "taskId": "uuid-string",
  "status": "processing" | "completed" | "failed",
  "progress": 65,
  "message": "正在进行分割推理..."
}
```

#### 获取推理结果
```http
GET /inference/{taskId}/result

Response: 200 OK
{
  "taskId": "uuid-string",
  "originalUrl": "/files/{taskId}/original.nii.gz",
  "segmentationUrl": "/files/{taskId}/segmentation.nii.gz",
  "stats": {
    "kidneyVolume": 185234.5,
    "tumorVolume": 12456.8,
    "processingTime": 98.5
  }
}
```

#### 获取历史记录列表
```http
GET /history?page=1&pageSize=20

Response: 200 OK
{
  "total": 45,
  "records": [...]
}
```

#### 删除历史记录
```http
DELETE /history/{recordId}

Response: 204 No Content
```

---

## 6. 分割颜色方案

### 6.1 标签映射
```typescript
const SEGMENTATION_COLORS = {
  0: { name: '背景', color: 'transparent' },
  1: { name: '肾脏', color: '#E74C3C', opacity: 0.6 },  // 红色
  2: { name: '肿瘤', color: '#3498DB', opacity: 0.8 },  // 蓝色
} as const
```

### 6.2 NiiVue 颜色表配置
```typescript
// 自定义 colormap 用于分割叠加
const kidneyTumorColormap = {
  R: [0, 231, 52],    // 背景、肾脏、肿瘤 的 R 值
  G: [0, 76, 152],    // G 值
  B: [0, 60, 219],    // B 值
  A: [0, 153, 204],   // Alpha 值
  I: [0, 1, 2]        // 索引
}
```

---

## 7. 响应式设计

### 7.1 断点定义
```css
/* UnoCSS 断点配置 */
sm: 640px   /* 手机横屏 */
md: 768px   /* 平板 */
lg: 1024px  /* 小笔记本 */
xl: 1280px  /* 桌面 */
2xl: 1536px /* 大屏 */
```

### 7.2 布局适配策略

| 屏幕 | 2D 视图布局 | 3D 视图 |
|------|------------|---------|
| < md | 单视图切换 | 隐藏 |
| md-lg | 2x2 网格 | 底部折叠 |
| >= xl | 1+3 布局 | 右侧面板 |

---

## 8. 性能优化策略

### 8.1 影像加载优化
- **流式加载**: 大文件使用 chunked 上传
- **Web Worker**: NIfTI 解析在 Worker 中进行
- **缓存策略**: 使用 IndexedDB 缓存已加载影像

### 8.2 渲染优化
- **WebGL2**: NiiVue 默认使用 WebGL2 硬件加速
- **LOD**: 3D 渲染时根据性能动态调整质量
- **懒加载**: 非当前视图的切片延迟渲染

### 8.3 构建优化
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'niivue': ['@niivue/niivue'],
          'naive-ui': ['naive-ui'],
          'echarts': ['echarts'],
        }
      }
    }
  }
})
```

---

## 9. 开发规范

### 9.1 命名约定
```yaml
组件: PascalCase (ViewerToolbar.vue)
composables: camelCase + use 前缀 (useNiiVue.ts)
stores: camelCase (viewer.ts)
类型: PascalCase + 描述性后缀 (InferenceState, ViewerConfig)
常量: UPPER_SNAKE_CASE (SEGMENTATION_COLORS)
```

### 9.2 Git 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 样式调整
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建/工具变更
```

### 9.3 代码风格
- ESLint: `@antfu/eslint-config`
- 组件使用 `<script setup lang="ts">`
- Props 使用 `defineProps` 配合 TypeScript 类型
- 优先使用组合式函数封装复用逻辑

---

## 10. 部署方案

### 10.1 开发环境
```bash
# 启动开发服务器
pnpm dev

# 代理配置 (vite.config.ts)
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    },
    '/files': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 10.2 生产环境
```bash
# 构建
pnpm build

# 输出目录
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   ├── niivue-[hash].js
│   └── ...
```

### 10.3 Docker 部署
```dockerfile
# 前端 Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## 11. 后续扩展规划

### Phase 2 功能
- [ ] 用户认证系统
- [ ] 批量上传处理
- [ ] 分割结果手动修正工具
- [ ] DICOM 格式支持
- [ ] 测量工具 (距离、面积、体积)

### Phase 3 功能
- [ ] 多模型对比
- [ ] AI 解释可视化 (Grad-CAM)
- [ ] 报告生成 (PDF)
- [ ] PACS 系统集成

---

## 12. 参考资源

- [Vue 3 官方文档](https://vuejs.org/)
- [Naive UI 组件库](https://www.naiveui.com/)
- [NiiVue 文档](https://github.com/niivue/niivue)
- [NiiVue Vue 示例](https://github.com/niivue/niivue-vue)
- [Vite 官方文档](https://vitejs.dev/)
- [UnoCSS 文档](https://unocss.dev/)
