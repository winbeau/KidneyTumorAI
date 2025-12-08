"""
KidneyTumorAI 后端主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api import inference, history, files

settings = get_settings()

# 创建应用
app = FastAPI(
    title="KidneyTumorAI API",
    description="肾脏肿瘤 AI 分割系统后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# GZip 压缩中间件 - 对 JSON 响应等非压缩内容有效
# 注意: .nii.gz 文件已经压缩，不会重复压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Preview", "X-Preview-Factor"],  # 暴露自定义响应头
)


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    print(f"Model path: {settings.model_path}")
    print(f"Upload dir: {settings.upload_dir}")
    print(f"Result dir: {settings.result_dir}")


# 注册路由
app.include_router(inference.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(files.router)  # 文件路由不加 api/v1 前缀

# 兼容部分反向代理剥掉 /api 前缀的场景，提供 /v1* 备用入口
app.include_router(inference.router, prefix="/v1")
app.include_router(history.router, prefix="/v1")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "KidneyTumorAI Backend",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "KidneyTumorAI API",
        "docs": "/docs",
        "health": "/health",
    }
