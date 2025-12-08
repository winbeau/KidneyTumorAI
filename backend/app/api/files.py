"""
文件下载 API 路由
"""
import hashlib
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response

import nibabel as nib
import numpy as np
from scipy import ndimage
import gzip
import io

from app.core.config import get_settings

router = APIRouter(prefix="/files", tags=["文件"])
settings = get_settings()

# 预览文件缓存目录
PREVIEW_CACHE_DIR = settings.temp_dir / "preview_cache"
PREVIEW_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def downsample_nifti(input_path: Path, factor: int = 4) -> bytes:
    """
    降采样 NIfTI 文件

    Args:
        input_path: 输入文件路径
        factor: 降采样因子 (2, 4, 8)

    Returns:
        压缩后的 NIfTI 字节数据
    """
    # 加载原始数据
    nii = nib.load(str(input_path))
    data = nii.get_fdata()
    affine = nii.affine.copy()
    header = nii.header.copy()

    # 降采样数据
    if data.ndim == 3:
        # 使用 zoom 进行降采样
        zoom_factors = [1.0 / factor] * 3
        if "segmentation" in str(input_path):
            # 分割图使用最近邻插值保持标签完整性
            downsampled = ndimage.zoom(data, zoom_factors, order=0)
        else:
            # CT 图像使用线性插值
            downsampled = ndimage.zoom(data, zoom_factors, order=1)
    else:
        downsampled = data

    # 更新 affine 矩阵以反映新的体素大小
    scale_matrix = np.diag([factor, factor, factor, 1])
    new_affine = affine @ scale_matrix

    # 更新 header
    new_header = header.copy()
    new_header.set_data_shape(downsampled.shape)
    zooms = header.get_zooms()
    new_header.set_zooms([z * factor for z in zooms[:3]])

    # 创建新的 NIfTI 对象
    new_nii = nib.Nifti1Image(downsampled.astype(np.float32), new_affine, new_header)

    # 保存到内存并压缩
    buffer = io.BytesIO()
    nib.save(new_nii, buffer)
    buffer.seek(0)

    # gzip 压缩
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode='wb', compresslevel=6) as gz:
        gz.write(buffer.read())

    return compressed.getvalue()


def get_preview_cache_path(task_id: str, filename: str, factor: int) -> Path:
    """获取预览缓存文件路径"""
    cache_key = hashlib.md5(f"{task_id}_{filename}_{factor}".encode()).hexdigest()
    return PREVIEW_CACHE_DIR / f"{cache_key}.nii.gz"


@router.get("/{task_id}/{filename}")
async def download_file(
    task_id: str,
    filename: str,
    preview: bool = Query(False, description="是否获取预览版本（降采样）"),
    factor: int = Query(4, description="降采样因子", ge=2, le=8),
):
    """
    下载文件

    - **task_id**: 任务 ID
    - **filename**: 文件名 (original.nii.gz 或 segmentation.nii.gz)
    - **preview**: 是否获取预览版本（低分辨率，加载更快）
    - **factor**: 降采样因子 (2-8)，仅在 preview=true 时有效
    """
    # 验证文件名
    allowed_files = ["original.nii.gz", "segmentation.nii.gz"]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 构建文件路径
    file_path = settings.result_dir / task_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    # 如果请求预览版本
    if preview:
        cache_path = get_preview_cache_path(task_id, filename, factor)

        # 检查缓存
        if not cache_path.exists():
            try:
                # 生成降采样版本
                preview_data = downsample_nifti(file_path, factor)
                # 保存到缓存
                cache_path.write_bytes(preview_data)
            except Exception as e:
                print(f"降采样失败: {e}")
                # 降采样失败时返回原始文件
                return FileResponse(
                    path=str(file_path),
                    filename=filename,
                    media_type="application/gzip",
                    headers={
                        "Cache-Control": "public, max-age=86400, immutable",
                        "X-Preview": "false",
                    },
                )

        return FileResponse(
            path=str(cache_path),
            filename=f"preview_{filename}",
            media_type="application/gzip",
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
                "X-Preview": "true",
                "X-Preview-Factor": str(factor),
            },
        )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/gzip",
        headers={
            "Cache-Control": "public, max-age=86400, immutable",
            "X-Preview": "false",
        },
    )
