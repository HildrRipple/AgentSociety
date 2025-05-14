import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base, TABLE_PREFIX

__all__ = ["AgentTemplateDB", "TemplateBlock", "ApiAgentTemplate"]

class DistributionType(str, Enum):
    CHOICE = "choice"
    UNIFORM_INT = "uniform_int"
    NORMAL = "normal"

class ChoiceDistribution(BaseModel):
    type: DistributionType = DistributionType.CHOICE
    params: Dict[str, Union[List[str], List[float]]] = Field(
        ...,
        description="Choice distribution parameters including choices and weights"
    )

class UniformIntDistribution(BaseModel):
    type: DistributionType = DistributionType.UNIFORM_INT
    params: Dict[str, int] = Field(
        ...,
        description="Uniform distribution parameters including min_value and max_value"
    )

class NormalDistribution(BaseModel):
    type: DistributionType = DistributionType.NORMAL
    params: Dict[str, float] = Field(
        ...,
        description="Normal distribution parameters including mean and std"
    )

class ChoiceDistributionConfig(BaseModel):
    type: DistributionType = DistributionType.CHOICE
    choices: List[str]
    weights: List[float]

class UniformIntDistributionConfig(BaseModel):
    type: DistributionType = DistributionType.UNIFORM_INT
    min_value: int
    max_value: int

class NormalDistributionConfig(BaseModel):
    type: DistributionType = DistributionType.NORMAL
    mean: float
    std: float

Distribution = Union[ChoiceDistribution, UniformIntDistribution, NormalDistribution]
DistributionConfig = Union[ChoiceDistributionConfig, UniformIntDistributionConfig, NormalDistributionConfig]

class AgentTemplateDB(Base):
    """Agent template database model"""
    __tablename__ = f"{TABLE_PREFIX}agent_template"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    profile: Mapped[Dict] = mapped_column(type_=JSONB)  # 使用 JSONB 类型
    base: Mapped[Dict] = mapped_column(type_=JSONB)
    states: Mapped[Dict] = mapped_column(type_=JSONB)
    agent_params: Mapped[Dict] = mapped_column(type_=JSONB)
    blocks: Mapped[List] = mapped_column(type_=JSONB)  # 修改为 JSONB
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

class AgentParams(BaseModel):
    """Agent parameters model"""
    enable_cognition: bool = Field(default=True)
    UBI: float = Field(default=0.0)
    num_labor_hours: float = Field(default=8.0)
    productivity_per_labor: float = Field(default=1.0)
    time_diff: float = Field(default=1.0)
    max_plan_steps: int = Field(default=5)
    need_initialization_prompt: Optional[str] = None
    need_evaluation_prompt: Optional[str] = None
    need_reflection_prompt: Optional[str] = None
    plan_generation_prompt: Optional[str] = None

class TemplateBlock(BaseModel):
    """Template block model"""
    id: str
    name: str
    type: str
    description: str
    dependencies: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)

class BaseConfig(BaseModel):
    """Base configuration model"""
    home: Dict[str, Any] = Field(default_factory=lambda: {"aoi_position": {"aoi_id": 0}})
    work: Dict[str, Any] = Field(default_factory=lambda: {"aoi_position": {"aoi_id": 0}})

class StatesConfig(BaseModel):
    """States configuration model"""
    needs: str = "str"
    plan: str = "dict"
    selfDefine: Optional[str] = None

class ApiAgentTemplate(BaseModel):
    """Agent template model for API"""
    tenant_id: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    profile: Dict[str, Union[Distribution, DistributionConfig]] = Field(
        ..., 
        description="Profile configuration with distributions"
    )
    base: BaseConfig = Field(default_factory=BaseConfig)
    states: StatesConfig = Field(default_factory=StatesConfig)
    agent_params: AgentParams = Field(default_factory=AgentParams)
    blocks: List[TemplateBlock] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Example Template",
                "description": "A template example",
                "profile": {
                    "fields": {
                        "name": "string",
                        "age": "number",
                        "occupation": "string"
                    }
                },
                "base": {
                    "fields": {
                        "home": {
                            "aoi_position": {
                                "aoi_id": "string"
                            }
                        }
                    }
                },
                "states": {
                    "fields": {
                        "health": "number",
                        "happiness": "number"
                    }
                },
                "agent_params": {
                    "enable_cognition": True,
                    "UBI": 1000,
                    "num_labor_hours": 8,
                    "productivity_per_labor": 1.0,
                    "time_diff": 1.0,
                    "max_plan_steps": 5
                },
                "blocks": [
                    {
                        "id": "block1",
                        "name": "Mobility Block",
                        "type": "mobilityblock",
                        "description": "Handles agent movement",
                        "params": {
                            "search_limit": 50
                        }
                    }
                ]
            }
        } 