from typing import Any, Awaitable, Callable, List, Optional, Union

from pydantic import BaseModel, Field, field_serializer

from ..environment import MapConfig, SimulatorConfig
from ..llm import LLMConfig
from .agent import AgentClassType, AgentConfig
from .env import EnvConfig
from .exp import (
    EnvironmentConfig,
    ExpConfig,
    MessageInterceptConfig,
    MetricExtractorConfig,
    MetricType,
    WorkflowStepConfig,
    WorkflowType,
)
from .utils import load_config_from_file

__all__ = [
    "EnvConfig",
    "AgentConfig",
    "WorkflowStepConfig",
    "ExpConfig",
    "MetricExtractorConfig",
    "EnvironmentConfig",
    "MessageInterceptConfig",
    "Config",
    "load_config_from_file",
    "AgentClassType",
    "MetricType",
    "WorkflowType",
]


class AgentsConfig(BaseModel):
    """Configuration for different types of agents in the simulation."""

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

    init_funcs: list[Callable[[Any], Union[None, Awaitable[None]]]] = Field([])
    """Initialization functions for simulation, the only one argument is the AgentSociety object"""

    @field_serializer("init_funcs")
    def serialize_init_funcs(self, init_funcs, info):
        return [func.__name__ for func in init_funcs]


class AdvancedConfig(BaseModel):
    """Advanced configuration for the simulation."""

    simulator: SimulatorConfig = Field(
        default_factory=lambda: SimulatorConfig.model_validate({})
    )
    """Simulator configuration"""

    embedding_model: Optional[str] = Field(None)
    """Embedding model name (e.g. BAAI/bge-m3) in Hugging Face, set it None if you want to use the simplest embedding model (TF-IDF)"""

    group_size: int = Field(100)
    """Group size for simulation"""

    logging_level: str = Field("INFO")
    """Logging level"""


class Config(BaseModel):
    """Configuration for the simulation."""

    llm: List[LLMConfig] = Field(..., min_length=1)
    """List of LLM configurations"""

    env: EnvConfig
    """Environment configuration"""

    map: MapConfig
    """Map configuration"""

    agents: AgentsConfig
    """Configuration for different types of agents in the simulation."""

    exp: ExpConfig
    """Experiment configuration"""

    advanced: AdvancedConfig = Field(
        default_factory=lambda: AdvancedConfig.model_validate({})
    )
    """Advanced configuration for the simulation (keep it empty if you don't need it)"""
