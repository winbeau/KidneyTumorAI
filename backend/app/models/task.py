"""
数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    """任务状态"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InferenceTask(Base):
    """推理任务表"""
    __tablename__ = "inference_tasks"

    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    original_path = Column(String(512), nullable=False)
    segmentation_path = Column(String(512), nullable=True)

    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    progress = Column(Integer, default=0)
    message = Column(Text, nullable=True)

    # 统计信息
    kidney_volume = Column(Float, nullable=True)  # mm³
    tumor_volume = Column(Float, nullable=True)   # mm³
    processing_time = Column(Float, nullable=True)  # seconds

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "stats": {
                "kidneyVolume": self.kidney_volume,
                "tumorVolume": self.tumor_volume,
                "processingTime": self.processing_time,
            } if self.kidney_volume is not None else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
        }
