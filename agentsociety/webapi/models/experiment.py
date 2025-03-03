import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
from typing import Optional

from ..database import Base
from ..config import settings


class ExperimentStatus(enum.IntEnum):
    """实验状态枚举"""
    NOT_STARTED = 0  # 未开始
    RUNNING = 1      # 运行中
    FINISHED = 2     # 运行结束
    ERROR = 3        # 错误中断


class Experiment(Base):
    """实验数据库模型"""
    __tablename__ = f"{settings.TABLE_PREFIX}experiment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    num_day = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=ExperimentStatus.NOT_STARTED)
    cur_day = Column(Integer, nullable=False, default=0)
    cur_t = Column(Float, nullable=False, default=0.0)
    config = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_agent_profile_table_name(self):
        """获取代理资料表名"""
        return f"{settings.TABLE_PREFIX}{str(self.id).replace('-', '_')}_agent_profile"
    
    def get_agent_status_table_name(self):
        """获取代理状态表名"""
        return f"{settings.TABLE_PREFIX}{str(self.id).replace('-', '_')}_agent_status"
    
    def get_agent_dialog_table_name(self):
        """获取代理对话表名"""
        return f"{settings.TABLE_PREFIX}{str(self.id).replace('-', '_')}_agent_dialog"
    
    def get_agent_survey_table_name(self):
        """获取代理调查表名"""
        return f"{settings.TABLE_PREFIX}{str(self.id).replace('-', '_')}_agent_survey"


# Pydantic模型用于API请求和响应
class ExperimentBase(BaseModel):
    """实验基础模型"""
    name: str
    num_day: int
    config: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    """创建实验请求模型"""
    pass


class ExperimentResponse(ExperimentBase):
    """实验响应模型"""
    id: uuid.UUID
    status: int
    cur_day: int
    cur_t: float
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TimeModel(BaseModel):
    """时间模型"""
    day: int
    t: float 