"""
文件下载 API 路由
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import get_settings

router = APIRouter(prefix="/files", tags=["文件"])
settings = get_settings()


@router.get("/{task_id}/{filename}")
async def download_file(task_id: str, filename: str):
    """
    下载文件

    - **task_id**: 任务 ID
    - **filename**: 文件名 (original.nii.gz 或 segmentation.nii.gz)
    """
    # 验证文件名
    allowed_files = ["original.nii.gz", "segmentation.nii.gz"]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 构建文件路径
    file_path = settings.result_dir / task_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/gzip",
    )
