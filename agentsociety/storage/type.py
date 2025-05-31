import enum
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime

__all__ = [
    "StorageSurvey",
    "StorageDialogType",
    "StorageDialog",
    "StorageGlobalPrompt",
    "StorageProfile",
    "StorageStatus",
    "StoragePendingDialog",
]


class StorageExpInfo(BaseModel):
    tenant_id: str
    id: str
    name: str
    num_day: int
    status: int
    cur_day: int
    cur_t: float
    config: str
    error: str
    input_tokens: int
    output_tokens: int
    created_at: datetime
    updated_at: datetime


class StorageSurvey(BaseModel):
    id: int
    day: int
    t: float
    survey_id: str
    result: str
    created_at: datetime


class StorageDialogType(enum.IntEnum):
    """Storage dialog type"""

    Thought = 0  # Dialog in agent self
    Talk = 1  # Dialog with other agents
    User = 2  # Dialog with user


class StorageDialog(BaseModel):
    id: int
    day: int
    t: float
    type: int
    speaker: str
    content: str
    created_at: datetime


class StorageGlobalPrompt(BaseModel):
    day: int
    t: float
    prompt: str
    created_at: datetime


class StorageProfile(BaseModel):
    id: int
    name: str
    profile: str


class StorageStatus(BaseModel):
    id: int
    day: int
    t: float
    lng: Optional[float]
    lat: Optional[float]
    parent_id: Optional[int]
    friend_ids: list[int]
    action: str
    status: str
    created_at: datetime


class StoragePendingDialog(BaseModel):
    """Pending dialog storage type"""

    id: int
    """Pending dialog ID"""
    agent_id: int
    """Agent ID"""
    day: int
    """Day"""
    t: float
    """Time"""
    content: str
    """Content"""
    created_at: datetime
    """Created time"""
    processed: bool
    """Whether the dialog has been processed"""
