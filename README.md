# KidneyTumorAI

<div align="center">

![MindSpore](https://img.shields.io/badge/MindSpore-1.10-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-orange.svg)

**基于 MindSpore GPU 和 nnU-Net 的肾脏肿瘤智能分割系统**

[功能特性](#功能特性) • [快速开始](#快速开始) • [安装指南](#安装指南) • [使用说明](#使用说明) • [API文档](#api-文档)

</div>

---

## 项目简介

KidneyTumorAI 是一个面向 [KiTS19 肾脏肿瘤分割挑战赛](https://kits19.grand-challenge.org/) 的全栈医学影像分析平台。项目将 nnU-Net 深度学习框架移植到华为 MindSpore GPU 平台，实现了从 CT 影像上传、AI 自动分割到 3D 可视化的完整工作流程。

### 核心亮点

- **国产化深度学习框架**：基于华为 MindSpore 1.10 GPU 版本，完整移植 nnU-Net 训练和推理流程
- **端到端解决方案**：现代化 Web 前端 + RESTful API 后端 + 深度学习推理引擎
- **专业医学可视化**：集成 NiiVue 实现多视图 3D 医学影像渲染
- **量化分析能力**：自动计算肾脏和肿瘤体积，辅助临床决策

## 功能特性

### 前端功能
- 拖拽上传 NIfTI 格式医学影像文件
- 实时显示推理进度和状态
- 多视图 3D 医学影像可视化（轴状位、冠状位、矢状位、3D 渲染）
- 分割结果叠加显示与颜色编码
- 肾脏/肿瘤体积统计展示
- 历史记录管理与批量操作

### 后端功能
- RESTful API 接口，支持 OpenAPI 文档
- 异步任务队列处理长时间推理任务
- SQLite 数据库持久化任务历史
- 自动体积计算（基于体素尺寸）
- 完善的文件管理和错误处理

### 深度学习功能
- 3D U-Net 编码器-解码器架构
- 深度监督（Deep Supervision）多尺度损失
- 混合精度训练（FP16）提升效率
- 多 GPU 分布式训练支持
- 5 折交叉验证集成预测
- 滑动窗口推理处理大体积数据

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **前端** | Vue 3 | 3.5.x | 渐进式 JavaScript 框架 |
| | TypeScript | 5.9.x | 类型安全的 JavaScript |
| | Vite | 7.x | 下一代前端构建工具 |
| | Naive UI | 2.43.x | Vue 3 组件库 |
| | Pinia | 3.0.x | Vue 状态管理 |
| | NiiVue | 0.65.x | WebGL 医学影像查看器 |
| | UnoCSS | 66.x | 原子化 CSS 引擎 |
| **后端** | FastAPI | 0.109+ | 高性能 Python Web 框架 |
| | SQLAlchemy | 2.0+ | Python ORM 框架 |
| | Uvicorn | 0.27+ | ASGI 服务器 |
| | nibabel | 5.2+ | NIfTI 文件读写库 |
| **深度学习** | MindSpore | 1.10 | 华为深度学习框架 |
| | nnU-Net | - | 医学图像分割框架 |
| | CUDA | 11.6 | NVIDIA GPU 计算平台 |
| | cuDNN | 8.4.1 | GPU 深度学习加速库 |

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户浏览器                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  文件上传   │  │  3D 可视化  │  │  历史记录   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI 后端服务                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API 路由层                             │   │
│  │  /api/v1/inference  │  /api/v1/history  │  /files        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    服务层                                 │   │
│  │  InferenceService: 任务管理、推理调度、体积计算           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    数据层                                 │   │
│  │  SQLAlchemy ORM  │  SQLite  │  文件系统                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ subprocess
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MindSpore GPU 推理引擎                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  nnU-Net 3D U-Net  │  滑动窗口推理  │  后处理             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  预训练模型: Task001_kits (肾脏肿瘤分割)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- **操作系统**: Ubuntu 18.04+ / Windows WSL2
- **GPU**: NVIDIA GPU (建议显存 ≥ 8GB)
- **CUDA**: 11.6
- **cuDNN**: 8.4.1
- **Python**: 3.9+
- **Node.js**: 16+

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/KidneyTumorAI.git
cd KidneyTumorAI

# 2. 创建 Python 环境
conda create -n kidney-ai python=3.9 -y
conda activate kidney-ai

# 3. 安装后端依赖
pip install -r backend/requirements.txt

# 4. 安装前端依赖
cd frontend && pnpm install && cd ..

# 5. 配置环境变量
source nnUNet-msgpu1.10/setup_paths.sh

# 6. 启动服务
# 终端 1: 启动后端
cd backend && python run.py

# 终端 2: 启动前端
cd frontend && pnpm dev
```

访问 http://localhost:3000 即可使用系统。

## 安装指南

### 1. 安装 CUDA 和 cuDNN

```bash
# 安装 CUDA 11.6
# 从 NVIDIA 官网下载对应版本

# 通过 conda 安装 cudatoolkit
conda install cudatoolkit=11.6 -c conda-forge

# cuDNN 8.4.1 需要手动安装
# 下载地址: https://developer.nvidia.com/cudnn
```

### 2. 安装 MindSpore GPU

```bash
pip install mindspore-gpu==1.10.0

# 验证安装
python -c "import mindspore as ms; ms.set_context(device_target='GPU'); print('MindSpore GPU 安装成功!')"
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt 内容：**
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
aiosqlite>=0.19.0
pydantic>=2.5.3
pydantic-settings>=2.1.0
nibabel>=5.2.0
numpy>=1.24.3
python-multipart>=0.0.6
python-dotenv>=1.0.0
```

### 4. 安装前端依赖

```bash
cd frontend
pnpm install
# 或
npm install
```

### 5. 安装 nnU-Net 依赖

```bash
cd nnUNet-msgpu1.10
pip install -r requirements.txt
```

### 6. 配置环境变量

在每次使用前，需要配置 nnU-Net 路径：

```bash
source nnUNet-msgpu1.10/setup_paths.sh
```

或手动设置：

```bash
export nnUNet_raw_data_base="/path/to/KidneyTumorAI/nnUNet_data/nnUNet_raw_data_base"
export nnUNet_preprocessed="/path/to/KidneyTumorAI/nnUNet_data/nnUNet_preprocessed"
export RESULTS_FOLDER="/path/to/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER"
```

## 使用说明

### 启动服务

**启动后端服务：**
```bash
cd backend
python run.py
# 服务运行在 http://localhost:8000
# API 文档: http://localhost:8000/docs
```

**启动前端服务：**
```bash
cd frontend
pnpm dev
# 服务运行在 http://localhost:3000
```

### 执行推理

1. 打开浏览器访问 http://localhost:3000
2. 在首页上传 NIfTI 格式的 CT 影像文件（.nii 或 .nii.gz）
3. 等待 AI 推理完成（进度实时显示）
4. 查看分割结果和体积统计
5. 在「影像查看」页面进行 3D 可视化浏览

### 训练模型

如需从头训练模型：

```bash
cd nnUNet-msgpu1.10
source setup_paths.sh

# 1. 下载 KiTS19 数据集
python ../gh-kits19/starter_code/get_imaging.py

# 2. 转换数据格式
python src/nnunet/experiment_planning/nnUNet_convert_decathlon_task.py \
  -r ../gh-kits19/data \
  -i "$nnUNet_raw_data_base/nnUNet_raw_data/Task01_kits"

# 3. 数据预处理
python src/nnunet/experiment_planning/nnUNet_plan_and_preprocess.py -t 1 -pl2d None

# 4. 开始训练 (5折交叉验证)
python train.py 3d_fullres nnUNetTrainerV2 Task001_kits 0  # fold 0
python train.py 3d_fullres nnUNetTrainerV2 Task001_kits 1  # fold 1
# ... 依此类推
```

### 单独执行推理

```bash
cd nnUNet-msgpu1.10
source setup_paths.sh

python eval.py \
  -i /path/to/input_nifti_folder \
  -o /path/to/output_folder \
  -t Task001_kits \
  -m 3d_fullres \
  -tr nnUNetTrainerV2 \
  -p nnUNetPlansv2.1 \
  -f 0 \
  -chk model_best \
  --disable_tta
```

## API 文档

### 推理接口

#### 开始推理
```http
POST /api/v1/inference/start
Content-Type: multipart/form-data

参数:
  - file: NIfTI 文件 (.nii 或 .nii.gz)
  - model: 模型类型 (默认: "3d_fullres")

响应:
{
  "taskId": "uuid-string",
  "status": "queued",
  "estimatedTime": 120
}
```

#### 查询状态
```http
GET /api/v1/inference/{task_id}/status

响应:
{
  "taskId": "uuid-string",
  "status": "processing",  // queued | processing | completed | failed
  "progress": 45,
  "message": "正在执行分割推理..."
}
```

#### 获取结果
```http
GET /api/v1/inference/{task_id}/result

响应:
{
  "taskId": "uuid-string",
  "originalUrl": "/files/{task_id}/original.nii.gz",
  "segmentationUrl": "/files/{task_id}/segmentation.nii.gz",
  "stats": {
    "kidneyVolume": 156000.5,   // 肾脏体积 (mm³)
    "tumorVolume": 28000.3,     // 肿瘤体积 (mm³)
    "processingTime": 145.8      // 处理时间 (秒)
  }
}
```

#### 删除任务
```http
DELETE /api/v1/inference/{task_id}

响应:
{
  "message": "任务已删除"
}
```

### 历史记录接口

#### 获取历史列表
```http
GET /api/v1/history?page=1&page_size=10

响应:
{
  "total": 25,
  "records": [
    {
      "id": "uuid-string",
      "filename": "case_00001.nii.gz",
      "status": "completed",
      "kidneyVolume": 156000.5,
      "tumorVolume": 28000.3,
      "createdAt": "2024-01-15T10:30:00Z",
      "completedAt": "2024-01-15T10:32:25Z"
    }
  ]
}
```

#### 批量删除
```http
POST /api/v1/history/batch-delete
Content-Type: application/json

请求体:
{
  "ids": ["uuid-1", "uuid-2", "uuid-3"]
}

响应:
{
  "message": "成功删除 3 条记录"
}
```

### 文件接口

#### 下载原始影像
```http
GET /files/{task_id}/original.nii.gz
```

#### 下载分割结果
```http
GET /files/{task_id}/segmentation.nii.gz
```

## 项目结构

```
KidneyTumorAI/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── main.py                  # 应用入口
│   │   ├── api/                     # API 路由
│   │   │   ├── inference.py         # 推理接口
│   │   │   ├── history.py           # 历史接口
│   │   │   └── files.py             # 文件接口
│   │   ├── core/
│   │   │   ├── config.py            # 配置管理
│   │   │   └── database.py          # 数据库初始化
│   │   ├── models/
│   │   │   └── task.py              # ORM 模型
│   │   ├── schemas/
│   │   │   └── inference.py         # Pydantic 模式
│   │   └── services/
│   │       └── inference.py         # 业务逻辑
│   ├── data/                        # 数据存储
│   ├── run.py                       # 启动脚本
│   └── requirements.txt
│
├── frontend/                         # Vue 3 前端
│   ├── src/
│   │   ├── api/                     # API 客户端
│   │   ├── components/              # Vue 组件
│   │   ├── pages/                   # 页面组件
│   │   │   ├── HomePage.vue         # 上传页面
│   │   │   ├── ViewerPage.vue       # 3D 可视化
│   │   │   ├── HistoryPage.vue      # 历史记录
│   │   │   └── AboutPage.vue        # 关于页面
│   │   ├── stores/                  # Pinia 状态
│   │   ├── router/                  # 路由配置
│   │   └── main.ts                  # 入口文件
│   ├── package.json
│   └── vite.config.ts
│
├── nnUNet-msgpu1.10/                 # MindSpore nnU-Net
│   ├── src/nnunet/
│   │   ├── training/                # 训练流程
│   │   │   ├── network_training/
│   │   │   │   └── nnUNetTrainerV2.py
│   │   │   ├── loss_functions/      # 损失函数
│   │   │   └── dataloading/         # 数据加载
│   │   ├── network_architecture/    # 网络架构
│   │   │   ├── generic_UNet.py      # 3D U-Net
│   │   │   └── neural_network.py
│   │   ├── preprocessing/           # 数据预处理
│   │   ├── inference/               # 推理流程
│   │   └── experiment_planning/     # 实验规划
│   ├── train.py                     # 训练入口
│   ├── eval.py                      # 推理入口
│   ├── setup_paths.sh               # 环境配置
│   └── requirements.txt
│
├── gh-kits19/                        # KiTS19 数据集工具
│   ├── starter_code/
│   │   ├── get_imaging.py           # 下载数据
│   │   └── visualize.py             # 可视化工具
│   └── data/                        # 数据集存储
│
├── nnUNet_data/                      # 数据目录 (不纳入版本控制)
│   ├── nnUNet_raw_data_base/        # 原始数据
│   ├── nnUNet_preprocessed/         # 预处理数据
│   └── RESULTS_FOLDER/              # 模型权重
│
├── docs/                             # 文档
├── README.md                         # 项目说明
├── CLAUDE.md                         # 开发指南
└── .gitignore
```

## 分割标签说明

| 标签值 | 含义 | 可视化颜色 |
|--------|------|-----------|
| 0 | 背景 | 透明 |
| 1 | 肾脏 | 红色 (#E74C3C) |
| 2 | 肿瘤 | 蓝色 (#3498DB) |

## 性能指标

在 KiTS19 验证集上的分割性能：

| 指标 | 肾脏 | 肿瘤 |
|------|------|------|
| Dice 系数 | ~0.97 | ~0.82 |
| 表面距离 (mm) | ~1.2 | ~3.5 |

**推理性能：**
- GPU: NVIDIA RTX 4060 (8GB)
- 单例推理时间: ~2-3 分钟
- 支持的最大体积: 512×512×512 体素

## 常见问题

### Q: 推理时出现 GPU 显存不足 (OOM) 错误？

A: 尝试以下解决方案：
1. 重启系统清理 GPU 显存碎片
2. 关闭其他占用 GPU 的程序
3. 添加 `--disable_tta` 参数禁用测试时增强
4. 使用较小的输入图像

### Q: 环境变量未设置导致路径错误？

A: 每次打开新终端时，需要执行：
```bash
source nnUNet-msgpu1.10/setup_paths.sh
```

### Q: 前端无法连接后端？

A: 检查：
1. 后端服务是否运行在 8000 端口
2. 前端 vite.config.ts 中的代理配置是否正确
3. 防火墙是否允许本地端口通信

### Q: 如何使用自己的训练数据？

A: 参考 KiTS19 数据格式，将数据组织为：
```
Task0XX_YourTask/
├── imagesTr/
│   ├── case_00000_0000.nii.gz
│   └── ...
├── labelsTr/
│   ├── case_00000.nii.gz
│   └── ...
└── dataset.json
```

## 致谢

- [nnU-Net](https://github.com/MIC-DKFZ/nnUNet) - 医学图像分割框架
- [MindSpore](https://www.mindspore.cn/) - 华为深度学习框架
- [KiTS19](https://kits19.grand-challenge.org/) - 肾脏肿瘤分割挑战赛
- [NiiVue](https://github.com/niivue/niivue) - WebGL 医学影像查看器
- [Naive UI](https://www.naiveui.com/) - Vue 3 组件库

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

<div align="center">

**如果这个项目对你有帮助，请给一个 Star ⭐**

</div>
