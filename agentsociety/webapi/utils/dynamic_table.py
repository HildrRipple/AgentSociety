import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, MetaData, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from ..database import engine


def create_dynamic_table(table_name, columns):
    """
    动态创建表
    
    Args:
        table_name: 表名
        columns: 列定义字典，格式为 {列名: 列类型}
    
    Returns:
        创建的表对象
    """
    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        *columns
    )
    metadata.create_all(engine)
    return table


def get_dynamic_table_model(table_name, base_class=None):
    """
    获取动态表的模型类
    
    Args:
        table_name: 表名
        base_class: 基础类，如果为None则创建新的
    
    Returns:
        表对应的模型类
    """
    if base_class is None:
        base_class = declarative_base()
    
    # 创建动态模型类
    class DynamicModel(base_class):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
    
    return DynamicModel


# 预定义的列类型
def agent_profile_columns():
    """获取代理资料表的列定义"""
    return [
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('name', String, nullable=False),
        Column('age', Integer, nullable=False),
        Column('gender', String, nullable=False),
        Column('occupation', String, nullable=False),
        Column('personality', String, nullable=False),
        Column('background', Text, nullable=False),
        Column('interests', JSONB, nullable=False),
        Column('relationships', JSONB, nullable=True),
        Column('extra', JSONB, nullable=True)
    ]


def agent_status_columns():
    """获取代理状态表的列定义"""
    return [
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('day', Integer, nullable=False),
        Column('t', Float, nullable=False),
        Column('location', String, nullable=False),
        Column('activity', String, nullable=False),
        Column('emotion', String, nullable=False),
        Column('energy', Float, nullable=False),
        Column('hunger', Float, nullable=False),
        Column('social', Float, nullable=False),
        Column('hygiene', Float, nullable=False),
        Column('bladder', Float, nullable=False),
        Column('fun', Float, nullable=False),
        Column('extra', JSONB, nullable=True)
    ]


def agent_dialog_columns():
    """获取代理对话表的列定义"""
    return [
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('day', Integer, nullable=False),
        Column('t', Float, nullable=False),
        Column('speaker_id', UUID(as_uuid=True), nullable=False),
        Column('speaker_name', String, nullable=False),
        Column('listener_id', UUID(as_uuid=True), nullable=False),
        Column('listener_name', String, nullable=False),
        Column('content', Text, nullable=False),
        Column('location', String, nullable=False),
        Column('extra', JSONB, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow)
    ]


def agent_survey_columns():
    """获取代理调查表的列定义"""
    return [
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('survey_id', UUID(as_uuid=True), nullable=False),
        Column('answers', JSONB, nullable=False),
        Column('extra', JSONB, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow)
    ] 