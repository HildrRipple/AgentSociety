import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base, TABLE_PREFIX

__all__ = ["AgentTemplateDB", "TemplateBlock", "ApiAgentTemplate"]

class AgentTemplateDB(Base):
    """Agent template database model"""
    __tablename__ = f"{TABLE_PREFIX}agent_template"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    profile: Mapped[Any] = mapped_column()  # JSONB field for profile configuration
    base: Mapped[Any] = mapped_column()  # JSONB field for base configuration
    states: Mapped[Any] = mapped_column()  # JSONB field for states configuration
    agent_params: Mapped[Any] = mapped_column()  # JSONB field for agent parameters
    blocks: Mapped[Any] = mapped_column()  # JSONB field for blocks
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

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
    """Template block model for API"""
    id: str
    name: str
    type: str
    description: str
    dependencies: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ProfileConfig(BaseModel):
    """Profile configuration model"""
    fields: Dict[str, str]

class BaseConfig(BaseModel):
    """Base configuration model"""
    fields: Dict[str, Any]

class StatesConfig(BaseModel):
    """States configuration model"""
    fields: Dict[str, str]
    selfDefine: Optional[str] = None

class ApiAgentTemplate(BaseModel):
    """Agent template model for API"""
    tenant_id: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    profile: ProfileConfig = Field(
        default_factory=lambda: ProfileConfig(fields={}),
        description="Profile configuration"
    )
    base: BaseConfig = Field(
        default_factory=lambda: BaseConfig(fields={}),
        description="Base configuration"
    )
    states: StatesConfig = Field(
        default_factory=lambda: StatesConfig(fields={}),
        description="States configuration"
    )
    agent_params: AgentParams = Field(
        default_factory=AgentParams,
        description="Agent parameters"
    )
    blocks: List[TemplateBlock] = Field(
        default_factory=list,
        description="List of template blocks"
    )
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

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