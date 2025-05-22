import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AwareDatetime, BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column

from ._base import TABLE_PREFIX, Base

__all__ = [
    "AgentProfile",
    "AgentProfileData",
    "ApiDistribution",
    "ApiMemoryDistribution",
    "ApiAgentProfile",
    "ApiAgentProfileData",
]


class AgentProfile(Base):
    """Agent profile model for storing distribution templates"""

    __tablename__ = f"{TABLE_PREFIX}agent_profile"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    agent_type: Mapped[str] = mapped_column()
    distributions: Mapped[Any] = mapped_column()  # JSONB field
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class AgentProfileData(Base):
    """Agent profile data model for storing metadata about agent data files"""

    __tablename__ = f"{TABLE_PREFIX}agent_profile_data"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    agent_type: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column()  # Path to the S3 file
    record_count: Mapped[int] = mapped_column()  # Number of records in the file
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class ApiDistribution(BaseModel):
    """Distribution model for API"""

    type: str = Field(
        ...,
        description="Distribution type (choice, uniform_int, uniform_float, normal, constant)",
    )
    params: Dict[str, Any] = Field(..., description="Distribution parameters")


class ApiMemoryDistribution(BaseModel):
    """Memory distribution model for API"""

    name: str = Field(..., description="Attribute name")
    distribution: ApiDistribution = Field(..., description="Distribution configuration")


class ApiAgentProfile(BaseModel):
    """Agent profile model for API"""

    tenant_id: Optional[str] = None
    id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    agent_type: str
    distributions: List[ApiMemoryDistribution]
    created_at: Optional[AwareDatetime] = None
    updated_at: Optional[AwareDatetime] = None

    class Config:
        from_attributes = True


class ApiAgentProfileData(BaseModel):
    """Agent profile data model for API"""

    tenant_id: Optional[str] = None
    id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    agent_type: str
    file_path: str
    record_count: int
    created_at: Optional[AwareDatetime] = None
    updated_at: Optional[AwareDatetime] = None

    class Config:
        from_attributes = True
