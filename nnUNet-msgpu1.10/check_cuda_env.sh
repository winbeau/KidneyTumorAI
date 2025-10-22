#!/bin/bash
# CUDA 环境诊断脚本

echo "=========================================="
echo "CUDA 环境诊断工具"
echo "=========================================="
echo ""

# 1. 检查 GPU
echo "1️⃣  检查 GPU"
echo "----------------------------------------"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.used --format=table
    echo "✅ GPU 检测正常"
else
    echo "❌ nvidia-smi 命令未找到"
fi
echo ""

# 2. 检查 CUDA 版本
echo "2️⃣  检查 CUDA 版本"
echo "----------------------------------------"
if command -v nvcc &> /dev/null; then
    nvcc --version | grep "release"
    echo "✅ CUDA 工具包已安装"
else
    echo "⚠️  nvcc 命令未找到 (可能只安装了运行时)"
fi
echo ""

# 3. 检查关键库文件
echo "3️⃣  检查关键库文件"
echo "----------------------------------------"

# libcuda.so (NVIDIA 驱动)
echo "📦 libcuda.so (NVIDIA 驱动):"
libcuda_paths=$(find /usr -name "libcuda.so" 2>/dev/null)
if [ -n "$libcuda_paths" ]; then
    echo "$libcuda_paths" | while read path; do
        echo "   ✅ $path"
    done
else
    echo "   ❌ 未找到"
fi

# libcudnn (cuDNN)
echo ""
echo "📦 libcudnn*.so (cuDNN):"
libcudnn_paths=$(find /usr -name "libcudnn*.so.8" 2>/dev/null | head -5)
if [ -n "$libcudnn_paths" ]; then
    echo "$libcudnn_paths" | while read path; do
        echo "   ✅ $path"
    done
else
    echo "   ❌ 未找到"
fi
echo ""

# 4. 检查环境变量
echo "4️⃣  检查环境变量"
echo "----------------------------------------"
echo "CUDA_HOME: ${CUDA_HOME:-未设置}"
echo "LD_LIBRARY_PATH:"
if [ -n "$LD_LIBRARY_PATH" ]; then
    echo "$LD_LIBRARY_PATH" | tr ':' '\n' | sed 's/^/   /'
else
    echo "   未设置"
fi
echo ""

# 5. WSL2 特殊检查
echo "5️⃣  WSL2 特殊检查"
echo "----------------------------------------"
if grep -qi microsoft /proc/version; then
    echo "✅ 运行在 WSL2 环境"
    if [ -d "/usr/lib/wsl/lib" ]; then
        echo "✅ WSL CUDA 库目录存在: /usr/lib/wsl/lib"
        ls -lh /usr/lib/wsl/lib/libcuda.so* 2>/dev/null | sed 's/^/   /'
    else
        echo "❌ WSL CUDA 库目录不存在"
    fi
else
    echo "ℹ️  非 WSL2 环境"
fi
echo ""

# 6. Python 环境检查
echo "6️⃣  Python 环境检查"
echo "----------------------------------------"
python_version=$(python --version 2>&1)
echo "Python 版本: $python_version"

echo ""
echo "MindSpore 版本:"
python -c "import mindspore; print(f'   {mindspore.__version__}')" 2>/dev/null || echo "   ❌ MindSpore 未安装"

echo ""
echo "CUDA 可用性 (MindSpore):"
python -c "
import mindspore as ms
from mindspore import context
try:
    context.set_context(mode=context.GRAPH_MODE, device_target='GPU', device_id=0)
    print('   ✅ GPU 设备可用')
except Exception as e:
    print(f'   ❌ GPU 不可用: {e}')
" 2>&1
echo ""

# 7. 诊断建议
echo "=========================================="
echo "诊断建议"
echo "=========================================="

needs_fix=false

# 检查 LD_LIBRARY_PATH 是否包含 WSL 路径
if grep -qi microsoft /proc/version; then
    if ! echo "$LD_LIBRARY_PATH" | grep -q "/usr/lib/wsl/lib"; then
        echo "⚠️  WSL2 环境缺少 /usr/lib/wsl/lib 在 LD_LIBRARY_PATH 中"
        needs_fix=true
    fi
fi

# 检查 libcuda.so
if [ -z "$libcuda_paths" ]; then
    echo "❌ 未找到 libcuda.so - 请检查 NVIDIA 驱动安装"
    needs_fix=true
fi

# 检查 libcudnn
if [ -z "$libcudnn_paths" ]; then
    echo "❌ 未找到 libcudnn - 请安装 cuDNN"
    needs_fix=true
fi

if [ "$needs_fix" = true ]; then
    echo ""
    echo "🔧 建议修复步骤:"
    echo "   1. 运行: source setup_cuda_env.sh"
    echo "   2. 重新测试: bash check_cuda_env.sh"
    echo "   3. 启动训练: python train.py ..."
else
    echo "✅ 环境配置正常，可以开始训练！"
fi

echo ""
echo "=========================================="
