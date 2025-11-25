"""
nnU-Net 推理服务
"""
import os
import sys
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor

import nibabel as nib
import numpy as np

from app.core.config import get_settings
from app.core.database import get_sync_session
from app.models.task import InferenceTask, TaskStatus

settings = get_settings()

# 线程池用于异步执行推理
executor = ThreadPoolExecutor(max_workers=2)


class InferenceService:
    """推理服务"""

    def __init__(self):
        self.settings = settings

    def create_task(self, filename: str, file_path: Path) -> str:
        """创建推理任务"""
        task_id = str(uuid.uuid4())

        # 创建任务目录
        task_dir = self.settings.result_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # 复制原始文件
        original_path = task_dir / f"original.nii.gz"
        shutil.copy(file_path, original_path)

        # 创建数据库记录
        with get_sync_session() as session:
            task = InferenceTask(
                id=task_id,
                filename=filename,
                original_path=str(original_path),
                status=TaskStatus.QUEUED,
            )
            session.add(task)

        return task_id

    def start_inference(self, task_id: str):
        """启动异步推理"""
        executor.submit(self._run_inference, task_id)

    def _run_inference(self, task_id: str):
        """执行推理 (在后台线程中运行)"""
        start_time = time.time()

        try:
            # 更新状态为处理中
            self._update_task_status(task_id, TaskStatus.PROCESSING, progress=10, message="正在准备推理...")

            # 获取任务信息
            with get_sync_session() as session:
                task = session.query(InferenceTask).filter_by(id=task_id).first()
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                original_path = Path(task.original_path)

            task_dir = original_path.parent

            # 准备输入目录 (nnU-Net 需要 _0000 后缀)
            input_dir = task_dir / "input"
            input_dir.mkdir(exist_ok=True)
            input_file = input_dir / f"{task_id}_0000.nii.gz"
            shutil.copy(original_path, input_file)

            # 输出目录
            output_dir = task_dir / "output"
            output_dir.mkdir(exist_ok=True)

            self._update_task_status(task_id, TaskStatus.PROCESSING, progress=20, message="正在执行分割推理...")

            # 调用 nnU-Net 推理
            success = self._call_nnunet_predict(input_dir, output_dir, task_id)

            if not success:
                raise RuntimeError("nnU-Net 推理失败")

            self._update_task_status(task_id, TaskStatus.PROCESSING, progress=80, message="正在处理分割结果...")

            # 找到输出文件
            output_files = list(output_dir.glob("*.nii.gz"))
            if not output_files:
                raise RuntimeError("未找到分割结果文件")

            # 重命名并移动到结果目录
            segmentation_path = task_dir / "segmentation.nii.gz"
            shutil.move(str(output_files[0]), str(segmentation_path))

            self._update_task_status(task_id, TaskStatus.PROCESSING, progress=90, message="正在计算体积统计...")

            # 计算统计信息
            kidney_volume, tumor_volume = self._calculate_volumes(segmentation_path, original_path)

            # 处理时间
            processing_time = time.time() - start_time

            # 更新任务完成
            with get_sync_session() as session:
                task = session.query(InferenceTask).filter_by(id=task_id).first()
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.message = "分割完成"
                task.segmentation_path = str(segmentation_path)
                task.kidney_volume = kidney_volume
                task.tumor_volume = tumor_volume
                task.processing_time = processing_time
                task.completed_at = datetime.utcnow()

            # 清理临时文件
            shutil.rmtree(input_dir, ignore_errors=True)
            shutil.rmtree(output_dir, ignore_errors=True)

        except Exception as e:
            print(f"Inference error: {e}")
            self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                progress=0,
                message=f"推理失败: {str(e)}"
            )

    def _call_nnunet_predict(self, input_dir: Path, output_dir: Path, task_id: str) -> bool:
        """调用 nnU-Net 预测脚本"""
        try:
            # 构建命令
            cmd = [
                sys.executable,
                str(self.settings.nnunet_root / "eval.py"),
                "-i", str(input_dir),
                "-o", str(output_dir),
                "-t", self.settings.task_name,
                "-m", self.settings.default_model,
                "-tr", self.settings.trainer_class,
                "-p", self.settings.plans_identifier,
                "-f", str(self.settings.default_fold),
                "-chk", "model_best",
                "--disable_tta",  # 禁用测试时增强以加快速度
            ]

            # 设置环境变量
            env = os.environ.copy()
            env["nnUNet_raw_data_base"] = self.settings.nnunet_raw_data_base
            env["nnUNet_preprocessed"] = self.settings.nnunet_preprocessed
            env["RESULTS_FOLDER"] = self.settings.results_folder

            print(f"Running inference command: {' '.join(cmd)}")

            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=str(self.settings.nnunet_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
            )

            if result.returncode != 0:
                print(f"nnU-Net stderr: {result.stderr}")
                return False

            print(f"nnU-Net stdout: {result.stdout}")
            return True

        except subprocess.TimeoutExpired:
            print("nnU-Net inference timeout")
            return False
        except Exception as e:
            print(f"nnU-Net call error: {e}")
            return False

    def _calculate_volumes(self, seg_path: Path, orig_path: Path) -> Tuple[float, float]:
        """计算肾脏和肿瘤体积 (mm³)"""
        try:
            # 加载分割结果
            seg_nii = nib.load(str(seg_path))
            seg_data = seg_nii.get_fdata()

            # 获取体素尺寸
            voxel_dims = seg_nii.header.get_zooms()[:3]
            voxel_volume = float(np.prod(voxel_dims))  # mm³

            # 计算体积
            # 标签 1: 肾脏, 标签 2: 肿瘤
            kidney_voxels = np.sum(seg_data == 1)
            tumor_voxels = np.sum(seg_data == 2)

            kidney_volume = float(kidney_voxels * voxel_volume)
            tumor_volume = float(tumor_voxels * voxel_volume)

            return kidney_volume, tumor_volume

        except Exception as e:
            print(f"Volume calculation error: {e}")
            return 0.0, 0.0

    def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int = 0,
        message: str = None
    ):
        """更新任务状态"""
        with get_sync_session() as session:
            task = session.query(InferenceTask).filter_by(id=task_id).first()
            if task:
                task.status = status
                task.progress = progress
                task.message = message

    def get_task(self, task_id: str) -> Optional[InferenceTask]:
        """获取任务信息"""
        with get_sync_session() as session:
            task = session.query(InferenceTask).filter_by(id=task_id).first()
            if task:
                # Detach from session
                session.expunge(task)
            return task

    def get_task_list(self, page: int = 1, page_size: int = 20) -> Tuple[list, int]:
        """获取任务列表"""
        with get_sync_session() as session:
            total = session.query(InferenceTask).count()
            tasks = (
                session.query(InferenceTask)
                .order_by(InferenceTask.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            # Detach from session
            for task in tasks:
                session.expunge(task)
            return tasks, total

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with get_sync_session() as session:
            task = session.query(InferenceTask).filter_by(id=task_id).first()
            if not task:
                return False

            # 删除文件
            task_dir = self.settings.result_dir / task_id
            if task_dir.exists():
                shutil.rmtree(task_dir, ignore_errors=True)

            # 删除数据库记录
            session.delete(task)
            return True


# 单例
inference_service = InferenceService()
