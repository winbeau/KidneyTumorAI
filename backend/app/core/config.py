"""
KidneyTumorAI 后端配置
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # 项目路径
    base_dir: Path = Path(__file__).parent.parent.parent
    nnunet_root: Path = Path("/home/winbeau/Projects/KidneyTumorAI/nnUNet-msgpu1.10")
    model_path: Path = Path("/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1")

    # 数据目录
    upload_dir: Path = Path("/home/winbeau/Projects/KidneyTumorAI/backend/data/uploads")
    result_dir: Path = Path("/home/winbeau/Projects/KidneyTumorAI/backend/data/results")
    temp_dir: Path = Path("/home/winbeau/Projects/KidneyTumorAI/backend/data/temp")

    # nnU-Net 环境变量
    nnunet_raw_data_base: str = "/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/nnUNet_raw_data_base"
    nnunet_preprocessed: str = "/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/nnUNet_preprocessed"
    results_folder: str = "/home/winbeau/Projects/KidneyTumorAI/nnUNet_data/RESULTS_FOLDER"

    # 数据库
    database_url: str = "sqlite:///./data/kidney_tumor.db"

    # 推理配置
    default_fold: int = 0
    default_model: str = "3d_fullres"
    task_name: str = "Task001_kits"
    trainer_class: str = "nnUNetTrainerV2"
    plans_identifier: str = "nnUNetPlansv2.1"

    # 文件限制
    max_upload_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list = [".nii", ".nii.gz"]

    class Config:
        env_file = ".env"
        extra = "ignore"

    def setup_nnunet_env(self):
        """设置 nnU-Net 环境变量"""
        os.environ["nnUNet_raw_data_base"] = self.nnunet_raw_data_base
        os.environ["nnUNet_preprocessed"] = self.nnunet_preprocessed
        os.environ["RESULTS_FOLDER"] = self.results_folder

    def ensure_dirs(self):
        """确保必要目录存在"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    settings.setup_nnunet_env()
    settings.ensure_dirs()
    return settings
