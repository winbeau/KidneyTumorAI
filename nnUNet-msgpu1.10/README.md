# MindSpore GPU 版 KidneyTumorAI nnU-Net

基于 MindSpore 的 nnU-Net 分支，面向肾肿瘤分割任务。本文档整合环境配置、数据预处理与训练流程，帮助你快速完成项目搭建、KiTS19 数据准备以及模型训练与评估。

## 快速上手

```bash
# 1）创建并激活 Conda 环境
conda create -n ms-gpu python=3.9 -y
conda activate ms-gpu

# 2）配置 Conda 镜像（建议开启）
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/
conda config --set show_channel_urls yes

# 3）配置 pip 镜像（建议开启）
mkdir -p ~/.pip
cat > ~/.pip/pip.conf <<'EOF'
[global]
index-url = https://pypi.org/simple
extra-index-url =
    https://pypi.tuna.tsinghua.edu.cn/simple
    https://mirrors.ustc.edu.cn/pypi/web/simple
    https://mirrors.aliyun.com/pypi/simple
    https://pypi.mirrors.ustc.edu.cn/simple
timeout = 60
retries = 3

[install]
trusted-host =
    pypi.org
    pypi.tuna.tsinghua.edu.cn
    mirrors.ustc.edu.cn
    mirrors.aliyun.com
    pypi.mirrors.ustc.edu.cn
EOF

# 4）安装依赖
pip install -r requirements.txt
conda install cudatoolkit=11.6 -y

# 5）安装 cuDNN 8.4.1（CUDA 11.6 对应版本[首先确保当前 cuda-11.6!!]）
cd ~
tar -xJvf cudnn-linux-x86_64-8.4.1.50_cuda11.6-archive.tar.xz
cd cudnn-linux-x86_64-8.4.1.50_cuda11.6-archive
sudo mv include/* /usr/local/cuda-11.6/include/
sudo mv lib/libcudnn* /usr/local/cuda-11.6/lib64/

# 6）验证 MindSpore GPU 环境
python -c "import mindspore as ms; ms.set_context(device_target='GPU'); print('√ device:', ms.get_context('device_target'))"

# 7）检测 CUDA 环境(可选)
./check_cuda_env.sh
```

## 数据集准备（KiTS19）

1. 下载 KiTS19 影像数据（注意 /path/to 路径!）：
   ```bash
   cd /path/to/KidneyTumorAI/nnUNet-msgpu1.10/  # 切换到 nnUNet 目录
   python ../gh-kits19/starter_code/get_imaging.py
   ```
2. 确认数据已解压到 `KidneyTumorAI/gh-kits19/data/`。
3. 每次开启新的终端后加载路径配置：
   ```bash
   source setup_paths.sh
   ```
   该脚本会导出 `nnUNet_raw_data_base`、`nnUNet_preprocessed`、`RESULTS_FOLDER` 等变量，所有中间产物与模型文件会写入 `nnUNet_data/` 目录，避免污染仓库。

## 数据转换与预处理

1. 创建原始数据目录、重采样数据、并将 KiTS19 转换为 nnU-Net Decathlon 规范：
   ```bash
   mkdir -p "$nnUNet_raw_data_base/nnUNet_raw_data/Task01_kits"
   python src/nnunet/experiment_planning/nnUNet_convert_decathlon_task.py \
     -r ../gh-kits19/data \
     -i "$nnUNet_raw_data_base/nnUNet_raw_data/Task01_kits"
   ```
   脚本会自动执行 4D 拆分、补充 `_0000` 模态后缀，并确保任务目录名称规范。如果需要小样本调试，可通过环境变量 `NUM_TRAIN` 与 `NUM_TEST` 覆盖默认的 210/90 拆分。

2. 剪切、预处理数据：
   ```bash
   python src/nnunet/experiment_planning/nnUNet_plan_and_preprocess.py -t 1 -pl2d None
   ```

## 训练与评估

- **训练**（以 3D full-resolution 管线为例）：
  ```bash
  python train.py 3d_fullres nnUNetTrainerV2 Task001_kits 0
  ```
  根据需要替换任务 ID 或训练器类名，若仅验证现有模型可添加 `--validation_only`。

- **评估** 已预处理的体数据[暂未尝试😂]：
  ```bash
  python eval.py \
    -i <输入 NIfTI 目录> \
    -o <输出目录> \
    -t Task01_kits \
    -m 3d_fullres
  ```

训练产生的模型权重与中间文件默认写入 `$RESULTS_FOLDER`（位于 `nnUNet_data/`），请勿将原始医学影像或权重提交到 Git 仓库。

## 故障排查清单

- `pip config list` 应显示主 PyPI 源与备用镜像。
- `./check_cuda_env.sh` 用于确认驱动、CUDA 与 cuDNN 版本满足 MindSpore 要求。
- MindSpore GPU 上下文测试应打印 `√ device: GPU`；若失败，请检查 CUDA、cuDNN 路径或驱动版本。
- 每次在新终端使用项目前务必 `source setup_paths.sh`，以便 nnU-Net 正确读取原始、预处理与结果目录。

## 参考资源

- `setup_env_vars.sh`、`setup_paths.sh`：部署到新机器时快速导出环境变量。
- `src/nnunet/`：训练、预处理与推理的核心代码。
- `train.py`、`eval.py`：MindSpore 训练与评估入口脚本。
