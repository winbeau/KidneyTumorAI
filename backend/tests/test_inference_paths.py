import os
import sys
from pathlib import Path

# 确保后端根目录在 sys.path（放在依赖导入前）
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest

from app.core.config import Settings
from app.services.inference import InferenceService


def build_settings(tmp_path: Path, model_dir: Path) -> Settings:
    """构造隔离的 Settings，指向临时目录，避免写入真实路径。"""
    settings = Settings(
        base_dir=tmp_path,
        backend_dir=tmp_path / "backend",
        model_store_dir=tmp_path / "models",
        model_path=model_dir,
        results_folder=str(tmp_path / "models"),
        nnunet_root=tmp_path / "nnUNet-msgpu1.10",
        nnunet_raw_data_base=str(tmp_path / "nnUNet_data" / "nnUNet_raw_data_base"),
        nnunet_preprocessed=str(tmp_path / "nnUNet_data" / "nnUNet_preprocessed"),
        upload_dir=tmp_path / "uploads",
        result_dir=tmp_path / "results",
        temp_dir=tmp_path / "temp",
        default_checkpoint="auto",
    )
    settings.resolve_all_paths()
    settings.apply_model_path_overrides()
    settings.setup_nnunet_env()
    settings.ensure_dirs()
    return settings


def test_settings_apply_model_path_overrides(tmp_path, monkeypatch):
    model_dir = tmp_path / "models" / "nnUNet" / "3d_fullres" / "Task001_kits" / "nnUNetTrainerV2__nnUNetPlansv2.1"
    model_dir.mkdir(parents=True)

    settings = build_settings(tmp_path, model_dir)

    assert settings.default_model == "3d_fullres"
    assert settings.task_name == "Task001_kits"
    assert settings.trainer_class == "nnUNetTrainerV2"
    assert settings.plans_identifier == "nnUNetPlansv2.1"
    # parents[3] -> results folder (models)
    assert Path(settings.results_folder) == model_dir.parents[3]
    # 环境变量已写入
    assert os.environ["RESULTS_FOLDER"] == str(settings.results_folder)


def test_call_nnunet_predict_prefers_model_dir_and_checkpoint(tmp_path, monkeypatch):
    # 使用相对模型路径，验证 resolve_all_paths 可以处理
    model_dir = Path("models/nnUNet/3d_fullres/Task001_kits/nnUNetTrainerV2__nnUNetPlansv2.1")
    abs_model_dir = tmp_path / model_dir
    fold_dir = abs_model_dir / "fold_0"
    fold_dir.mkdir(parents=True)
    # 只有 final，测试自动回落
    (fold_dir / "model_final_checkpoint.ckpt").touch()

    settings = build_settings(tmp_path, abs_model_dir)

    # 用隔离的 settings 覆盖 service 的单例
    service = InferenceService()
    monkeypatch.setattr(service, "settings", settings)

    # 创建输入/输出目录
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    calls = {}

    def fake_run(cmd, cwd, env, capture_output, text, timeout):
        calls["cmd"] = cmd
        calls["env"] = env
        class R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return R()

    monkeypatch.setattr("app.services.inference.subprocess.run", fake_run)

    ok = service._call_nnunet_predict(input_dir, output_dir, task_id="demo")

    assert ok is True
    assert "model_final_checkpoint" in " ".join(calls["cmd"])
    # 结果目录取自模型路径的上级（models，已解析为绝对路径）
    assert calls["env"]["RESULTS_FOLDER"] == str(abs_model_dir.parents[3])
