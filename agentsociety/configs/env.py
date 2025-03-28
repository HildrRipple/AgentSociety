from typing import List, Optional

from pydantic import BaseModel, Field

from ..llm import LLMConfig
from ..message import RedisConfig
from ..storage import PostgreSQLConfig, AvroConfig
from ..metrics import MlflowConfig
from ..environment import SimulatorConfig, MapConfig

__all__ = [
    "LLMConfig",
    "RedisConfig",
    "PostgreSQLConfig",
    "AvroConfig",
    "MlflowConfig",
    "SimulatorConfig",
    "MapConfig",
    "EnvConfig",
]


class EnvConfig(BaseModel):
    """Environment configuration class."""

    llm: List[LLMConfig] = Field(..., min_length=1)
    """List of LLM configurations"""

    simulator: SimulatorConfig = Field(
        default_factory=lambda: SimulatorConfig.model_validate({})
    )
    """Simulator configuration"""

    redis: RedisConfig
    """Redis configuration"""

    pgsql: PostgreSQLConfig
    """PostgreSQL configuration"""

    avro: AvroConfig
    """Avro configuration"""

    mlflow: MlflowConfig
    """MLflow configuration"""

    map: MapConfig
    """Map configuration"""
