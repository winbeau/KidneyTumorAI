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
        with open(temp_path, "wb") as f:
            content = await file.read()
            if len(content) > settings.max_upload_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制 ({settings.max_upload_size // 1024 // 1024}MB)"
                )
            f.write(content)

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
