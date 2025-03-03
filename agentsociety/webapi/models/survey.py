import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel

from ..database import Base
from ..config import settings


class Survey(Base):
    """调查数据库模型"""
    __tablename__ = f"{settings.TABLE_PREFIX}survey"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SurveyQuestion(BaseModel):
    """调查问题模型"""
    id: str
    type: str  # text, choice, multiple_choice, etc.
    question: str
    options: Optional[List[str]] = None
    required: bool = True


class SurveyBase(BaseModel):
    """调查基础模型"""
    title: str
    description: Optional[str] = None
    questions: List[SurveyQuestion]


class SurveyCreate(SurveyBase):
    """创建调查请求模型"""
    pass


class SurveyUpdate(SurveyBase):
    """更新调查请求模型"""
    pass


class SurveyResponse(SurveyBase):
    """调查响应模型"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 