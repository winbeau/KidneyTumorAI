# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KidneyTumorAI is a kidney and tumor segmentation project combining MindSpore GPU with nnU-Net for the KiTS19 challenge. The project has two main components:
- `gh-kits19/`: KiTS19 dataset utilities (data download, visualization, evaluation)
- `nnUNet-msgpu1.10/`: MindSpore GPU port of nnU-Net for training and inference

## Environment Setup

```bash
# Create conda environment
conda create -n ms-gpu python=3.9 -y
conda activate ms-gpu

# Install dependencies
pip install -r nnUNet-msgpu1.10/requirements.txt
conda install cudatoolkit=11.6 -y

# Verify MindSpore GPU
python -c "import mindspore as ms; ms.set_context(device_target='GPU'); print('device:', ms.get_context('device_target'))"
```

**Required**: CUDA 11.6 + cuDNN 8.4.1

## Path Configuration

**Critical**: Run this in every new terminal session before any nnU-Net operations:
```bash
source nnUNet-msgpu1.10/setup_paths.sh
```

This exports required environment variables:
- `nnUNet_raw_data_base`: Raw data location
- `nnUNet_preprocessed`: Preprocessed data location
- `RESULTS_FOLDER`: Model weights and training outputs

All data stored in `nnUNet_data/` directory (not tracked in git).

## Common Commands

### Download KiTS19 Data
```bash
cd nnUNet-msgpu1.10
python ../gh-kits19/starter_code/get_imaging.py
```

### Convert KiTS19 to nnU-Net Format
```bash
mkdir -p "$nnUNet_raw_data_base/nnUNet_raw_data/Task01_kits"
python src/nnunet/experiment_planning/nnUNet_convert_decathlon_task.py \
  -r ../gh-kits19/data \
  -i "$nnUNet_raw_data_base/nnUNet_raw_data/Task01_kits"
```

Use `NUM_TRAIN` and `NUM_TEST` env vars for small sample debugging (default: 210/90).

### Preprocess Data
```bash
python src/nnunet/experiment_planning/nnUNet_plan_and_preprocess.py -t 1 -pl2d None
```

### Training
```bash
python train.py 3d_fullres nnUNetTrainerV2 Task001_kits <fold>
# fold: 0-4 for 5-fold CV, or 'all'
# Add --validation_only to validate existing model
```

### Inference
```bash
python eval.py \
  -i <input_nifti_dir> \
  -o <output_dir> \
  -t Task01_kits \
  -m 3d_fullres
```

## Architecture

### Network Architecture (`src/nnunet/network_architecture/`)
- `generic_UNet.py`: Core 3D U-Net implementation with deep supervision
- `neural_network.py`: Base segmentation network class
- Uses MindSpore's `nn.Conv3d`, `nn.BatchNorm3d`, `nn.LeakyReLU`

### Training Pipeline (`src/nnunet/training/`)
- `network_training/nnUNetTrainerV2.py`: Main trainer with:
  - `CustomTrainOneStepCell`: Custom training step with loss scaling (1024.0)
  - `WithLossCell` / `WithEvalCell`: Training and evaluation wrappers
  - Deep supervision with 5 output scales
  - Poly learning rate decay over 1000 epochs
  - Adam optimizer with weight decay 0.0005
- `loss_functions/`: Dice loss + cross-entropy with deep supervision
- `data_augmentation/`: 3D augmentation pipeline (rotation, scaling, no elastic)

### Data Processing
- `experiment_planning/`: Dataset conversion and experiment planning
- `preprocessing/`: Cropping, resampling, normalization
- `inference/predict.py`: Sliding window inference with test-time augmentation

### Key Classes
- `nnUNetTrainerV2`: Primary trainer (extends `nnUNetTrainer`)
- `Generic_UNet`: Encoder-decoder with skip connections and deep supervision
- `MultipleOutputLoss2`: Deep supervision loss aggregation

## Segmentation Labels
- 0: Background
- 1: Kidney
- 2: Tumor

## Multi-GPU Training
Set environment variables:
```bash
export DEVICE_ID=<gpu_id>
export RANK_SIZE=<num_gpus>  # >1 enables distributed training
```

## Troubleshooting
- If `nnUNet_raw_data_base is not defined`: Run `source setup_paths.sh`
- CUDA stream errors: Code has retry mechanism built-in
- MindSpore device errors: Verify CUDA/cuDNN versions match requirements
