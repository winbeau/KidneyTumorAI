# 模型存放说明

- 目录位置：`models/`（已随仓库创建）。
- 建议结构：`models/nnUNet/<架构>/<任务名>/<Trainer__Plans>`。
- 示例：
  - `models/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.ckpt`
  - 同目录可存放 `model_final_checkpoint.ckpt`。

使用方式：
- `backend/.env` 设置 `MODEL_PATH` 指向具体模型目录（上例中的 `.../nnUNetTrainerV2__nnUNetPlansv2.1`）。
- 后端会自动推导 `RESULTS_FOLDER`、模型架构、Task、Trainer、Plans，并设置 nnU-Net 环境变量，无需再手动 `source setup_paths.sh`。

提示：若已存在旧权重在 `nnUNet_data/RESULTS_FOLDER/...`，可将该目录移动或拷贝到 `models/nnUNet/...`，或在 `.env` 直接指向旧路径。
