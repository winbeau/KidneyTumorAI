#!/bin/bash
# CUDA Environment Setup for WSL2 + MindSpore Training
# 修复 libcuda.so 找不到的问题

echo "=================================================="
echo "设置 CUDA 环境变量"
echo "=================================================="

# WSL2 CUDA 库路径 (最重要!)
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH

# CUDA 11.6 路径
export CUDA_HOME=/usr/local/cuda-11.6
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export PATH=$CUDA_HOME/bin:$PATH

# cuDNN 路径 (已包含在 CUDA_HOME/lib64)
# export CUDNN_HOME=$CUDA_HOME

# MindSpore 相关环境变量
export GLOG_v=2
export GLOG_logtostderr=1

# 显示配置的路径
echo "✅ LD_LIBRARY_PATH 已更新:"
echo "   $LD_LIBRARY_PATH"
echo ""
echo "✅ CUDA_HOME: $CUDA_HOME"
echo "✅ PATH: $PATH"
echo ""

# 验证关键库文件
echo "=================================================="
echo "验证关键库文件"
echo "=================================================="

if [ -f "/usr/lib/wsl/lib/libcuda.so" ]; then
    echo "✅ libcuda.so 找到"
else
    echo "❌ libcuda.so 未找到"
fi

if [ -f "$CUDA_HOME/lib64/libcudnn_cnn_infer.so.8" ]; then
    echo "✅ libcudnn_cnn_infer.so.8 找到"
else
    echo "❌ libcudnn_cnn_infer.so.8 未找到"
fi

echo ""
echo "=================================================="
echo "GPU 状态"
echo "=================================================="
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

echo ""
echo "=================================================="
echo "环境配置完成 ✅"
echo "=================================================="
echo ""
echo "使用方法:"
echo "  source setup_cuda_env.sh"
echo "  python train.py 3d_fullres nnUNetTrainerV2 Task001_kits 0"
echo ""
