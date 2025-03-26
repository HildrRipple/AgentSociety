from typing import Any, Optional
from pydantic import BaseModel

__all__ = [
    "StorageSurvey",
    "StorageDialog",
    "StorageGlobalPrompt",
    "StorageProfile",
    "StorageStatus",
]


class StorageSurvey(BaseModel):
    id: int
    day: int
    t: float
    survey_id: str
    result: str
    created_at: int


class StorageDialog(BaseModel):
    id: int
    day: int
    t: float
    type: int
    speaker: str
    content: str
    created_at: int


class StorageGlobalPrompt(BaseModel):
    day: int
    t: float
    prompt: str
    created_at: int


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
    created_at: int
