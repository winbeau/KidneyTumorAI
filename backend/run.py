#!/usr/bin/env python
"""
后端启动脚本
"""
import uvicorn
from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1,  # MindSpore GPU 只支持单进程
    )
