import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel

from ..database import Base


# 注意：这些模型在实际使用时会动态创建表，这里只是定义结构
class AgentProfile(BaseModel):
    """代理资料模型"""
    id: uuid.UUID
    name: str
    age: int
    gender: str
    occupation: str
    personality: str
    background: str
    interests: List[str]
    relationships: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class AgentStatus(BaseModel):
    """代理状态模型"""
    id: uuid.UUID
    day: int
    t: float
    location: str
    activity: str
    emotion: str
    energy: float
    hunger: float
    social: float
    hygiene: float
    bladder: float
    fun: float
    extra: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class AgentDialog(BaseModel):
    """代理对话模型"""
    id: uuid.UUID
    day: int
    t: float
    speaker_id: uuid.UUID
    speaker_name: str
    listener_id: uuid.UUID
    listener_name: str
    content: str
    location: str
    extra: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class AgentDialogCreate(BaseModel):
    """创建代理对话请求模型"""
    day: int
    t: float
    speaker_id: uuid.UUID
    speaker_name: str
    listener_id: uuid.UUID
    listener_name: str
    content: str
    location: str
    extra: Dict[str, Any] = {}


class AgentSurvey(BaseModel):
    """代理调查模型"""
    id: uuid.UUID
    survey_id: uuid.UUID
    answers: Dict[str, Any]
    extra: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentSurveyCreate(BaseModel):
    """创建代理调查请求模型"""
    survey_id: uuid.UUID
    answers: Dict[str, Any]
    extra: Dict[str, Any] = {} 