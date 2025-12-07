# 后端快速启动指南（GPU 服务器）

## 场景说明
- GPU 服务器运行 FastAPI + nnU-Net 推理；CPU 服务器用 Nginx 提供前端，FRP 将公网流量转发到 GPU 服务器 `8000` 端口。
- 目标：最少操作启动后端，供前端/FRP 直接访问。

## 前置要求
- Python 3.9+、CUDA 11.6、cuDNN 8.4.1、MindSpore GPU 1.10 已安装。
- `nnUNet-msgpu1.10` 目录存在，`nnUNet_data` 下已放置模型权重（`RESULTS_FOLDER/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1`）。
- GPU 服务器放行本地 `8000` 端口；FRP 已可访问该端口。

## 一次性环境准备
```bash
git clone <repo-url> && cd KidneyTumorAI
conda create -n kidney-ai python=3.9 -y
conda activate kidney-ai
pip install -r backend/requirements.txt
```

## 配置环境变量（backend/.env）
将路径改成 GPU 服务器上的实际目录：
```env
DEBUG=false
HOST=0.0.0.0
PORT=8000

MODEL_PATH=models/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1
NNUNET_ROOT=nnUNet-msgpu1.10
NNUNET_RAW_DATA_BASE=nnUNet_data/nnUNet_raw_data_base
NNUNET_PREPROCESSED=nnUNet_data/nnUNet_preprocessed
RESULTS_FOLDER=models
DEFAULT_MODEL=3d_fullres
TASK_NAME=Task001_kits
TRAINER_CLASS=nnUNetTrainerV2
PLANS_IDENTIFIER=nnUNetPlansv2.1
DEFAULT_CHECKPOINT=auto  # auto -> 优先 model_best，缺失则用 model_final_checkpoint

UPLOAD_DIR=backend/data/uploads
RESULT_DIR=backend/data/results
TEMP_DIR=backend/data/temp
DATABASE_URL=sqlite:///./data/kidney_tumor.db
```
说明：仅需准确填写 `MODEL_PATH`，后端会自动：
- 推导 `RESULTS_FOLDER`/模型架构/Task/Trainer/Plans，并写入 nnU-Net 环境变量（无需再手动 `source setup_paths.sh`）。
- 自动选择 checkpoint（`DEFAULT_CHECKPOINT=auto` 时优先 `model_best`，缺失则用 `model_final_checkpoint`）。
- 创建 `uploads/results/temp` 目录。

建议将权重放到仓库根目录下的 `models/nnUNet/...`（已创建 `models/` 目录），或直接在 `.env` 指向现有权重位置。
迁移旧权重示例：
```bash
rsync -av nnUNet_data/RESULTS_FOLDER/nnUNet/ models/nnUNet/
```

## 启动命令
```bash
cd backend
python run.py  # 或 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --workers 1
```
- MindSpore GPU 仅支持单进程，保持 `workers=1`。
- 健康检查：`curl http://<GPU服务器IP或FRP域名>:8000/health`

## 与 FRP/Nginx 对接提示
- FRP 示例（TCP 转发）：  
  ```ini
  [backend_api]
  type = tcp
  local_ip = 127.0.0.1
  local_port = 8000
  remote_port = 8000
  ```
- 前端 Nginx/应用调用时，将 API Base URL 指向 FRP 暴露的地址（如 `http://<frp-host>:8000`）。
