from fastapi import APIRouter

from ..config import settings

router = APIRouter(tags=["mlflow"])


@router.get("/mlflow/url")
def get_mlflow_base_url():
    """获取MLFlow基础URL"""
    return {"data": settings.MLFLOW_URL} 