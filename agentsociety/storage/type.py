from pydantic import BaseModel

__all__ = ["Survey", "Dialog"]


class Survey(BaseModel):
    id: int
    day: int
    t: float
    survey_id: str
    result: str
    created_at: int


class Dialog(BaseModel):
    id: int
    day: int
    t: float
    type: int
    speaker: str
    content: str
    created_at: int
