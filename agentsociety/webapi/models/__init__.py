from .experiment import Experiment, ExperimentStatus
from .agent import AgentProfile, AgentStatus, AgentDialog, AgentSurvey
from .survey import Survey, SurveyQuestion
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

__all__ = [
    'Experiment', 'ExperimentStatus',
    'AgentProfile', 'AgentStatus', 'AgentDialog', 'AgentSurvey',
    'Survey', 'SurveyQuestion'
]

# 定义泛型类型变量
T = TypeVar('T')

# 通用API响应模型
class ApiResponse(GenericModel, Generic[T]):
    """通用API响应模型，与原Go后端保持一致"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

# 分页响应模型
class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[T] = Field(..., description="数据项列表") 