#!/bin/bash

# 这个脚本用于初始化 nnU-Net 所需的环境变量。
# 请使用 'source' 命令来执行它，以确保环境变量在您当前的终端会话中生效。
#
# 正确用法:
# source setup_paths.sh
#
# 错误用法 (环境变量不会被保留):
# ./setup_paths.sh

# 获取脚本所在的目录，并将其作为项目根目录
# 这使得无论您从哪里调用此脚本，路径都是正确的
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# 在项目根目录下定义主数据文件夹
DATA_DIR="$PROJECT_ROOT/nnUNet_data"

# 1. 导出环境变量
echo "正在设置数据目录环境变量..."
export nnUNet_raw_data_base="$DATA_DIR/nnUNet_raw_data_base"
export nnUNet_preprocessed="$DATA_DIR/nnUNet_preprocessed"
export RESULTS_FOLDER="$DATA_DIR/RESULTS_FOLDER"
echo "环境变量设置成功!"
echo ""

# 2. 显示设置好的路径
echo "当前路径设置如下:"
echo ""
echo "  原始数据 (nnUNet_raw_data_base): $nnUNet_raw_data_base"
echo "  预处理数据 (nnUNet_preprocessed): $nnUNet_preprocessed"
echo "  模型结果 (RESULTS_FOLDER):      $RESULTS_FOLDER"
echo ""

# 3. 设置训练集、测试集数量
echo "正在设置训练集-测试集数量..."
export NUM_TRAIN=35
export NUM_TEST=15
echo "环境变量设置成功!"
echo ""

# 4. 显示当前训练集、测试集数量
echo "  训练集数量 (NUM_TRAIN): $NUM_TRAIN"
echo "  测试集数量 (NUM_TEST): $NUM_TEST"
echo ""
echo "现在您可以在这个终端会话中运行 nnU-Net 命令了。"
