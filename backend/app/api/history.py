"""
历史记录 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.inference import inference_service
from app.schemas.inference import HistoryListResponse, HistoryRecord, StatsInfo

router = APIRouter(prefix="/history", tags=["历史记录"])


class BatchDeleteRequest(BaseModel):
    ids: list[str]


@router.get("", response_model=HistoryListResponse)
async def get_history_list(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    """
    获取历史记录列表

    - **page**: 页码 (从1开始)
    - **pageSize**: 每页数量
    """
    tasks, total = inference_service.get_task_list(page, pageSize)

    records = []
    for task in tasks:
        records.append(HistoryRecord(
            id=task.id,
            filename=task.filename,
            uploadTime=task.created_at.isoformat() if task.created_at else "",
            status=task.status.value,
            stats=StatsInfo(
                kidneyVolume=task.kidney_volume,
                tumorVolume=task.tumor_volume,
                processingTime=task.processing_time,
            ) if task.kidney_volume is not None else None,
            originalUrl=f"/files/{task.id}/original.nii.gz",
            segmentationUrl=f"/files/{task.id}/segmentation.nii.gz" if task.segmentation_path else None,
        ))

    return HistoryListResponse(total=total, records=records)


@router.get("/{record_id}", response_model=HistoryRecord)
async def get_history_record(record_id: str):
    """
    获取单条历史记录

    - **record_id**: 记录 ID
    """
    task = inference_service.get_task(record_id)
    if not task:
        raise HTTPException(status_code=404, detail="记录不存在")

    return HistoryRecord(
        id=task.id,
        filename=task.filename,
        uploadTime=task.created_at.isoformat() if task.created_at else "",
        status=task.status.value,
        stats=StatsInfo(
            kidneyVolume=task.kidney_volume,
            tumorVolume=task.tumor_volume,
            processingTime=task.processing_time,
        ) if task.kidney_volume is not None else None,
        originalUrl=f"/files/{task.id}/original.nii.gz",
        segmentationUrl=f"/files/{task.id}/segmentation.nii.gz" if task.segmentation_path else None,
    )


@router.delete("/{record_id}")
async def delete_history_record(record_id: str):
    """
    删除历史记录

    - **record_id**: 记录 ID
    """
    success = inference_service.delete_task(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")

    return {"message": "记录已删除"}


@router.post("/batch-delete")
async def batch_delete_history(request: BatchDeleteRequest):
    """
    批量删除历史记录

    - **ids**: 要删除的记录 ID 列表
    """
    deleted = 0
    for record_id in request.ids:
        if inference_service.delete_task(record_id):
            deleted += 1

    return {"message": f"已删除 {deleted} 条记录"}
