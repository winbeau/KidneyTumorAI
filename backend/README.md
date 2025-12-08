# KidneyTumorAI 后端

基于 FastAPI 的肾脏肿瘤 AI 分割系统后端服务。

## 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者使用已有的 conda 环境
conda activate ms-gpu
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件，确认路径配置正确：

```bash
# 模型路径
MODEL_PATH=/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1

# nnU-Net 环境变量
nnUNet_raw_data_base=/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/nnUNet_raw_data_base
nnUNet_preprocessed=/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/nnUNet_preprocessed
RESULTS_FOLDER=/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER
```

### 4. 启动服务

```bash
python run.py
# 或者
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API 接口

### 推理接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/inference/start` | 上传文件并开始推理 |
| GET | `/api/v1/inference/{task_id}/status` | 查询推理状态 |
| GET | `/api/v1/inference/{task_id}/result` | 获取推理结果 |
| DELETE | `/api/v1/inference/{task_id}` | 取消/删除任务 |

### 历史记录接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/history` | 获取历史记录列表 |
| GET | `/api/v1/history/{record_id}` | 获取单条记录 |
| DELETE | `/api/v1/history/{record_id}` | 删除记录 |
| POST | `/api/v1/history/batch-delete` | 批量删除 |

### 文件下载

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/files/{task_id}/original.nii.gz` | 下载原始影像 |
| GET | `/files/{task_id}/segmentation.nii.gz` | 下载分割结果 |

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── inference.py  # 推理接口
│   │   ├── history.py    # 历史记录接口
│   │   └── files.py      # 文件下载接口
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   └── database.py   # 数据库连接
│   ├── models/           # 数据模型
│   │   └── task.py       # 任务模型
│   ├── schemas/          # Pydantic schemas
│   │   └── inference.py  # 请求/响应模型
│   ├── services/         # 业务逻辑
│   │   └── inference.py  # 推理服务
│   └── main.py           # FastAPI 应用入口
├── data/                 # 数据目录
│   ├── uploads/          # 上传文件
│   ├── results/          # 推理结果
│   └── temp/             # 临时文件
├── requirements.txt      # Python 依赖
├── .env                  # 环境配置
 └── run.py               # 启动脚本
```

## 注意事项

1. **GPU 环境**: 推理需要 CUDA 环境，确保 MindSpore GPU 版本正确安装
2. **单进程运行**: MindSpore GPU 不支持多进程，workers 必须设为 1
3. **内存需求**: 推理大文件时需要充足的 GPU 显存和系统内存
4. **大文件上传**: 后端默认放开到 1GB，如果前面有 Nginx/反向代理需要同步调大，例如在 `http` 或 `server` 块中增加 `client_max_body_size 1g;`，参考 `docs/nginx.conf.example`
