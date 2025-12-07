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

MODEL_PATH=/data/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1
NNUNET_ROOT=/data/KidneyTumorAI/nnUNet-msgpu1.10
NNUNET_RAW_DATA_BASE=/data/KidneyTumorAI/nnUNet_data/nnUNet_raw_data_base
NNUNET_PREPROCESSED=/data/KidneyTumorAI/nnUNet_data/nnUNet_preprocessed
RESULTS_FOLDER=/data/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER

UPLOAD_DIR=/data/KidneyTumorAI/backend/data/uploads
RESULT_DIR=/data/KidneyTumorAI/backend/data/results
TEMP_DIR=/data/KidneyTumorAI/backend/data/temp
DATABASE_URL=sqlite:////data/KidneyTumorAI/backend/data/kidney_tumor.db
```
说明：后端会自动创建 `uploads/results/temp` 目录，并将 nnU-Net 所需环境变量写入当前进程。

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
