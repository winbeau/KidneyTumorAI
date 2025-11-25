"""
Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InferenceStartResponse(BaseModel):
    """推理启动响应"""
    taskId: str
    status: str
    estimatedTime: int


class InferenceStatusResponse(BaseModel):
    """推理状态响应"""
    taskId: str
    status: str
    progress: int
    message: Optional[str] = None


class StatsInfo(BaseModel):
    """统计信息"""
    kidneyVolume: Optional[float] = None
    tumorVolume: Optional[float] = None
    processingTime: Optional[float] = None


class InferenceResultResponse(BaseModel):
    """推理结果响应"""
    taskId: str
    originalUrl: str
    segmentationUrl: str
    stats: StatsInfo


class HistoryRecord(BaseModel):
    """历史记录"""
    id: str
    filename: str
    uploadTime: str
    status: str
    stats: Optional[StatsInfo] = None
    originalUrl: str
    segmentationUrl: Optional[str] = None


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    total: int
    records: list[HistoryRecord]
