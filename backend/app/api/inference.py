"""
推理 API 路由
"""
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.services.inference import inference_service
from app.models.task import TaskStatus
from app.schemas.inference import (
    InferenceStartResponse,
    InferenceStatusResponse,
    InferenceResultResponse,
    StatsInfo,
)

router = APIRouter(prefix="/inference", tags=["推理"])
settings = get_settings()


async def _save_upload_file(file: UploadFile, dest: Path, max_size: int) -> int:
    """逐块写入上传文件，避免一次性读入内存"""
    chunk_size = 8 * 1024 * 1024  # 8MB
    total = 0
    with open(dest, "wb") as f:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制 ({max_size // 1024 // 1024}MB)"
                )
            f.write(chunk)
    await file.seek(0)
    return total


@router.post("/upload", response_model=InferenceStartResponse)
async def upload_file_only(
    file: UploadFile = File(...),
    model: str = Query(default="3d_fullres", description="模型类型"),
):
    """
    仅上传文件并创建任务，不立即启动推理
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    is_valid = any(file.filename.endswith(ext) for ext in settings.allowed_extensions)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，请上传 {settings.allowed_extensions}"
        )

    temp_path = settings.temp_dir / file.filename
    try:
        await _save_upload_file(file, temp_path, settings.max_upload_size)
        task_id = inference_service.create_task(file.filename, temp_path)
        return InferenceStartResponse(
            taskId=task_id,
            status="queued",
            estimatedTime=0,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.post("/{task_id}/start", response_model=InferenceStartResponse)
async def start_inference_task(task_id: str):
    """
    根据已上传的任务 ID 启动推理
    """
    task = inference_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status == TaskStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="任务正在处理中")

    # 重新标记排队状态
    inference_service._update_task_status(task_id, TaskStatus.QUEUED, progress=0, message="排队中...")
    inference_service.start_inference(task_id)
    return InferenceStartResponse(
        taskId=task_id,
        status="queued",
        estimatedTime=120,
    )


@router.post("/start", response_model=InferenceStartResponse)
async def start_inference(
    file: UploadFile = File(...),
    model: str = Query(default="3d_fullres", description="模型类型"),
):
    """
    上传文件并开始推理

    - **file**: NIfTI 格式的 CT 影像文件 (.nii 或 .nii.gz)
    - **model**: 模型类型 (默认 3d_fullres)
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    is_valid = any(file.filename.endswith(ext) for ext in settings.allowed_extensions)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，请上传 {settings.allowed_extensions}"
        )

    # 保存上传文件
    temp_path = settings.temp_dir / file.filename
    try:
        await _save_upload_file(file, temp_path, settings.max_upload_size)

        # 创建任务
        task_id = inference_service.create_task(file.filename, temp_path)

        # 启动异步推理
        inference_service.start_inference(task_id)

        return InferenceStartResponse(
            taskId=task_id,
            status="queued",
            estimatedTime=120,  # 预估2分钟
        )

    finally:
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()


@router.get("/{task_id}/status", response_model=InferenceStatusResponse)
async def get_inference_status(task_id: str):
    """
    查询推理任务状态

    - **task_id**: 任务 ID
    """
    task = inference_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return InferenceStatusResponse(
        taskId=task.id,
        status=task.status.value,
        progress=task.progress,
        message=task.message,
    )


@router.get("/{task_id}/result", response_model=InferenceResultResponse)
async def get_inference_result(task_id: str):
    """
    获取推理结果

    - **task_id**: 任务 ID
    """
    task = inference_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task.status.value}")

    return InferenceResultResponse(
        taskId=task.id,
        originalUrl=f"/files/{task_id}/original.nii.gz",
        segmentationUrl=f"/files/{task_id}/segmentation.nii.gz",
        stats=StatsInfo(
            kidneyVolume=task.kidney_volume,
            tumorVolume=task.tumor_volume,
            processingTime=task.processing_time,
        ),
    )


@router.delete("/{task_id}")
async def cancel_inference(task_id: str):
    """
    取消/删除推理任务

    - **task_id**: 任务 ID
    """
    success = inference_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {"message": "任务已删除"}
