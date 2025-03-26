from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from .agent import AgentConfig, DistributionConfig
from .const import AgentClassType
from .env import (
    AvroConfig,
    EnvConfig,
    LLMConfig,
    MapConfig,
    MlflowConfig,
    PostgreSQLConfig,
    RedisConfig,
    SimulatorConfig,
)
from .exp import (
    EnvironmentConfig,
    ExpConfig,
    MessageInterceptConfig,
    MetricExtractorConfig,
    WorkflowStepConfig,
)
from .utils import load_config_from_file

__all__ = [
    "LLMConfig",
    "RedisConfig",
    "PostgreSQLConfig",
    "AvroConfig",
    "MlflowConfig",
    "SimulatorConfig",
    "MapConfig",
    "EnvConfig",
    "AgentConfig",
    "DistributionConfig",
    "WorkflowStepConfig",
    "ExpConfig",
    "MetricExtractorConfig",
    "EnvironmentConfig",
    "MessageInterceptConfig",
    "Config",
    "load_config_from_file",
]


class Config(BaseModel):
    """Configuration for the simulation."""

    env: EnvConfig
    """Environment configuration"""

    citizens: list[AgentConfig] = Field(..., min_length=1)
    """Citizen Agent configuration"""

    firms: list[AgentConfig] = Field(
        [
            AgentConfig(
                agent_class=AgentClassType.FIRM,
                number=1,
            ),
        ],
        min_length=1,
    )
    """Firm Agent configuration"""

    banks: list[AgentConfig] = Field(
        [
            AgentConfig(
                agent_class=AgentClassType.BANK,
                number=1,
            ),
        ],
        min_length=1,
    )
    """Bank Agent configuration"""

    nbs: list[AgentConfig] = Field(
        [
            AgentConfig(
                agent_class=AgentClassType.NBS,
                number=1,
            ),
        ],
        min_length=1,
    )
    """NBS Agent configuration"""

    governments: list[AgentConfig] = Field(
        [
            AgentConfig(
                agent_class=AgentClassType.GOVERNMENT,
                number=1,
            ),
        ],
        min_length=1,
    )
    """Government Agent configuration"""

    exp: ExpConfig
    """Experiment configuration"""

    embedding_model: Optional[str] = Field("BAAI/bge-m3")
    """Embedding model name in Hugging Face, set it None if you want to use the simplest embedding model (TF-IDF)"""

    init_funcs: list[Callable[[Any], None]] = Field([])
    """Initialization functions for simulation, the only one argument is the AgentSociety object"""

    group_size: int = Field(100)
    """Group size for simulation"""

    logging_level: str = Field("INFO")
    """Logging level"""
