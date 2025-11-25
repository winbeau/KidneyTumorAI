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

# 1. 创建 nnU-Net 需要的目录结构
echo "正在创建目录..."
mkdir -p "$DATA_DIR/nnUNet_raw_data_base"
mkdir -p "$DATA_DIR/nnUNet_preprocessed"
mkdir -p "$DATA_DIR/RESULTS_FOLDER"
echo "目录创建完成。"
echo ""
