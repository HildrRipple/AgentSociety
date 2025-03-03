from fastapi import APIRouter, Depends
from typing import Any, Callable, Dict, List, TypeVar, Generic, Optional, Type, Union
from pydantic import BaseModel

from ..models import ApiResponse

from .experiment import router as experiment_router
from .agent_profile import router as agent_profile_router
from .agent_status import router as agent_status_router
from .agent_dialog import router as agent_dialog_router
from .agent_survey import router as agent_survey_router
from .survey import router as survey_router
from .mlflow import router as mlflow_router

# 定义泛型类型变量
T = TypeVar('T')

# 创建主路由
api_router = APIRouter(prefix="/api")

# 包含各个子路由
api_router.include_router(experiment_router)
api_router.include_router(agent_profile_router)
api_router.include_router(agent_status_router)
api_router.include_router(agent_dialog_router)
api_router.include_router(agent_survey_router)
api_router.include_router(survey_router)
api_router.include_router(mlflow_router) 