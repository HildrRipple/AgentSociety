import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .api import api_router
from .config import settings
from .database.mqtt import init_mqtt_client
from .database import Base, engine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="SocialCity API",
    description="SocialCity Web API for Agent Society",
    version="0.1.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加响应中间件，统一处理API响应格式
@app.middleware("http")
async def add_response_wrapper(request: Request, call_next: Callable) -> Response:
    """统一API响应格式的中间件"""
    # 只处理API路由
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    
    # 调用下一个中间件或路由处理函数
    response = await call_next(request)
    
    # 如果是JSONResponse，且状态码为200
    if isinstance(response, JSONResponse) and response.status_code == 200:
        try:
            # 解析响应体
            body = json.loads(response.body)
            
            # 检查是否已经是包装过的响应
            if isinstance(body, dict) and "code" in body and "message" in body and "data" in body:
                # 已经是包装过的响应，不需要再包装
                return response
            
            # 包装响应
            wrapped_body = {
                "code": 200,
                "message": "success",
                "data": body
            }
            
            # 创建新的响应
            return JSONResponse(
                content=wrapped_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception as e:
            logger.error(f"Error wrapping response: {e}")
            # 出错时也尝试包装原始响应
            try:
                return JSONResponse(
                    content={
                        "code": 200,
                        "message": "success",
                        "data": json.loads(response.body)
                    },
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            except:
                pass
    
    # 其他情况直接返回原始响应
    return response

# 包含API路由
app.include_router(api_router)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的事件"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 初始化MQTT客户端
    if settings.MQTT_BROKER:
        init_mqtt_client()
    
    logger.info("Application started")


# 前端静态文件服务
# 首先尝试查找项目根目录下的frontend/dist
project_root = Path(__file__).parent.parent.parent.parent  # 从webapi目录向上4级到项目根目录
frontend_path = project_root / "frontend" / "dist"

# 如果不存在，尝试查找包内的frontend/dist
if not frontend_path.exists():
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"

logger.info(f"Looking for frontend at: {frontend_path}")

if frontend_path.exists():
    logger.info(f"Serving frontend from: {frontend_path}")
    # 挂载静态资源目录
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        # API路由由FastAPI处理
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        # 其他路由返回前端入口文件
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        else:
            logger.error(f"Frontend index.html not found at {index_file}")
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    logger.warning(f"Frontend directory not found at {frontend_path}")


# 直接运行时的入口
if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("HOST", settings.HOST)
    port = int(os.getenv("PORT", settings.PORT))
    
    # 启动服务器
    uvicorn.run(
        "agentsociety.webapi.main:app",
        host=host,
        port=port,
        reload=True,
    ) 