"""
KidneyTumorAI 后端配置
"""
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# 仓库根目录和后端目录
BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = BASE_DIR / "backend"
MODEL_STORE_DIR = BASE_DIR / "models"


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # 项目路径
    base_dir: Path = BASE_DIR
    backend_dir: Path = BACKEND_DIR
    model_store_dir: Path = MODEL_STORE_DIR
    nnunet_root: Path = BASE_DIR / "nnUNet-msgpu1.10"
    model_path: Path = (
        MODEL_STORE_DIR
        / "nnUNet"
        / "3d_fullres"
        / "Task001_kits"
        / "nnUNetTrainerV2__nnUNetPlansv2.1"
    )

    # 数据目录
    upload_dir: Path = BACKEND_DIR / "data" / "uploads"
    result_dir: Path = BACKEND_DIR / "data" / "results"
    temp_dir: Path = BACKEND_DIR / "data" / "temp"

    # nnU-Net 环境变量
    nnunet_raw_data_base: str = str(BASE_DIR / "nnUNet_data" / "nnUNet_raw_data_base")
    nnunet_preprocessed: str = str(BASE_DIR / "nnUNet_data" / "nnUNet_preprocessed")
    results_folder: str = str(MODEL_STORE_DIR)

    # 数据库
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'kidney_tumor.db').as_posix()}"

    # 推理配置
    default_fold: int = 0
    default_model: str = "3d_fullres"
    task_name: str = "Task001_kits"
    trainer_class: str = "nnUNetTrainerV2"
    plans_identifier: str = "nnUNetPlansv2.1"
    default_checkpoint: str = "auto"  # auto -> 优先 model_best，缺失则用 model_final_checkpoint

    # 文件限制
    max_upload_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list = [".nii", ".nii.gz"]

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        extra = "ignore"

    def apply_model_path_overrides(self):
        """从模型路径推导结果目录和模型元信息，减少手工配置"""
        try:
            model_path_obj = Path(self.model_path)
            if not model_path_obj.is_absolute():
                model_path_obj = (self.base_dir / model_path_obj).resolve()
                self.model_path = model_path_obj

            # 如果配置的模型路径不存在，尝试已知候选（models/..., 旧 RESULTS_FOLDER/...）
            if not model_path_obj.exists():
                candidates = [
                    model_path_obj,
                    MODEL_STORE_DIR
                    / "nnUNet"
                    / "3d_fullres"
                    / "Task001_kits"
                    / "nnUNetTrainerV2__nnUNetPlansv2.1",
                    BASE_DIR
                    / "nnUNet_data"
                    / "RESULTS_FOLDER"
                    / "nnUNet"
                    / "3d_fullres"
                    / "Task001_kits"
                    / "nnUNetTrainerV2__nnUNetPlansv2.1",
                ]
                for candidate in candidates:
                    if Path(candidate).exists():
                        model_path_obj = Path(candidate)
                        self.model_path = model_path_obj
                        break

            parts = list(model_path_obj.parts)
            if "nnUNet" not in parts:
                return

            nnunet_idx = parts.index("nnUNet")
            # 期望结构: .../RESULTS_FOLDER/nnUNet/<model>/<task>/<trainer__plans>
            if len(parts) > nnunet_idx + 1:
                self.default_model = parts[nnunet_idx + 1]
            if len(parts) > nnunet_idx + 2:
                self.task_name = parts[nnunet_idx + 2]
            if len(parts) > nnunet_idx + 3:
                trainer_plans = parts[nnunet_idx + 3]
                if "__" in trainer_plans:
                    trainer, plans = trainer_plans.split("__", 1)
                    self.trainer_class = trainer
                    self.plans_identifier = plans

            # 解析 RESULTS_FOLDER: /.../RESULTS_FOLDER/nnUNet/<model>/<task>/<trainer__plans>
            # parents[3] -> .../RESULTS_FOLDER
            if len(model_path_obj.parents) >= 4:
                self.results_folder = str(model_path_obj.parents[3])
        except Exception:
            # 容错：任何异常都不影响默认配置
            pass

    def resolve_all_paths(self):
        """将相对路径转为基于 base_dir 的绝对路径"""
        def _resolve_path(value: Path) -> Path:
            return value if value.is_absolute() else (self.base_dir / value).resolve()

        def _resolve_str(value: str) -> str:
            p = Path(value)
            return str(p if p.is_absolute() else (self.base_dir / p).resolve())

        self.base_dir = Path(self.base_dir).resolve()
        self.backend_dir = _resolve_path(Path(self.backend_dir))
        self.model_store_dir = _resolve_path(Path(self.model_store_dir))
        self.nnunet_root = _resolve_path(Path(self.nnunet_root))
        self.model_path = _resolve_path(Path(self.model_path))
        self.upload_dir = _resolve_path(Path(self.upload_dir))
        self.result_dir = _resolve_path(Path(self.result_dir))
        self.temp_dir = _resolve_path(Path(self.temp_dir))
        self.results_folder = _resolve_str(self.results_folder)
        self.nnunet_raw_data_base = _resolve_str(self.nnunet_raw_data_base)
        self.nnunet_preprocessed = _resolve_str(self.nnunet_preprocessed)

    def setup_nnunet_env(self):
        """设置 nnU-Net 环境变量"""
        os.environ["nnUNet_raw_data_base"] = str(self.nnunet_raw_data_base)
        os.environ["nnUNet_preprocessed"] = str(self.nnunet_preprocessed)
        os.environ["RESULTS_FOLDER"] = str(self.results_folder)

    def ensure_dirs(self):
        """确保必要目录存在"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.model_store_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    settings.resolve_all_paths()
    settings.apply_model_path_overrides()
    settings.setup_nnunet_env()
    settings.ensure_dirs()
    return settings
