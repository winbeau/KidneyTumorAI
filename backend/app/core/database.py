"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import contextmanager

from app.core.config import get_settings
from app.models.task import Base

settings = get_settings()

# 同步引擎 (用于初始化)
sync_engine = create_engine(
    settings.database_url.replace("sqlite:///", "sqlite:///"),
    echo=settings.debug,
)

# 异步引擎
async_engine = create_async_engine(
    settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=settings.debug,
)

# Session 工厂
SyncSessionLocal = sessionmaker(bind=sync_engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=sync_engine)


@contextmanager
def get_sync_session():
    """获取同步 Session"""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_async_session():
    """获取异步 Session (用于依赖注入)"""
    async with AsyncSessionLocal() as session:
        yield session
